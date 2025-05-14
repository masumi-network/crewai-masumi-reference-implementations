# CrewAI Masumi Agent Collection

A collection of specialized CrewAI agents integrated with Masumi for decentralized payments.

## Overview

This repository contains multiple AI agent implementations designed for production use cases, demonstrating integration with Masumi's payment infrastructure on Cardano. Each agent is a part of the CrewAI framework, allowing for sophisticated, multi-agent collaboration to perform complex tasks.

## Available Agents

| Agent                         | Repository                                                              | Status             | Description                                                 |
|-------------------------------|-------------------------------------------------------------------------|--------------------|-------------------------------------------------------------|
| **Contract Creation Agent**   | [`crewai-contract-creation-agent`](./crewai-contract-creation-agent)    | In Development 🔧  | Generate legal contracts with specialized agents          |
| **Dashboard Agent**           | [`crewai-dashboard-agent`](./crewai-dashboard-agent)                    | In Development 🔧  | Create interactive dashboard reports                        |
| **SEO Agent**                 | [`crewai-seo-agent`](./crewai-seo-agent)                                | In Development 🔧  | Optimize content and analyze SEO performance                |
| **Meeting Agent**             | [`crewai_meeting_agent`](./crewai_meeting_agent)                        | In Development 🔧  | Prepares comprehensive meeting packages using AI agents     |
| **PR Writer Agent**           | [`crewai-pr-writer-agent`](./crewai-pr-writer-agent)                    | In Development 🔧  | Generates Pull Request descriptions and summaries         |

All agents are intended for deployment and can be made available on platforms like the [Sokosumi Marketplace](https://sokosumi.com).

## Architecture

- FastAPI backend for each agent, providing MIP-003 compliant endpoints.
- Integration with the Masumi payment system for monetizing agent services.
- Core agent logic and CrewAI definitions typically found in `agent_definition.py` or `crew_definition.py`.
- Common utilities for logging (e.g., `logging_config.py`) and environment configuration.

## Setup Requirements

### Prerequisites

- Python 3.12+ (Python 3.12.8 recommended for optimal compatibility)
- A Cardano wallet (e.g., Nami, Eternl) for interacting with the Masumi payment system.
- Masumi API credentials (API Key, Agent Identifier).
- OpenAI API Key (and other relevant service keys like Serper API Key, if used by the agent).
- CrewAI, FastAPI, and other Python packages as listed in each agent's `requirements.txt`.

### Environment Setup

1.  Clone this repository:
    ```bash
    git clone <repository-url>
    cd crewai-masumi-reference-implementations
    ```

2.  Navigate to a specific agent's directory:
    ```bash
    cd name-of-the-agent-directory # e.g., cd crewai-contract-creation-agent
    ```

3.  Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5.  Configure the `.env` file in the agent's directory. Create one if it doesn't exist, based on the agent's needs. A typical `.env` file might look like this:
    ```env
    OPENAI_API_KEY="your_openai_api_key"
    SERPER_API_KEY="your_serper_api_key" # If used by the agent

    PAYMENT_SERVICE_URL="https://payment.masumi.network/api/v1"
    PAYMENT_API_KEY="your_masumi_payment_api_key"
    NETWORK="PREPROD"  # or "MAINNET"
    AGENT_IDENTIFIER="your_agent_identifier_from_masumi"
    
    # Default payment amounts (agent-specific, in lovelace)
    PAYMENT_AMOUNT="10000000"  # Example: 10 ADA
    PAYMENT_UNIT="lovelace"
    
    SELLER_VKEY="your_cardano_seller_verification_key" 
    # Often your wallet's public key or a specific key registered with Masumi
    ```

## Running an Agent

After completing the setup for a specific agent:

1.  Ensure you are in the agent's directory with the virtual environment activated.
2.  Start the FastAPI server (typically, but check the agent's specific run command):
    ```bash
    python main.py api
    ```
    The server will usually be available at `http://localhost:8000`. You can access the API documentation (Swagger UI) at `http://localhost:8000/docs`.

## Troubleshooting Masumi Integration

### Common Issues

1.  **"network: Required" error / Payment Initialization Failure**:
    *   Ensure `NETWORK` is correctly set to `"PREPROD"` or `"MAINNET"` (all caps) in your `.env` file.
    *   Verify `PAYMENT_SERVICE_URL` is `https://payment.masumi.network/api/v1`.
    *   Confirm your `PAYMENT_API_KEY` and `AGENT_IDENTIFIER` are correctly set and valid for the chosen network.

2.  **F-string or Syntax Errors**:
    *   Ensure you are using Python 3.10 or newer. Python 3.12.8 is recommended.
    *   Be mindful of quote usage within f-strings if nesting them.

3.  **Payment Connection Issues**:
    *   Check your internet connectivity and ensure no firewalls are blocking access to `payment.masumi.network`.
    *   Double-check that your `AGENT_IDENTIFIER` is correctly registered on the Masumi platform.

4.  **Python Version Compatibility**:
    *   While Python 3.10+ might work, these reference implementations are tested and developed with Python 3.12.x. Using the specified version (e.g., 3.12.8, check agent-specific `runtime.txt` or `.python-version`) is recommended.

## Development Guidelines

When developing a new agent or modifying an existing one:

1.  Use the structure of existing agents in this repository as a template.
2.  Ensure all API endpoints interacting with Masumi are MIP-003 compliant.
3.  Maintain a consistent environment variable structure (as shown in the `.env` example).
4.  Implement payment status monitoring and handling as demonstrated in `main.py` of the reference agents.
5.  Incorporate robust error handling and logging (using `logging_config.py` or similar).
6.  Define agent roles, tasks, and tools clearly, typically within a `crew_definition.py` or `agent_definition.py` file.

## Contributing

Contributions are welcome! To contribute a new agent or improve an existing one:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  If adding a new agent, you can clone the structure from an existing working agent.
4.  Implement the agent's specific capabilities, ensuring CrewAI best practices.
5.  Thoroughly test the agent, including its integration with the Masumi payment system on PREPROD.
6.  Update the agent's own `README.md` with specific details, setup instructions, and usage examples.
7.  Add the new agent to the main `README.md` table in this root directory.
8.  Submit a Pull Request with a clear description of your changes.

## License

MIT License

Copyright (c) 2025 Masumi Network

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
