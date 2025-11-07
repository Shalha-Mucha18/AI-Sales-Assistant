import io, base64
import pandas as pd
import matplotlib.pyplot as plt

def plot_series(series: pd.Series, title: str):
    fig, ax = plt.subplots(figsize=(5, 3))
    series.plot(ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(series.name if series.name else "Value")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")



