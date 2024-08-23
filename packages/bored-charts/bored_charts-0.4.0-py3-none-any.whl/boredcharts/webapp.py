from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from plotly.offline import get_plotlyjs

from boredcharts.jinja import figure, md_to_html, row

module_root = Path(__file__).parent.absolute()


def boredcharts(
    pages: Path,
    figure_router: APIRouter,
    *,
    name: str = "bored-charts",
) -> FastAPI:
    """Creates a boredcharts app."""
    static_root = module_root / "static"
    templates_root = module_root / "templates"
    Path(static_root / "plotlyjs.min.js").write_text(get_plotlyjs())

    app = FastAPI()

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

    @app.get("/")
    async def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            "index.html",
            {"request": request},
        )

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    # TODO: pass pages path into framework, auto generate this route
    @app.get("/report/{report_name}", name="report")
    async def report(report_name: str, request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            "report.html",
            {
                "request": request,
                "report": report_name,
            },
        )

    app.mount("/", figure_router)

    return app
