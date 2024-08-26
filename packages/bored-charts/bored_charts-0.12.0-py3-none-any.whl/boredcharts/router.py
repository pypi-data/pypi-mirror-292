from collections.abc import Callable
from typing import Any

import plotly.graph_objects as go
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.types import DecoratedCallable
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from boredcharts.jinja import to_html


def validate_figure(fig: Any) -> go.Figure:
    assert isinstance(fig, go.Figure)
    return fig


class HTMLFigure:
    """A Plotly Figure that Pydantic can understand and serialize.

    This allows us to return a Plotly Figure from a FastAPI route.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.any_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(go.Figure),
                    core_schema.any_schema(),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(to_html),
        )


class FigureRouter(APIRouter):
    """A FastAPI router that turns charts into endpoints.

    Usage:

    ```py
    from boredcharts import FigureRouter
    import plotly.graph_objects as go

    router = FigureRouter()

    @router.chart("my_chart")
    async def my_chart() -> go.Figure:
        return go.Figure()
    ```
    """

    def chart(
        self,
        name: str,
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """
        Creates a GET route for a chart, just a shorter form of the FastAPI get decorator,
        your function still has to return a HTMLResponse
        """
        path = name if name.startswith("/") else f"/{name}"
        return self.get(
            path=path,
            name=name,
            response_model=HTMLFigure,
            response_class=HTMLResponse,
        )
