# Contract Creator AI 🤖📄

A smart contract creation service that helps you generate legally-checked NDAs, Freelance, and Employment contracts using AI. Built with CrewAI and Masumi Network for secure, blockchain-based payments.

## What's This All About?

Ever spent hours drafting contracts or paid hefty legal fees for standard agreements? This tool helps you create professional, legally-sound contracts in minutes. It's like having a team of legal experts at your fingertips, but way cheaper and available 24/7.

### Features

- 📋 Three contract types:
  - NDAs (when you need to keep things hush-hush)
  - Freelance Agreements (for your next awesome contractor)
  - Employment Contracts (time to grow the team!)
- ⚖️ Legal compliance checks built-in
- 🔍 Risk assessment included
- 📝 Professional PDF generation
- 💸 Pay-per-use with crypto (ADA)

## Getting Started

### Prerequisites

You'll need:
- Python 3.10 or newer (but not 3.13+ yet)
- PostgreSQL 15
- Node.js v18+
- A Blockfrost API key (for Cardano blockchain stuff)

### Quick Setup

1. Clone and install dependencies:
```bash
git clone <your-repo-url>
cd contract-creator-ai
pip install -r requirements.txt
```

2. Set up your environment:
```bash
cp .env.example .env
```

Edit `.env` with your details:
```ini
# OpenAI - You need this for the AI magic
OPENAI_API_KEY=your_key_here

# Masumi Payment Service
PAYMENT_SERVICE_URL=http://localhost:3001/api/v1
PAYMENT_API_KEY=your_payment_key

# Agent Config
AGENT_IDENTIFIER=your_agent_id
PAYMENT_AMOUNT=10000000
PAYMENT_UNIT=lovelace
```

3. Start the services:
```bash
# Start Masumi Payment Service
docker compose up -d

# Start the Contract Creator API
python main.py api
```

## Using the Service

### Creating a Contract

Send a POST request to `/start_job` with your contract details:

```json
{
    "contract_type": "freelance",
    "company_name": "Cool Tech Inc",
    "company_address": "123 Startup St, SF",
    "party_name": "Jane Developer",
    "party_email": "jane@dev.com",
    "start_date": "2024-03-01",
    "hourly_rate": 150,
    "project_scope": "Build an awesome API"
}
```

### What Happens Behind the Scenes?

1. Our AI crew springs into action:
   - Contract Specialist drafts the initial agreement
   - Legal Expert checks compliance
   - Risk Analyst looks for potential issues
   - Final Reviewer does a thorough check
   - Document Formatter makes it look professional

2. You get back:
   - A job ID
   - Payment details (using ADA cryptocurrency)
   - A link to track progress

3. Once payment is confirmed:
   - Your contract is generated
   - You get a professional PDF
   - Everything is legally checked and ready to use

## API Endpoints

- `POST /start_job` - Start contract creation
- `GET /status` - Check contract status
- `GET /availability` - Check if service is running
- `GET /input_schema` - Get required input format
- `GET /health` - Service health check

## Development Setup

Want to hack on this? Here's how to set up your dev environment:

1. Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up PostgreSQL:
```bash
createdb contract_creator_dev
```

3. Run migrations:
```bash
npm run prisma:migrate
npm run prisma:seed
```

## Testing

```bash
pytest tests/
```

## Deployment

We use Docker for easy deployment. Just make sure you have your `.env` file set up correctly and run:

```bash
docker compose up -d
```

The service will be available at `http://localhost:8000`.

## Contributing

Got ideas? Found a bug? Want to help? Awesome! Here's how:

1. Fork it
2. Create your feature branch (`git checkout -b cool-new-feature`)
3. Commit your changes (`git commit -am 'Added something cool'`)
4. Push to the branch (`git push origin cool-new-feature`)
5. Create a Pull Request

## Troubleshooting

### Common Issues

**Q: The AI seems stuck**
A: Check your OpenAI API key and credits

**Q: Payment not confirming**
A: The Cardano network can be slow sometimes. Give it a few minutes.

**Q: Getting weird contract output**
A: Make sure all required fields are filled in correctly. The AI needs good input for good output!

## License

MIT - Go wild! Just don't blame us if something goes wrong.

## Support

Having trouble? Here's how to get help:

1. Check the issues on GitHub
2. Join our Discord (link coming soon)
3. Email support@yourcontractcreator.com

## Roadmap

Here's what's coming up:

- More contract types (Partnership agreements, SaaS contracts)
- Multi-language support
- Custom clause library
- Contract template marketplace

---

Built with ❤️ by developers for developers
