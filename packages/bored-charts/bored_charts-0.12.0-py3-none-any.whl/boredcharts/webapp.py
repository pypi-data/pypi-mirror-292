import logging
from collections.abc import Awaitable, Callable
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from plotly.offline import get_plotlyjs

from boredcharts.jinja import figure, md_to_html, row
from boredcharts.router import FigureRouter
from boredcharts.utils import DirTree, get_dirtree, to_name, to_url_path

logger = logging.getLogger("boredcharts")

module_root = Path(__file__).parent.absolute()


class ReportEndpoint(NamedTuple):
    name: str
    path: str
    endpoint: Callable[..., Awaitable[HTMLResponse]]


def boredcharts(
    pages: Path,
    figures: FigureRouter | list[FigureRouter],
    *,
    index_name: str = "bored-charts",
) -> FastAPI:
    """Creates a boredcharts app.

    Usage:

    ```py
    from pathlib import Path
    from boredcharts import FigureRouter, boredcharts
    import plotly.graph_objects as go

    router = FigureRouter()

    @router.chart("my_chart")
    async def my_chart() -> go.Figure:
        return go.Figure()

    app = boredcharts(Path("pages"), router)
    ```
    """
    static_root = module_root / "static"
    templates_root = module_root / "templates"
    Path(static_root / "plotlyjs.min.js").write_text(get_plotlyjs())

    app = FastAPI(title=index_name)

    app.mount(
        "/static",
        StaticFiles(directory=static_root),
        "static",
    )

    # --- templates ------------------------------------------------------------
    templates = Jinja2Templates(
        env=Environment(
            loader=FileSystemLoader(
                [
                    pages,  # being first allows user to overwrite default templates
                    templates_root,
                ],
            ),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        ),
    )
    templates.env.globals["title"] = index_name
    templates.env.filters["markdown"] = md_to_html
    templates.env.globals["figure"] = figure
    templates.env.globals["row"] = row
    templates.env.globals["to_name"] = to_name

    # --- report endpoints -----------------------------------------------------
    report_tree = get_dirtree(pages)
    create_report_endpoints(app, templates, report_tree)

    # --- figure endpoints -----------------------------------------------------
    if not isinstance(figures, list):
        figures = [figures]
    for router in figures:
        # tag grouping for openapi schema
        tags: list[str | Enum] | None = None
        if router.tags is None or len(router.tags) == 0:
            tag = "figures"
            if router.prefix:
                tag += f":{router.prefix.lstrip("/")}"
            tags = [tag]

        app.include_router(router, prefix="/figure", tags=tags)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


def create_report_endpoints(
    app: FastAPI,
    templates: Jinja2Templates,
    report_tree: DirTree,
    parent: Path = Path(),
) -> None:
    tag = ":".join(["reports"] + list(report_tree.name.parts))

    # recurse
    for subtree in report_tree.dirs:
        create_report_endpoints(
            app,
            templates,
            subtree,
            parent=report_tree.name,
        )

    # index
    index_dir = parent / report_tree.name
    index_path = to_url_path(index_dir)

    index_name = to_name(index_path, "index")
    logger.debug(
        f"Creating index endpoint for: path={index_path}, name={index_name}, parent={index_dir}"
    )
    app.router.add_api_route(
        path=index_path,
        endpoint=create_index_endpoint(report_tree, templates, str(index_dir)),
        name=index_name,
        tags=[tag],
    )

    # reports
    report_endpoints: list[ReportEndpoint] = []
    for report_file in report_tree.files:
        report_file = parent / report_tree.name / report_file
        report_path = to_url_path(report_file)
        report_name = to_name(report_path)
        logger.debug(
            f"Creating report endpoint for: file={report_file}, path={report_path}, name={report_name}"
        )

        report_endpoints.append(
            ReportEndpoint(
                name=report_name,
                path=report_path,
                endpoint=create_report_endpoint(str(report_file), templates),
            )
        )
    for report_endpoint in report_endpoints:
        app.router.add_api_route(
            path=report_endpoint.path,
            endpoint=report_endpoint.endpoint,
            name=report_endpoint.name,
            tags=[tag],
        )


def create_index_endpoint(
    report_tree: DirTree,
    templates: Jinja2Templates,
    parent: str = "",
) -> Callable[..., Awaitable[HTMLResponse]]:
    async def index_endpoint(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "report_tree": report_tree,
                "parent": parent,
            },
        )

    return index_endpoint


def create_report_endpoint(
    report: str,
    templates: Jinja2Templates,
) -> Callable[..., Awaitable[HTMLResponse]]:
    async def report_endpoint(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            "report.html",
            {
                "request": request,
                "report": report,
            },
        )

    return report_endpoint
