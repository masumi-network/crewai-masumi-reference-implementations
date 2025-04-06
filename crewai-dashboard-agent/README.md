# CrewAI Dashboard Generator with Masumi Integration

This project allows users to generate interactive data dashboards using natural language requests. It leverages CrewAI for agent-based task execution and Masumi for decentralized payments on Cardano.

## Overview

The Dashboard Generator uses a team of specialized AI agents to:
1. Interpret natural language dashboard requests
2. Fetch and process data from various sources
3. Design appropriate visualizations
4. Build interactive Jupyter notebooks or web dashboards

All of these capabilities are monetized through Masumi's decentralized payment system on the Cardano blockchain.

## Technical Components

### Agent Architecture

The system uses four specialized CrewAI agents:

- **Prompt Interpreter**: Analyzes natural language requests and extracts dashboard requirements
- **Data Fetcher**: Connects to data sources and prepares data for visualization
- **Chart Designer**: Selects optimal chart types and visual parameters
- **Jupyter Dashboard Builder**: Creates interactive Jupyter notebooks with widgets

### Dashboard Formats

The system supports multiple output formats:

1. **Jupyter Notebooks**: Interactive notebooks with ipywidgets for data exploration
2. **Web Dashboards**: Static or interactive web-based visualizations
3. **PDF Reports**: Formatted reports for sharing and printing

### Key Technologies

- **CrewAI**: Agent-based workflow orchestration
- **Jupyter**: Interactive computing environment with notebooks and widgets
- **Plotly**: Interactive data visualization library
- **Masumi**: Decentralized payment infrastructure on Cardano
- **FastAPI**: High-performance API framework

## Installation

### Prerequisites

- Python 3.12.x
- Node.js v18+ (for Masumi)
- PostgreSQL 15 (for Masumi)
- Blockfrost API key (for Cardano integration)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crewai-dashboard-agent.git
   cd crewai-dashboard-agent
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install and configure Masumi following [official documentation](https://docs.masumi.network/get-started/installation).

4. Configure environment variables by copying `.env.example` to `.env` and filling in values:
   ```bash
   cp .env.example .env
   ```

## Configuration

The `.env` file should contain:

```ini
# Payment Service
PAYMENT_SERVICE_URL=http://localhost:3001/api/v1
PAYMENT_API_KEY=your_payment_service_api_key

# Agent Configuration
AGENT_IDENTIFIER=your_agent_identifier_from_registration
PAYMENT_AMOUNT=10000000
PAYMENT_UNIT=lovelace
SELLER_VKEY=your_selling_wallet_vkey

# OpenAI API
OPENAI_API_KEY=your_openai_api_key
```

## Usage

### Starting the API Server

Run the FastAPI server:

```bash
python main.py api
```

The API will be available at: `http://localhost:8000`

### API Endpoints

The API exposes several endpoints following the Masumi API standard:

- **POST /start_job**: Start a new dashboard generation job
- **GET /status**: Check the status of a job
- **GET /availability**: Check if the service is available
- **GET /input_schema**: Get the input data schema
- **GET /health**: Health check endpoint

### Example Request

```bash
curl -X POST "http://localhost:8000/start_job" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier_from_purchaser": "user123",
    "input_data": {
      "text": "Create a dashboard showing monthly sales trends by product category",
      "data_source": "data/sales.csv",
      "output_format": "jupyter",
      "interactive": true
    }
  }'
```

## Jupyter Integration

The system leverages Jupyter for creating interactive dashboards:

### Features

- **Interactive Widgets**: Dynamic chart customization with ipywidgets
- **Voilà Support**: Convert notebooks to web applications
- **Multiple Chart Types**: Support for line, bar, scatter, and other chart types
- **Custom Data Processing**: Data transformation and analysis cells

### Using Generated Notebooks

1. After receiving a completed job, download the Jupyter notebook
2. Open with JupyterLab: `jupyter lab path/to/notebook.ipynb`
3. Use the interactive widgets to explore your data
4. Convert to a web app: `voila path/to/notebook.ipynb`

## Masumi Payment Integration

This service uses Masumi for decentralized payments:

1. When a job starts, a payment request is created on the Cardano blockchain
2. The user pays using their Cardano wallet
3. The system monitors payment status and executes the dashboard creation once paid
4. After completion, the payment is finalized

## Extending the System

### Adding New Data Sources

Extend the `DataFetcherTool` in `tools/dashboard_tools.py` to support additional data sources.

### Adding New Chart Types

Add new chart generation methods to `ChartDesignerTool` in `tools/dashboard_tools.py` and corresponding cells in `JupyterDashboardTool`.

### Customizing the Agents

Modify agent roles, goals, and tools in `crew_definition.py` to change agent behavior.

## Production Deployment

For production use:

1. Deploy on a server with adequate CPU and memory resources
2. Set up a proper database instead of the in-memory job store
3. Configure proper authentication and rate limiting
4. Use HTTPS with valid certificates
5. Set up logging to persistent storage

## Troubleshooting

Common issues:

- **Payment Not Detected**: Ensure Masumi service is properly configured and running
- **Data Fetching Fails**: Check data source availability and format
- **Notebook Generation Error**: Verify that all required Python packages are installed

## Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [Jupyter Documentation](https://jupyter.org)
- [Masumi Documentation](https://docs.masumi.network)
- [Plotly Documentation](https://plotly.com/python/)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
