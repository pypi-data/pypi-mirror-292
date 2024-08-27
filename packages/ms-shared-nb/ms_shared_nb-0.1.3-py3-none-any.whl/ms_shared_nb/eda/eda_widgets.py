from ipydatagrid import DataGrid
from IPython.display import display
from ipywidgets import Button, HBox, Text, VBox, widgets

from ms_shared_nb.eda.df_filtering import filter_df_by_filter_type

df_filter_widgets_config = [
    {
        "widget_type": widgets.Dropdown,
        "options": ["column_regex", "column_type", "date_string"],
        "value": "column_regex",
        "description": "filter_type",
    },
    {"widget_type": widgets.Text, "value": "", "description": "filter_value"},
]

df_date_col_widgets_config = [
    {"widget_type": widgets.Checkbox, "value": False, "description": "index_is_date"},
    {"widget_type": widgets.Text, "value": "", "description": "date_col"},
]


def create_widgets_from_config(config):
    return {
        widget_config["description"]: widget_config["widget_type"](**widget_config)
        for widget_config in config
    }


class GridWidgetClass:
    def __init__(self, config_list, layout):
        self.config_list = config_list
        self.layout = layout
        self.widgets = {}
        self.next_position = [0, 0]
        self.create_widgets()

    def create_widgets(self):
        for config in self.config_list:
            for conf in config:
                widget_type = conf["widget_type"]
                position = conf.get("grid_position", self.get_next_position())
                widget_conf = {
                    key: value
                    for key, value in conf.items()
                    if key not in ["widget_type", "grid_position"]
                }
                widget_instance = widget_type(**widget_conf)
                self.layout[position[0], position[1]] = widget_instance
                self.widgets[conf["description"]] = widget_instance

    def get_next_position(self):
        position = tuple(self.next_position)
        if self.next_position[1] < self.layout.n_columns - 1:
            # If next position is within the same row
            self.next_position[1] += 1
        else:
            # If next position is in a new row
            self.next_position[0] += 1
            self.next_position[1] = 0
        return position

    def add_widget(self, widget_or_config, position=None):
        if isinstance(widget_or_config, dict):
            widget_config = widget_or_config
            widget_type = widget_config["widget_type"]
            widget_key = widget_config.get("description")
            widget_config = {
                key: value
                for key, value in widget_config.items()
                if key not in ["widget_type", "grid_position"]
            }
            widget_instance = widget_type(**widget_config)
        else:
            widget_instance = widget_or_config
            widget_key = widget_instance.description

        if position is None:
            position = self.get_next_position()

        self.layout[position[0], position[1]] = widget_instance
        self.widgets[widget_key] = widget_instance

    def display_widgets(self):
        display(self.layout)

    def get_widget_value(self, widget_key):
        return self.widgets[widget_key].value

    def get_values(self):
        return {name: widget.value for name, widget in self.widgets.items()}


class ExtendedGridWidgetClass(GridWidgetClass):
    def __init__(self, base_class_instance, additional_config):
        if not isinstance(base_class_instance, GridWidgetClass):
            raise ValueError(
                "base_class_instance must be an instance of GridWidgetClass"
            )
        self.layout = base_class_instance.layout
        self.widgets = base_class_instance.widgets
        self.next_position = base_class_instance.next_position
        self.add_additional_widgets(additional_config)

    def add_additional_widgets(self, additional_config):
        for conf in additional_config:
            widget_type = conf["widget_type"]
            position = conf.get("grid_position", self.get_next_position())
            widget_conf = {
                key: value
                for key, value in conf.items()
                if key not in ["widget_type", "grid_position"]
            }
            widget_instance = widget_type(**widget_conf)
            self.layout[position[0], position[1]] = widget_instance
            self.widgets[conf["description"]] = widget_instance


class FilterWidgetClass(GridWidgetClass):
    def __init__(self, datagrid):
        layout = widgets.GridspecLayout(1, 4)  # adjust dimensions as needed
        self.datagrid = datagrid
        self.add_button = Button(description="Add")
        self.add_button.on_click(self.add_filter)
        self.apply_button = Button(description="Apply")
        self.apply_button.on_click(self.apply_filters)
        super().__init__([df_filter_widgets_config, df_date_col_widgets_config], layout)
        self.filter_textbox = Text(
            description="Filters:", value="", layout=widgets.Layout(width="100%")
        )

    def add_filter(self, button):
        fitler_type, filter_value = (
            self.get_widget_value("filter_type"),
            self.get_widget_value("filter_value"),
        )
        self.update_filter_text_area(fitler_type, filter_value)

    def apply_filters(self, button):
        pass

    def update_filter_text_area(self, filter_text, filter_value):
        value = f"{filter_text}: {filter_value}"
        self.filter_textbox.value += f"{value},"

    def get_filters(self):
        filters_text = self.filter_textbox.value
        filters = []
        for filter_text in filters_text.split(","):
            if filter_text:
                filter_type, filter_value = filter_text.split(":")
                filters.append((filter_type.strip(), filter_value.strip()))
        return filters

    def display_widgets(self):
        l = [self.add_button, self.apply_button, self.filter_textbox]
        display(VBox([self.layout, HBox(l)]))


class FiltersWithGridWidgetClass(FilterWidgetClass):
    def __init__(self, df):
        self.datagrid = DataGrid(
            df,
            selection_mode="column",
            base_row_size=30,
            base_column_size=300,
            layout={"height": "400px"},
            theme="material-dark",
        )
        super().__init__(self.datagrid)

    def display_widgets(self):
        l = [self.add_button, self.apply_button, self.filter_textbox]
        display(VBox([self.layout, HBox(l), self.datagrid]))

    def apply_filters(self, button):
        df = self.datagrid.data
        for filter_type, filter_value in self.get_filters():
            filter_values = {"filter_type": filter_type, "filter_value": filter_value}
            if filter_type == "date_string":
                filter_values["index_is_date"] = self.get_widget_value("index_is_date")
                filter_values["date_col"] = self.get_widget_value("date_col")
            df = filter_df_by_filter_type(self.datagrid.data, **filter_values)
        self.datagrid.data = df
        self.datagrid.auto_fit_columns = True

    def get_selected_cols(self):
        columns = self.datagrid.data.columns
        return [columns[s["c1"]] for s in self.datagrid.selections]
