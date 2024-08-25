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
from boredcharts import BCRouter, boredcharts

pages = Path(__file__).parent.absolute() / "pages"
figures = BCRouter()


@figures.chart("population")
async def population(country: str) -> go.Figure:
    df = px.data.gapminder().query(f"country=='{country}'")
    fig = px.bar(df, x="year", y="pop")
    return fig


app = boredcharts(
    pages=pages,
    figures=figures,
)
```

### Write a markdown report

pages/populations.md:

```md
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

A more full project structure might look like this:

```
my-reports
├── myreports
│   ├── pages           <-- put your markdown reports here
│   │   └── example.md
│   ├── __init__.py
│   ├── app.py          <-- spin up the app here
│   └── figures.py      <-- define your figures here
├── README.md
└── pyproject.toml
```

## Extensibility

The bored-charts app is just a FastAPI (ASGI) app,
so you can integrate it into your existing projects or extend it as needed.

## Roadmap

See the [Github repo](https://github.com/oliverlambson/bored-charts)
