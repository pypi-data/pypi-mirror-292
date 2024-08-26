# bored-charts

Build easy, minimal, PDF-able data reports with markdown and python.

The idea is you do your analysis in Python, as you normally would, and dumping your
figures into a nice report written in markdown is now super low-effort: you decorate
the function to generate the figure (that you already wrote when doing your analysis)
and it becomes available to bored-charts so you can present your findings clearly.

## Minimal example

Install bored-charts and uvicorn:

```bash
pip install bored-charts uvicorn
```

### Create your app

```python
# main.py

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
from boredcharts import FigureRouter, boredcharts

figures = FigureRouter()


@figures.chart("population")
async def population(country: str) -> go.Figure:
    df = px.data.gapminder().query(f"country=='{country}'")
    fig = px.bar(df, x="year", y="pop")
    return fig


app = boredcharts(pages=Path(__file__).parent, figures=figures)
```

### Write a markdown report

```md
<!-- populations.md -->

## Populations

USA's population has been growing linearly for the last 70 years:

{{ figure("population", country="United States") }}
```

### Run your app

```bash
uvicorn main:app --reload
```

🎉Now you can view your reports at [http://localhost:8000](http://localhost:8000)!

## Going further

A more full project structure might look like this
(see the [full example here](https://github.com/oliverlambson/bored-charts/tree/main/examples/full)):

```
my-reports
├── analysis          <-- do your analysis and define your figures
│   ├── __init__.py
│   ├── figures.py
│   └── ...
├── pages             <-- write your markdown reports
│   ├── example.md
│   └── ...
├── app.py            <-- spin up the bored-charts app
├── pyproject.toml
└── README.md
```

## Extensibility

The bored-charts app is just a FastAPI (ASGI) app,
so you can integrate it into your existing projects or extend it as needed.

## Roadmap

See the [Github repo](https://github.com/oliverlambson/bored-charts)
