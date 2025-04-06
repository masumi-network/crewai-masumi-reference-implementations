from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from crewai.tools import BaseTool
import json

class DataFetcherTool(BaseTool):
    name = "Data Fetcher"
    description = "Fetches data from various sources including CSV, Google Sheets, and APIs"

    def __init__(self):
        super().__init__()

    def _execute(self, data_source: str, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Fetch data from the specified source
        
        Args:
            data_source: Path or URL to data source
            parameters: Additional parameters for data fetching
        
        Returns:
            pandas DataFrame containing the fetched data
        """
        try:
            if data_source.endswith('.csv'):
                return pd.read_csv(data_source)
            # Add more data source handlers here
            else:
                raise ValueError(f"Unsupported data source: {data_source}")
        except Exception as e:
            raise Exception(f"Error fetching data: {str(e)}")

class ChartDesignerTool(BaseTool):
    name = "Chart Designer"
    description = "Designs and generates charts based on data and requirements"

    def __init__(self):
        super().__init__()

    def _execute(self, data: pd.DataFrame, chart_type: str, parameters: Dict[str, Any] = None) -> Dict:
        """
        Create chart specification based on data and requirements
        
        Args:
            data: DataFrame containing the data to visualize
            chart_type: Type of chart to create
            parameters: Additional visualization parameters
        
        Returns:
            Dictionary containing chart specification
        """
        try:
            if chart_type == "line":
                fig = px.line(data, **parameters)
            elif chart_type == "bar":
                fig = px.bar(data, **parameters)
            elif chart_type == "scatter":
                fig = px.scatter(data, **parameters)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            return json.loads(fig.to_json())
        except Exception as e:
            raise Exception(f"Error creating chart: {str(e)}")

class DashboardBuilderTool(BaseTool):
    name = "Dashboard Builder"
    description = "Builds complete dashboards from chart specifications"

    def __init__(self):
        super().__init__()

    def _execute(self, charts: List[Dict], layout: Dict[str, Any] = None) -> Dict:
        """
        Build complete dashboard from chart specifications
        
        Args:
            charts: List of chart specifications
            layout: Dashboard layout configuration
        
        Returns:
            Dictionary containing complete dashboard specification
        """
        try:
            dashboard = {
                "charts": charts,
                "layout": layout or {},
                "timestamp": pd.Timestamp.now().isoformat()
            }
            return dashboard
        except Exception as e:
            raise Exception(f"Error building dashboard: {str(e)}") 