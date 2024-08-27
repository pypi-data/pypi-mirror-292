import ipywidgets as widgets
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from ipydatagrid import DataGrid
from IPython.display import display, clear_output

from shared_eda.utils import summarize_df


class DataFrameAnalyzer:
    def __init__(self, df):
        self.df = df
        
        # Create interactive widgets
        self.info_widget = widgets.Output()
        self.describe_widget = widgets.Output()
        self.shape_widget = widgets.Output()
        self.plot_widget = widgets.Output()
        chart_types = ['bar', 'box', 'scatter', 'hist', 'kde', 'countplot', 'pie', 'outliers']

        self.x_column_select = widgets.Dropdown(
            options=self.df.columns,
            description='X Column:'
        )

        self.y_column_select = widgets.Dropdown(
            options=self.df.columns,
            description='Y Column:'
        )
        self.use_selected_columns_checkbox = widgets.Checkbox(  
            value=False,
            description='Use Selected Columns',
            disabled=False,
        )
        self.chart_type_select = widgets.Dropdown(
            options=chart_types,
            description='Chart Type:'
        )

        # Register the update function to the widgets
        self.x_column_select.observe(self.update_output_widgets, 'value')
        self.y_column_select.observe(self.update_output_widgets, 'value')
        self.chart_type_select.observe(self.update_output_widgets, 'value')

        describe = summarize_df(self.df)
        self.desc_datagrid = DataGrid(describe, selection_mode='row')
        
        # Display the interactive widgets
        display(widgets.VBox([
            widgets.HBox([self.shape_widget, self.x_column_select, self.y_column_select, self.chart_type_select, self.use_selected_columns_checkbox]),
            widgets.HBox([self.desc_datagrid, self.plot_widget]),
        ]))

        # Display the DataFrame info
        self.display_dataframe_describe()
        self.display_dataframe_shape()

    @property
    def selected_columns(self):
        if not self.use_selected_columns_checkbox.value:
            return [self.x_column_select.value, self.y_column_select.value]
        # get selected columns from datagrid
        selected_rows_index = [_s['r1'] for _s in self.desc_datagrid.selections]
        selected_rows = self.desc_datagrid.data.iloc[selected_rows_index]
        return selected_rows['column_name'].tolist()
        
        
    # Function to display DataFrame describe
    def display_dataframe_describe(self):
        with self.describe_widget:
            self.df_describe = summarize_df(self.df)
            datagrid = DataGrid(self.df_describe)
            display(datagrid)

    # Function to display DataFrame shape
    def display_dataframe_shape(self):
        with self.shape_widget:
            self.df_shape = f"shape -> {self.df.shape}"
            display(self.df_shape)

    # Function to plot KDE plot for all numeric columns
    def plot_kde_plots(self):
        with self.plot_widget:
            for column in self.selected_columns:
                sns.kdeplot(data=self.df[column])
                plt.title(f"KDE Plot: {column}")
                plt.show()
        
    def plot_value_counts(self, as_chart_type):
        '''
        as_chart_type: 'countplot', 'bar' or 'pie'
        '''
        with self.plot_widget:
            for column in self.selected_columns:
                if as_chart_type == 'countplot':
                    sns.countplot(data=self.df, x=column)
                elif as_chart_type == 'bar':
                    self.df[column].value_counts().plot.bar()
                elif as_chart_type == 'pie':
                    self.df[column].value_counts().plot.pie()
                plt.title(f"{as_chart_type.capitalize()}: {column}")
                plt.show()
    
    def plot_outliers(self, as_chart_type):
        '''
        as_chart_type: 'box' or 'scatter'
        '''
        with self.plot_widget:
            for column in self.selected_columns:
                if as_chart_type == 'box':
                    sns.boxplot(data=self.df, x=column)
                elif as_chart_type == 'scatter':
                    sns.scatterplot(data=self.df, x=column)
                plt.title(f"{as_chart_type.capitalize()}: {column}")
                plt.show()

     # Function to plot different charts for data understanding
    def plot_charts(self):
        with self.plot_widget:
            clear_output(wait=True)  # Clear previous chart
            x_column = self.x_column_select.value
            y_column = self.y_column_select.value
            chart_type = self.chart_type_select.value
            if chart_type == 'bar':
                sns.barplot(data=self.df, x=x_column, y=y_column)
            elif chart_type == 'box':
                sns.boxplot(data=self.df, x=x_column, y=y_column)
            elif chart_type == 'scatter':
                sns.scatterplot(data=self.df, x=x_column, y=y_column)
            elif chart_type == 'hist':
                sns.histplot(data=self.df, x=x_column, y=y_column)
            elif chart_type == 'kde':
                self.plot_kde_plots()
            elif chart_type == 'countplot':
                self.plot_value_counts('countplot')
            elif chart_type == 'pie':
                self.plot_value_counts('pie')
            elif chart_type == 'outliers':
                self.plot_outliers('box')
            plt.title(f"{chart_type.capitalize()} Plot: {x_column} vs {y_column}")
            plt.show()

    # Function to update the output widgets
    def update_output_widgets(self, change):
        self.plot_charts()


