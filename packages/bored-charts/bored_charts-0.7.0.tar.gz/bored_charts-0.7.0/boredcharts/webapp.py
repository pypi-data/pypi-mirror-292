from enum import Enum
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from plotly.offline import get_plotlyjs

from boredcharts.jinja import figure, md_to_html, row
from boredcharts.router import BCRouter

module_root = Path(__file__).parent.absolute()


def boredcharts(
    pages: Path,
    figures: BCRouter | list[BCRouter],
    *,
    name: str = "bored-charts",
) -> FastAPI:
    """Creates a boredcharts app."""
    static_root = module_root / "static"
    templates_root = module_root / "templates"
    Path(static_root / "plotlyjs.min.js").write_text(get_plotlyjs())

    app = FastAPI(title=name)

    app.mount(
        "/static",
        StaticFiles(directory=static_root),
        "static",
    )

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
    templates.env.globals["title"] = name
    templates.env.globals["reports"] = [
        {"name": f.stem}
        for f in sorted(
            pages.glob("*.md"),
            reverse=True,
        )
    ]
    templates.env.filters["markdown"] = md_to_html
    templates.env.globals["figure"] = figure
    templates.env.globals["row"] = row

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", tags=["reports"])
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            "index.html",
            {"request": request},
        )

    # TODO: pass pages path into framework, auto generate this route
    @app.get("/report/{report_name}", name="report", tags=["reports"])
    async def report(report_name: str, request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            "report.html",
            {
                "request": request,
                "report": report_name,
            },
        )

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

    return app
