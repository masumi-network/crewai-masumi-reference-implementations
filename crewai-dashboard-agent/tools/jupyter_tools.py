import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from typing import List, Dict, Any
from crewai.tools import BaseTool

class JupyterDashboardTool(BaseTool):
    name = "Jupyter Dashboard Generator"
    description = "Creates interactive Jupyter notebooks for dashboard visualization"

    def __init__(self):
        super().__init__()

    def _execute(self, data: Dict[str, Any], charts: List[Dict], title: str) -> Dict:
        """
        Create a Jupyter notebook with interactive dashboard
        
        Args:
            data: The processed dataset
            charts: List of chart specifications
            title: Dashboard title
        
        Returns:
            Dictionary containing the notebook content
        """
        try:
            # Create a new notebook
            nb = new_notebook()
            
            # Add title and description
            nb.cells.append(new_markdown_cell(f"# {title}\n\nInteractive dashboard created with AI"))
            
            # Add import cells
            imports = """
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import interact, widgets
            """
            nb.cells.append(new_code_cell(imports))
            
            # Add data loading cell
            data_cell = f"""
# Load and prepare data
df = pd.DataFrame({data})
            """
            nb.cells.append(new_code_cell(data_cell))
            
            # Add interactive elements for each chart
            for i, chart in enumerate(charts):
                chart_cell = self._create_chart_cell(chart)
                nb.cells.append(new_markdown_cell(f"## Chart {i+1}"))
                nb.cells.append(new_code_cell(chart_cell))
            
            return {
                "notebook": nb,
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    }
                }
            }
        except Exception as e:
            raise Exception(f"Error creating Jupyter notebook: {str(e)}")

    def _create_chart_cell(self, chart: Dict) -> str:
        """Create an interactive chart cell with widgets"""
        chart_type = chart.get("type", "line")
        
        if chart_type == "line":
            return self._create_line_chart_cell(chart)
        elif chart_type == "bar":
            return self._create_bar_chart_cell(chart)
        elif chart_type == "scatter":
            return self._create_scatter_chart_cell(chart)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    def _create_line_chart_cell(self, chart: Dict) -> str:
        return """
@interact
def update_line_chart(
    x_column=widgets.Dropdown(options=df.columns, description='X-axis'),
    y_column=widgets.Dropdown(options=df.columns, description='Y-axis')
):
    fig = px.line(df, x=x_column, y=y_column)
    fig.show()
        """

    def _create_bar_chart_cell(self, chart: Dict) -> str:
        return """
@interact
def update_bar_chart(
    x_column=widgets.Dropdown(options=df.columns, description='X-axis'),
    y_column=widgets.Dropdown(options=df.columns, description='Y-axis'),
    color=widgets.Dropdown(options=['None'] + list(df.columns), description='Color')
):
    if color == 'None':
        fig = px.bar(df, x=x_column, y=y_column)
    else:
        fig = px.bar(df, x=x_column, y=y_column, color=color)
    fig.show()
        """

    def _create_scatter_chart_cell(self, chart: Dict) -> str:
        return """
@interact
def update_scatter_chart(
    x_column=widgets.Dropdown(options=df.columns, description='X-axis'),
    y_column=widgets.Dropdown(options=df.columns, description='Y-axis'),
    size=widgets.Dropdown(options=['None'] + list(df.columns), description='Size'),
    color=widgets.Dropdown(options=['None'] + list(df.columns), description='Color')
):
    kwargs = {'x': x_column, 'y': y_column}
    if size != 'None':
        kwargs['size'] = size
    if color != 'None':
        kwargs['color'] = color
    fig = px.scatter(df, **kwargs)
    fig.show()
        """ 