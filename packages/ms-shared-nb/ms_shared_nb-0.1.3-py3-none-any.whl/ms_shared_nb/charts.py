import hvplot.pandas  # noqa: F401
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objs as go
import seaborn as sns
from IPython.display import display


def plot_distrib(var_name, df):
    v = df[var_name]
    min_v, max_v, mean_v, median_v = v.min(), v.max(), v.mean(), v.median()
    std_dev_v, kurtosis_v, skew_v = v.std(), v.kurtosis(), v.skew()
    std_dev_range = mean_v - std_dev_v, mean_v + std_dev_v

    # Create a distribution plot using plotly figure_factory
    hist_data = [v]
    group_labels = [var_name]
    fig = ff.create_distplot(hist_data, group_labels, bin_size=0.2, show_rug=False)

    # Add vertical lines for mean, median, and std deviation
    fig.add_trace(go.Scatter(x=[mean_v, mean_v], y=[0, 1], mode="lines", name="mean"))
    fig.add_trace(
        go.Scatter(x=[median_v, median_v], y=[0, 1], mode="lines", name="median")
    )
    fig.add_trace(
        go.Scatter(x=std_dev_range, y=[0, 0], mode="lines", name="std_dev_range")
    )

    # Add points for min and max
    fig.add_trace(
        go.Scatter(x=[min_v, max_v], y=[0, 0], mode="markers", name="min/max")
    )

    # Set labels
    fig.update_layout(
        xaxis_title=var_name,
        yaxis_title="Density",
        title=",".join(
            [
                "{}:{} ".format(a[0], round(a[1], 2))
                for a in zip(
                    *[
                        ["min", "max", "mean", "median", "sd", "ku", "sk"],
                        [
                            v.min(),
                            v.max(),
                            v.mean(),
                            v.median(),
                            std_dev_v,
                            kurtosis_v,
                            skew_v,
                        ],
                    ]
                )
            ]
        ),
    )

    fig.show()


def plot_kde(var_name, df):
    v = df[var_name]
    min_v, max_v, mean_v, median_v = v.min(), v.max(), v.mean(), v.median()
    std_dev_v, kurtosis_v, skew_v = v.std(), v.kurtosis(), v.skew()
    std_dev_range = mean_v - std_dev_v, mean_v + std_dev_v

    # plot kde using seaborn distplot and add labels for mean, median, and std deviation
    sns.kdeplot(v)
    plt.axvline(mean_v, color="r", linestyle="--")
    plt.axvline(median_v, color="g", linestyle="-")
    plt.axvline(std_dev_range[0], color="b", linestyle=":")
    plt.axvline(std_dev_range[1], color="b", linestyle=":")
    plt.axvline(min_v, color="k", linestyle="-.")
    plt.axvline(max_v, color="k", linestyle="-.")
    plt.xlabel(var_name)
    plt.ylabel("Density")
    plt.title(
        ",".join(
            [
                "{}:{} ".format(a[0], round(a[1], 2))
                for a in zip(
                    *[
                        ["min", "max", "mean", "median", "sd", "ku", "sk"],
                        [
                            v.min(),
                            v.max(),
                            v.mean(),
                            v.median(),
                            std_dev_v,
                            kurtosis_v,
                            skew_v,
                        ],
                    ]
                )
            ]
        )
    )
    plt.show()


def plot_col_vs_date(df, column, chart_type):
    # Initialize FigureWidget
    fig = go.FigureWidget()
    # Add trace based on chart type
    if chart_type == "scatter":
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[column],
                mode="markers",
                name=column,
            )
        )
    elif chart_type == "line":
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[column],
                mode="lines",
                name=column,
            )
        )
    elif chart_type == "bar":
        fig.add_trace(go.Bar(x=df["date"], y=df[column], name=column))
    elif chart_type == "histogram":
        fig.add_trace(go.Histogram(x=df[column], name=column))
    # Update layout
    fig.layout.title = f"{column} vs Date"
    fig.layout.xaxis.title = "Date"
    fig.layout.yaxis.title = column
    fig.layout.showlegend = True
    # Display the figure
    display(fig)
