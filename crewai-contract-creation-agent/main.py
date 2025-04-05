import os
import uvicorn
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from masumi_crewai.config import Config
from masumi_crewai.payment import Payment, Amount
from crew_definition import ResearchCrew, ContractCreationCrew, ContractDetails, ContractType
from typing import Optional

# Load environment variables
load_dotenv(override=True)

# Retrieve API Keys and URLs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")

# Initialize FastAPI
app = FastAPI()

# ─────────────────────────────────────────────────────────────────────────────
# Temporary in-memory job store (DO NOT USE IN PRODUCTION)
# ─────────────────────────────────────────────────────────────────────────────
jobs = {}
payment_instances = {}

# ─────────────────────────────────────────────────────────────────────────────
# Initialize Masumi Payment Config
# ─────────────────────────────────────────────────────────────────────────────
config = Config(
    payment_service_url=PAYMENT_SERVICE_URL,
    payment_api_key=PAYMENT_API_KEY
)

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────────────────────────
class StartJobRequest(BaseModel):
    contract_type: ContractType
    company_name: str
    company_address: str
    party_name: str
    party_address: str
    party_email: str
    start_date: str
    end_date: Optional[str] = None
    salary: Optional[float] = None
    hourly_rate: Optional[float] = None
    project_scope: Optional[str] = None
    confidentiality_period: Optional[str] = None
    jurisdiction: str = "California, USA"
    additional_terms: Optional[str] = None

class ProvideInputRequest(BaseModel):
    job_id: str

# ─────────────────────────────────────────────────────────────────────────────
# CrewAI Task Execution
# ─────────────────────────────────────────────────────────────────────────────
async def execute_crew_task(data: StartJobRequest) -> dict:
    """ Execute a CrewAI task with Contract Creation Agents """
    crew = ContractCreationCrew()
    contract_details = ContractDetails(**data.dict())
    result = crew.process_contract(contract_details)
    return result

# ─────────────────────────────────────────────────────────────────────────────
# 1) Start Job (MIP-003: /start_job)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/start_job")
async def start_job(data: StartJobRequest):
    """ Initiates a job and creates a payment request """
    job_id = str(uuid.uuid4())
    agent_identifier = os.getenv("AGENT_IDENTIFIER")

    # Define payment amounts
    payment_amount = os.getenv("PAYMENT_AMOUNT", "10000000")  # Default 10 ADA
    payment_unit = os.getenv("PAYMENT_UNIT", "lovelace") # Default lovelace
    amounts = [Amount(amount=payment_amount, unit=payment_unit)]
    
    # Create a payment request using Masumi
    payment = Payment(
        agent_identifier=agent_identifier,
        amounts=amounts,
        config=config,
        identifier_from_purchaser="default_purchaser_id" # Best practice: Replace with a random identifier for each purchase
    )
    
    payment_request = await payment.create_payment_request()
    payment_id = payment_request["data"]["blockchainIdentifier"]
    payment.payment_ids.add(payment_id)

    # Store job info (Awaiting payment)
    jobs[job_id] = {
        "status": "awaiting_payment",
        "payment_status": "pending",
        "payment_id": payment_id,
        "input_data": data.dict(),
        "result": None
    }

    async def payment_callback(payment_id: str):
        await handle_payment_status(job_id, payment_id)

    # Start monitoring the payment status
    payment_instances[job_id] = payment
    await payment.start_status_monitoring(payment_callback)

    # Return the response in the required format
    return {
        "status": "success",
        "job_id": job_id,
        "blockchainIdentifier": payment_request["data"]["blockchainIdentifier"],
        "submitResultTime": payment_request["data"]["submitResultTime"],
        "unlockTime": payment_request["data"]["unlockTime"],
        "externalDisputeUnlockTime": payment_request["data"]["externalDisputeUnlockTime"],
        "agentIdentifier": agent_identifier,
        "sellerVkey": os.getenv("SELLER_VKEY"),
        "identifierFromPurchaser": "example_identifier",
        "amounts": amounts
    }

# ─────────────────────────────────────────────────────────────────────────────
# 2) Process Payment and Execute AI Task
# ─────────────────────────────────────────────────────────────────────────────
async def handle_payment_status(job_id: str, payment_id: str) -> None:
    """ Executes CrewAI task after payment confirmation """
    print(f"Payment {payment_id} completed for job {job_id}, executing task...")
    
    # Update job status to running
    jobs[job_id]["status"] = "running"
    
    # Execute the AI task
    result = await execute_crew_task(jobs[job_id]["input_data"])
    print(f"Crew task completed for job {job_id}")

    # Convert result content to string if it's not already
    result_str = str(result["content"])
    
    # Mark payment as completed on Masumi
    # Use a shorter string for the result hash
    result_hash = result_str[:64] if len(result_str) >= 64 else result_str
    await payment_instances[job_id].complete_payment(payment_id, result_hash)
    print(f"Payment completed for job {job_id}")

    # Update job status
    jobs[job_id]["status"] = "completed"
    jobs[job_id]["payment_status"] = "completed"
    jobs[job_id]["result"] = result["content"]
    jobs[job_id]["pdf_path"] = result["pdf_path"]

    # Stop monitoring payment status
    if job_id in payment_instances:
        payment_instances[job_id].stop_status_monitoring()
        del payment_instances[job_id]
    
    # Still stop monitoring to prevent repeated failures
    if job_id in payment_instances:
        payment_instances[job_id].stop_status_monitoring()
        del payment_instances[job_id]

# ─────────────────────────────────────────────────────────────────────────────
# 3) Check Job and Payment Status (MIP-003: /status)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/status")
async def get_status(job_id: str):
    """ Retrieves the current status of a specific job """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    # Check latest payment status if payment instance exists
    if job_id in payment_instances:
        status = await payment_instances[job_id].check_payment_status()
        job["payment_status"] = status.get("data", {}).get("status")

    return {
        "job_id": job_id,
        "status": job["status"],
        "payment_status": job["payment_status"],
        "result": job.get("result"),
        "pdf_path": job.get("pdf_path")
    }

# ─────────────────────────────────────────────────────────────────────────────
# 4) Check Server Availability (MIP-003: /availability)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/availability")
async def check_availability():
    """ Checks if the server is operational """
    return {
        "status": "available",
        "message": "The server is running smoothly."
    }

# ─────────────────────────────────────────────────────────────────────────────
# 5) Retrieve Input Schema (MIP-003: /input_schema)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/input_schema")
async def input_schema():
    """
    Returns the expected input schema for the /start_job endpoint.
    """
    return {
        "input_schema": {
            "contract_type": {
                "type": "string",
                "enum": ["nda", "freelance", "employment"],
                "required": True
            },
            "company_name": {
                "type": "string",
                "required": True
            },
            "company_address": {
                "type": "string",
                "required": True
            },
            "party_name": {
                "type": "string",
                "required": True
            },
            "party_address": {
                "type": "string",
                "required": True
            },
            "party_email": {
                "type": "string",
                "required": True
            },
            "start_date": {
                "type": "string",
                "required": True
            },
            "end_date": {
                "type": "string",
                "required": False
            },
            "salary": {
                "type": "number",
                "required": False,
                "description": "Required for employment contracts"
            },
            "hourly_rate": {
                "type": "number",
                "required": False,
                "description": "Required for freelance contracts"
            },
            "project_scope": {
                "type": "string",
                "required": False,
                "description": "Required for freelance contracts"
            },
            "confidentiality_period": {
                "type": "string",
                "required": False,
                "description": "Required for NDAs"
            },
            "jurisdiction": {
                "type": "string",
                "required": False,
                "default": "California, USA"
            },
            "additional_terms": {
                "type": "string",
                "required": False
            }
        }
    }

# ─────────────────────────────────────────────────────────────────────────────
# 6) Health Check
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """
    Returns the health of the server.
    """
    return {
        "status": "healthy"
    }

# ─────────────────────────────────────────────────────────────────────────────
# Main Logic if Called as a Script
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("Running CrewAI as standalone script is not supported when using payments.")
    print("Start the API using `python main.py api` instead.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        print("Starting FastAPI server with Masumi integration...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        main()
