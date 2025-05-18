# 🚀 CrewAI Masumi Starter Kit

This **CrewAI Masumi Starter Kit** lets you quickly deploy your own CrewAI agents and integrate them with Masumi’s decentralized payment solution.

**Key benefits:**

- Simple setup: Just clone, configure, and deploy.
- Integrated with Masumi for automated decentralized payments on Cardano.
- Production-ready API built with FastAPI.

---

## 📌 Quick Start

Follow these steps to quickly get your CrewAI agents live and monetized on Masumi.

## 📖 Steps

### **1. Clone Repository**

Clone the repository and navigate into the directory:

```bash
git clone https://github.com/masumi-network/crewai-masumi-quickstart-template.git
cd crewai-masumi-starter-kit
```

---

### 🔧 **2. Define Your CrewAI Agents**

Edit the file **`crew_definition.py`** to define your agents and their tasks.

Example:

```python
from crewai import Agent, Crew, Task
from logging_config import get_logger

class ResearchCrew:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()

    def create_crew(self):
        researcher = Agent(
            role='Research Analyst',
            goal='Find and analyze key information',
            backstory='Expert at extracting information',
            verbose=self.verbose
        )

        writer = Agent(
            role='Content Summarizer',
            goal='Create clear summaries from research',
            backstory='Skilled at transforming complex information',
            verbose=self.verbose
        )

        crew = Crew(
            agents=[researcher, writer],
            tasks=[
                Task(
                    description='Research: {text}',
                    expected_output='Detailed research findings about the topic',
                    agent=researcher
                ),
                Task(
                    description='Write summary',
                    expected_output='Clear and concise summary of the research findings',
                    agent=writer
                )
            ]
        )
        return crew
```

---

### 🌐 **3. Deploy Your Service**

Deploy your CrewAI service using a hosting provider such as:

- **Digital Ocean** (Recommended)
- AWS, Google Cloud, Azure, etc.

Your project requires:

- **Python 3.12.x**
- **FastAPI** for the API
- **Uvicorn** ASGI server

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API server:

```bash
uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}
```

The API documentation will be available at:

```
http://localhost:8000/docs
```

---

### 💳 **4. Install the Masumi Payment Service**

Masumi handles decentralized payments via Cardano:

Follow the official Masumi installation guide:

👉 [Masumi Payment Installation Guide](https://docs.masumi.network/get-started/installation)

Ensure you have:

- Node.js v18+
- PostgreSQL 15
- Blockfrost API key for Cardano Preprod network

Run Masumi (recommended with Docker):

```bash
docker compose up -d
```

Open Masumi Admin Dashboard:

```
http://localhost:3001/admin
```

---

### 💰 **5. Top Up Your Wallet with Test ADA**

Get free Test ADA from Cardano Faucet:

- Copy your wallet address from the Masumi Dashboard.
- Visit the [Cardano Faucet](https://docs.cardano.org/cardano-testnets/tools/faucet).
- Request Test ADA (Preprod network).

---

### ⚙️ **6. Configure Your Environment Variables**

Copy `.env.example` to `.env` and fill with your own data:

```bash
cp .env.example .env
```

Example `.env` configuration:

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

---

### 📝 **6. Register Your Crew on Masumi**

Register your CrewAI agent via Masumi’s API:

```bash
curl -X POST 'http://localhost:3001/api/v1/registry/' \
-H 'accept: application/json' \
-H 'token: <your_api_key>' \
-H 'Content-Type: application/json' \
-d '{
    "network": "PREPROD",
    "paymentContractAddress": "<payment_contract_address>",
    "tags": ["tag1", "tag2"],
    "name": "Agent Name",
    "api_url": "https://api.example.com",
    "description": "Agent Description",
    "author": {
        "name": "Your Name",
        "contact": "your_email@example.com",
        "organization": "Your Organization"
    },
    "legal": {
        "privacy_policy": "Privacy Policy URL",
        "terms": "Terms URL",
        "other": "Other Legal Info URL"
    },
    "sellingWalletVkey": "<selling_wallet_vkey>",
    "capability": {
        "name": "Capability Name",
        "version": "1.0.0"
    },
    "requests_per_hour": "100",
    "pricing": [{"unit": "usdm", "quantity": "500000000"}]
}
```

Note your `agentIdentifier` from the response and update it in your `.env` file.

---

### 🔗 **7. Run & Verify Your API**

Start your FastAPI server with integrated Masumi payments:

```bash
uvicorn main:app --reload
```

Visit your server at:

```
http://localhost:8000/docs
```

Test with the provided endpoints:
- `/start_job` to initiate paid AI tasks
- `/status` to check job status and payment state
- `/availability` to check service availability

---

## 📂 **Project Structure**

```
.
├── .env.example
├── .gitignore
├── README.md
├── crew_definition.py
├── logging_config.py
├── main.py
├── requirements.txt
└── runtime.txt
```

---

## ✅ **Summary & Next Steps**

- [x] Defined your CrewAI Agents
- [x] Deployed the CrewAI FastAPI service
- [x] Installed and configured Masumi Payment Service
- [ ] **Next Step**: For production deployments, replace the in-memory store with a persistent database.

---

## 📚 **Useful Resources**

- [CrewAI Documentation](https://docs.crewai.com)
- [Masumi Documentation](https://docs.masumi.network)
- [FastAPI](https://fastapi.tiangolo.com)
- [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnets/tools/faucet)
