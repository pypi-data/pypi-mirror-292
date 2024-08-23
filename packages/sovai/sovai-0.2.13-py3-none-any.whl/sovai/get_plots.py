# Inside plot/get_plot.py

from .plots.bankruptcy.bankruptcy_plots import *
from .plots.breakout.breakout_plots import *
from .plots.accounting.accounting_plots import *
from .plots.ratios.ratios_plots import *
from .plots.institutional.institutional_plots import *
from .plots.news.news_plots import plot_news_daily, create_plot_news_sent_price, plot_above_sentiment_returns, run_dash_news_ts
from .plots.corp_risk.corp_risk_plots import *

from .plots.insider.insider_plots import *
from .plots.allocation.allocation_plots import *
from .plots.earnings_surprise.earnings_surprise_plots import *

from sovai.utils.plot import plotting_data
from typing import Optional, Union, Tuple, List, Dict
from sovai import data
from IPython.display import Markdown, display
import plotly.io as pio
import pandas as pd

# Changing the default plotting backend to Plotly
pd.options.plotting.backend = "plotly"
pd.set_option("display.max_columns", None)

# Setting the default theme for Plotly to a dark mode
pio.templates.default = "plotly_dark"


def enable_plotly_in_cell():
    import IPython
    from plotly.offline import init_notebook_mode

    display(
        IPython.core.display.HTML(
            """<script src="/static/components/requirejs/require.js"></script>"""
        )
    )
    init_notebook_mode(connected=False)


def _draw_graphs(data: Union[Dict, List[Dict]]):
    # print(data)
    if isinstance(data, list):
        for plot in data:
            for _, val in plot.items():
                plotting_data(val)
                break
    else:
        for _, val in data.items():
            plotting_data(val)
            break


from typing import Optional, Union, Tuple, List, Dict

# Assuming other necessary imports and definitions here
def generate_error_message(analysis_type, chart_type, source, verbose):
    if source == "local":
        code_snippet = (
            f"dataset = sov.data('{analysis_type}/monthly')\n"
            f"sov.plot('{analysis_type}', chart_type='{chart_type}', df=dataset)"
        )
        message = (
            f"**Dataset is empty.** Will fetch the data on your behalf:\n\n"
            f"```python\n{code_snippet}\n```"
        )
        if verbose:
            print(display(Markdown(message)))
        return ""
    else:
        display(Markdown("**An unknown error occurred.**"))

## 

plot_ticker_widget

PLOT_FUNCTION_MAPPER = {
    ("bankruptcy", "compare", "local"): plot_bankruptcy_monthly_line,
    ("bankruptcy", "pca_clusters", "local"): plot_pca_clusters,
    ("bankruptcy", "predictions", "local"): plot_ticker_widget,
    ("bankruptcy", "shapley", "database"): _draw_graphs,
    ("bankruptcy", "pca", "database"): _draw_graphs,
    ("bankruptcy", "line", "database"): _draw_graphs,
    ("bankruptcy", "similar", "database"): _draw_graphs,
    ("bankruptcy", "facet", "database"): _draw_graphs,
    ("bankruptcy", "shapley", "database"): _draw_graphs,
    ("bankruptcy", "stack", "database"): _draw_graphs,
    ("bankruptcy", "box", "database"): _draw_graphs,
    ("bankruptcy", "waterfall", "database"): _draw_graphs,
    ("bankruptcy", "pca_relation", "database"): _draw_graphs,
    ("bankruptcy", "line_relation", "database"): _draw_graphs,
    ("bankruptcy", "facet_relation", "database"): _draw_graphs,
    ("bankruptcy", "time_global", "database"): _draw_graphs,
    ("bankruptcy", "stack_global", "database"): _draw_graphs,
    ("bankruptcy", "box_global", "database"): _draw_graphs,
    ("bankruptcy", "waterfall_global", "database"): _draw_graphs,
    ("bankruptcy", "confusion_global", "database"): _draw_graphs,
    ("bankruptcy", "classification_global", "database"): _draw_graphs,
    ("bankruptcy", "precision_global", "database"): _draw_graphs,
    ("bankruptcy", "lift_global", "database"): _draw_graphs,
    ("breakout", "predictions", "local"): get_predict_breakout_plot_for_ticker,
    ("breakout", "accuracy", "local"): interactive_plot_display_breakout_accuracy,
    ("accounting", "balance", "local"): get_balance_sheet_tree_plot_for_ticker,
    ("accounting", "cashflows", "local"): plot_cash_flows,
    ("accounting", "assets", "local"): plot_assets,
    ("ratios", "relative", "local"): plot_ratios_triple,
    ("ratios", "benchmark", "local"): plot_ratios_benchmark,
    ("institutional", "flows", "local"): institutional_flows_plot,
    ("institutional", "prediction", "local"): institutional_flow_predictions_plot,
    ("insider", "percentile", "local"): create_parallel_coordinates_plot_single_ticker,
    ("insider", "flows", "local"): insider_flows_plot,
    ("insider", "prediction", "local"): insider_flow_predictions_plot,
    ("news", "sentiment", "local"): plot_above_sentiment_returns,
    ("news", "strategy", "local"): plot_news_daily,
    ("news", "analysis", "local"): run_dash_news_ts,
    ("corprisk/risks", "line", "local"): plotting_corp_risk_line,
    ("allocation", "line", "local"): create_line_plot_allocation,
    ("allocation", "stacked", "local"): create_stacked_bar_plot_allocation,
    ("earnings", "line", "local"): create_earnings_surprise_plot,


    

    # Add other mappings as needed
}


def plot(
    dataset_name,
    chart_type=None,
    df=None,
    tickers: Optional[List[str]] = None,
    verbose=False,
    purge_cache=False,
    **kwargs,
):
    # The key now includes a placeholder for source since it's needed to determine the data source
    enable_plotly_in_cell()
    for key in PLOT_FUNCTION_MAPPER:
        if key[:2] == (dataset_name, chart_type):
            _, _, source = key
            break
    else:
        raise ValueError(
            f"Plotting function for {dataset_name} with chart type {chart_type} not found."
        )

    plot_function = PLOT_FUNCTION_MAPPER.get((dataset_name, chart_type, source))

    if plot_function:
        if source == "local":
            try:
                if df is None:  # Check if the DataFrame is None
                    add_text = generate_error_message(
                        dataset_name, chart_type, source, verbose
                    )
                    # print(error_message)
                    return plot_function(
                        data(dataset_name + add_text), **kwargs
                    )  # Pass kwargs to the plot function
                else:
                    return plot_function(
                        df, **kwargs
                    )  # Pass kwargs to the plot function
            except:
                return plot_function(**kwargs)

        elif source == "database":
            datasets = data(
                dataset_name + "/charts",
                chart=chart_type,
                tickers=tickers,
                purge_cache=purge_cache,
                **kwargs,
            )  # Pass kwargs to the data function
            # print(datasets)
            if datasets is None:  # Check if the dataset is None
                print(
                    f"Failed to retrieve data for {dataset_name} with chart type {chart_type} and tickers {tickers}"
                )
                return None

            # Check if datasets is a list of datasets, one for each ticker
            if isinstance(datasets, list):
                # print(datasets)
                for dataset in datasets:
                    plot_function(
                        dataset, **kwargs
                    )  # Pass kwargs to the plot function for each dataset (ticker)
            else:
                # print("herer")
                # return datasets
                plot_function(
                    datasets, **kwargs
                )  # Pass kwargs to the plot function for a single dataset

    else:
        raise ValueError(
            f"Plotting function for {dataset_name} with chart type {chart_type} not found."
        )
