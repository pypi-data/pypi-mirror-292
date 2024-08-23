import logging
import string
import uuid
from textwrap import dedent, indent
from typing import Any

import markdown
import matplotlib.figure as mplfig
import mpld3
from fastapi import Request
from jinja2 import Undefined, pass_context
from jinja2.runtime import Context
from markupsafe import Markup
from plotly.graph_objects import Figure

logger = logging.getLogger("boredcharts")


def md_to_html(md: str) -> Markup:
    """Renders a Markdown as HTML."""
    return Markup(markdown.markdown(md))


def to_html(fig: Figure | mplfig.Figure) -> Markup:
    """Renders a Figure to an HTML string."""
    match fig:
        case Figure():
            return plotly_to_html(fig)
        case mplfig.Figure():
            return mpl_to_html(fig)
        case _:
            raise ValueError(
                f"Input must be a Plotly/Matplotlib Figure, got {type(fig)}"
            )


def plotly_to_html(fig: Figure) -> Markup:
    """Renders a Plotly Figure as HTML."""
    return Markup(
        fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_height="100%",
            default_width="100%",
            config={
                "displaylogo": False,
                "responsive": True,
                "displayModeBar": False,
            },
        )
    )


def mpl_to_html(fig: mplfig.Figure) -> Markup:
    """Renders a matplotlib Figure as HTML."""
    # TODO: return base64 encoded PNG instead of using mpld3
    figid = uuid.uuid4()
    script = dedent(
        string.Template(
            """
                <script>
                async function resizeMpld3(event, figid) {
                    var targetDiv = event.detail.elt.querySelector(`#${figid}`);
                    if (targetDiv) {
                        var svgElements = targetDiv.querySelectorAll('.mpld3-figure');
                        svgElements.forEach(function(svgElement) {
                            var width = svgElement.getAttribute('width');
                            var height = svgElement.getAttribute('height');
                            svgElement.setAttribute('viewBox', `0 0 ${width} ${height}`);
                            svgElement.setAttribute('width', '100%');
                            svgElement.removeAttribute('height');
                        });
                    }
                }
                document.addEventListener("htmx:afterSettle", (event) => { resizeMpld3(event, "${figid}") });
                </script>
            """
        ).safe_substitute(figid=figid)
    ).strip()
    return Markup(
        mpld3.fig_to_html(
            fig,
            no_extras=True,
            figid=str(figid),
        )
        + script
    )


@pass_context
def figure(
    context: Context,
    figure: str,
    *,
    css_class: str = "min-h-112 min-w-80",
    **kwargs: Any,
) -> Markup:
    """Jinja function to display a figure.

    Calls a figure endpoint and swaps-in the returned HTML snippet.

    e.g.:
    {{ figure("example_figure") }}
    {{ figure("example_figure_with_params", param_1="foo") }}
    """
    report = context.resolve("report")
    if not isinstance(report, Undefined):
        if not isinstance(report, str):
            raise ValueError(f"report must be a string, got {type(report)}")
        kwargs.update(report_name=report)

    request = context.resolve("request")
    if isinstance(request, Undefined):
        raise ValueError("request is not available in the context")
    if not isinstance(request, Request):
        raise ValueError(f"request must be a Request, got {type(request)}")

    url = request.url_for(figure).include_query_params(**kwargs)

    # note using dedent to return a valid root-level element
    return Markup(
        dedent(f"""
            <div
                hx-ext="response-targets"
                class="not-prose {css_class} flex flex-1 items-stretch"
            >
                <figure
                class="plotly-container min-h-0 min-w-0 flex-1"
                hx-get="{url}"
                hx-trigger="load"
                hx-swap="innerHTML"
                hx-target-error="find div"
                >
                    <div class="flex h-full w-full items-center justify-center bg-stone-100">
                        <p>loading...</p>
                    </div>
                </figure>
            </div>
        """).strip()
    )


def row(*figures: Markup) -> Markup:
    """Jinja function to display multiple figures in a single row.

    e.g.:
    {{
        row(
            figure("example_figure"),
            figure("example_figure_with_params", param_1="foo"),
        )
    }}
    """

    # Important:
    # ---
    # For HTML to be a valid block in markdown, it must be a root-level element.
    # This means there shouldn't be any leading whitespace for the first tag in the
    # returned string.
    # I'm guaranteeing that by pinning the fstring to the left, and using indent to
    # correctly format the inner HTML.
    # We could also just use strip on the whole thing and not bother with the indents,
    # but that would make the returned markup less readable.
    out = Markup(
        f"""
<div class="flex flex-wrap not-prose">
{indent("\n".join(figures), " " * 4)}
</div>
        """.strip()
    )
    logger.debug(out)
    return out
