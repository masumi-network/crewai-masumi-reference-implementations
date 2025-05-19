"""
CrewAI Invoice generator Agent
"""
import os
import boto3
import botocore
import uuid
import uvicorn
import tracebackA
from crew_definition import Invoice_Agents
from tools.export import export_invoice_to_pdf  
from dotenv import load_dotenv
from datetime import datetime, timezone
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from masumi.config import Config
from masumi.payment import Payment, Amount
from logging_config import setup_logging

logger = setup_logging()

# Load environment variables
load_dotenv(override=True)

# Retrieve API Keys and URLs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")

logger.info("Starting application with configuration:")
logger.info(f"PAYMENT_SERVICE_URL: {PAYMENT_SERVICE_URL}")

# Initialize FastAPI
app = FastAPI(
    title="API following the Masumi API Standard",
    description="API for running Agentic Services tasks with Masumi payment integration",
    version="1.0.0"
)

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
    
    """
    sender: str
    sender_address: str
    sender_country: str
    sender_contact: str
    sender_tax_number:str
    recipient: str
    recipient_address: str
    recipient_country: str
    recipient_contact: str
    recipient_tax_number:str
    due_date: str
    transactions:str
    logo: str
    payment_instructions:str
    invoice_notes:str
    extra_charges: str
    taxes: str
    transaction_notes:str
    currency:str
"""
    identifier_from_purchaser: str
    input_data: dict[str, str]
    class Config:
        json_schema_extra = {
            "example": {
                "identifier_from_purchaser": "example_purchaser_123",
                "input_data": {
                    "invoice_info": "Generate an invoice from SENDER: John Doe, 123 Example Street, Switzerland, JohnDoe@Email.com, Tax number: 12345678 to RECIPIENT: Jane Doe, 456 Example Street, Switzerland, JaneDoe@Email.com, Tax number:5678910. Due on 1/1/15 for 2 ITEM1 for 200 euro each and 1 ITEM2 for 100 euro. Company logo: filepath/to/local/image. To by payed to IBAN:1234567. SAMPLE INVOICE NOTE, Extra charges: Late fee 10 euro. 10% VAT currency is Euro."
                }
            }
        }

class ProvideInputRequest(BaseModel):
    job_id: str
    """
    sender: str
    sender_address: str
    sender_country: str
    sender_contact: str
    sender_tax_number:str
    recipient: str
    recipient_address: str
    recipient_country: str
    recipient_contact: str
    recipient_tax_number:str
    due_date: str
    transactions:str
    logo: str
    payment_instructions:str
    invoice_notes:str
    extra_charges: str
    taxes: str
    transaction_notes:str
    currency:str
    """
# ─────────────────────────────────────────────────────────────────────────────
# CrewAI Task Execution
# ─────────────────────────────────────────────────────────────────────────────

async def execute_crew_task(input_data:str) -> str:
    """
    invoice_dictionary = {
        "sender": str(data.sender),
        "sender_address": str(data.sender_address),
        "sender_country": str(data.sender_country),
        "sender_contact": str(data.sender_contact),
        "sender_tax_number": str(data.sender_tax_number),
        "recipient": str(data.recipient),
        "recipient_address": str(data.recipient_address),
        "recipient_country": str(data.recipient_country),
        "recipient_contact": str(data.recipient_contact),
        "recipient_tax_number": str(data.recipient_tax_number),
        "due_date": str(data.due_date),
        "transactions": str(data.transactions),
        "logo": str(data.logo),
        "payment_instructions": str(data.payment_instructions),
        "invoice_notes": str(data.invoice_notes),
        "extra_charges": str(data.extra_charges),
        "taxes": str(data.taxes),
        "transaction_notes": str(data.transaction_notes),
        "currency": str(data.currency)
    }

    invoice_info = f
    Sender: {invoice_dictionary["sender"]}
    Sender Address: {invoice_dictionary["sender_address"]}
    Sender Country: {invoice_dictionary["sender_country"]}
    Sender Contact: {invoice_dictionary["sender_contact"]}
    Sender tax number: {invoice_dictionary["sender_tax_number"]}
    
    Recipient: {invoice_dictionary["recipient"]}
    Recipient Address: {invoice_dictionary["recipient_address"]}
    Recipient Country: {invoice_dictionary["recipient_country"]}
    Recipient Contact: {invoice_dictionary["recipient_contact"]}
    Recpient tax number: {invoice_dictionary["recipient_tax_number"]}
 
    Due Date: {invoice_dictionary["due_date"]}
    
    Transactions: {invoice_dictionary["transactions"]}
    
    Logo: {invoice_dictionary["logo"]}
    Payment Instructions: {invoice_dictionary["payment_instructions"]}
    Invoice Notes: {invoice_dictionary["invoice_notes"]}

    Extra Charges: {invoice_dictionary["extra_charges"]}

    Taxes: {invoice_dictionary["taxes"]}

    Transaction_notes: {invoice_dictionary["transaction_notes"]}

    Currency: {invoice_dictionary["currency"]}
    """
    
    #legal_info = search_invoice_regulations(data.sender_country, data.recipient_country)
    #cleaning_crew = Cleaning_Agents(legal_info['content'])
    #legal_info = cleaning_crew.clean_Data()
    invoice_crew = Invoice_Agents(input_data, "None",logger = logger)
    result,analysis = invoice_crew.run_analysis()
    InvoicePDF = export_invoice_to_pdf(result)
    # Initialize extra_info in the result
     # Initialize an empty list for extra information

    
    
    #logger.info(f"Starting CrewAI task with input: {input_data}")
    # Step 2: The new session validates your request and directs it to your Space's specified endpoint using the AWS SDK.
    session = boto3.session.Session()
    client = session.client('s3',
                            endpoint_url = os.getenv('SPACES_ENDPOINT'), # Find your endpoint in the control panel, under Settings. Prepend "https://".
                            config=botocore.config.Config(s3={'addressing_style': 'virtual'}), # Configures to use subdomain/virtual calling format.
                            region_name=os.getenv('SPACES_REGION'), # Use the region in your endpoint.
                            aws_access_key_id= os.getenv('SPACES_KEY'), # Access key pair. You can create access key pairs using the control panel or API.
                            aws_secret_access_key=os.getenv('SPACES_SECRET')) # Secret access key defined through an environment variable.
    # Step 3: Call the put_object command and specify the file to upload.
    with open(InvoicePDF, 'rb') as invoice_file:  # Open the PDF file in binary mode
        client.put_object(
            Bucket='invoice-agent-bucket',  # The path to the directory you want to upload the object to, starting with your Space name.
            Key=f'invoices/{datetime.now().year}/{datetime.now().month}/{InvoicePDF}',  # Object key, referenced whenever you want to access this file later.
            Body=invoice_file,  # The object's contents.
            ACL='public-read',  # Defines Access-control List (ACL) permissions, such as private or public.
            Metadata={  # Defines metadata tags.
                'x-amz-meta-my-key': InvoicePDF
            }
        )
  
    logger.info("CrewAI task completed successfully")

    return InvoicePDF,analysis
    
# ─────────────────────────────────────────────────────────────────────────────
# 1) Start Job (MIP-003: /start_job)
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/start_job")
async def start_job(data: StartJobRequest):
    """
    Initiates a job with specific input data.
    Fulfills MIP-003 /start_job endpoint.
    """
    try:
        job_id = str(uuid.uuid4())
        agent_identifier = os.getenv("AGENT_IDENTIFIER")

        # Construct the input text from the invoice information
        # Log the input text (truncate if too long)
        invoice_info  = data.input_data["invoice_info"]
        truncated_input = invoice_info[:100] + "..." if len(invoice_info) > 100 else invoice_info
        logger.info(f"Received job request with input: '{truncated_input}'")
        logger.info(f"Starting job {job_id} with agent {agent_identifier}")

        payment_amount = os.getenv("PAYMENT_AMOUNT", "10000000")  # Default 10 ADA
        payment_unit = os.getenv("PAYMENT_UNIT", "lovelace")  # Default lovelace

        amounts = [Amount(amount=payment_amount, unit=payment_unit)]
        logger.info(f"Using payment amount: {payment_amount} {payment_unit}")

        # Create a payment request using Masumi
        payment = Payment(
            agent_identifier=agent_identifier,
            config=config,
            identifier_from_purchaser=data.identifier_from_purchaser,
            input_data = data.input_data
            # Include any other necessary parameters
        )

        logger.info("Creating payment request...")
        payment_request = await payment.create_payment_request()
        payment_id = payment_request["data"]["blockchainIdentifier"]
        payment.payment_ids.add(payment_id)
        logger.info(f"Created payment request with ID: {payment_id}")

        jobs[job_id] = {
            "status": "awaiting payment",
            "payment_status":"pending",
            "payment_id": payment_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "input_data": data.input_data,
            "result": None,
            "identifier_from_purchaser": data.identifier_from_purchaser
        }

        async def payment_callback(payment_id: str):
            await handle_payment_status(job_id, payment_id)

        payment_instances[job_id] = payment
        logger.info(f"Starting payment status monitoring for job {job_id}")
        await payment.start_status_monitoring(payment_callback)

        return {
            "status": "success",
            "job_id": job_id,
            "blockchainIdentifier": payment_request["data"]["blockchainIdentifier"],
            "submitResultTime": payment_request["data"]["submitResultTime"],
            "unlockTime": payment_request["data"]["unlockTime"],
            "externalDisputeUnlockTime": payment_request["data"]["externalDisputeUnlockTime"],
            "agentIdentifier": agent_identifier,
            "sellerVkey": os.getenv("SELLER_VKEY"),
            "identifierFromPurchaser": data.identifier_from_purchaser,
            "amounts": amounts,
            "input_hash": payment.input_hash
        }
    except KeyError as e:
        logger.error(f"Missing required field in request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Bad Request: If input_data or identifier_from_purchaser is missing, invalid, or does not adhere to the schema."
        )
    except Exception as e:
        logger.error(f"Error in start_job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Input_data or identifier_from_purchaser is missing, invalid, or does not adhere to the schema."
        )
# ─────────────────────────────────────────────────────────────────────────────
# 2) Process Payment and Execute AI Task
# ─────────────────────────────────────────────────────────────────────────────
async def handle_payment_status(job_id: str, payment_id: str) -> None:
    try:
        logger.info(f"Payment {payment_id} completed for job {job_id}, executing task...")
    
        jobs[job_id]["status"] = "running"
        logger.info(f"Input data: {jobs[job_id]["input_data"]}")

        # Execute the AI task   
        result,legal,invoice_dictionary = await execute_crew_task(jobs[job_id]["input_data"])

        logger.info(f"Crew task completed for job {job_id}")
        # Convert result to string if it's not already
        result_str = str(result)
        # Mark payment as completed on Masumi
        # Use a shorter string for the result hash
        result_hash = result_str[:64] if len(result_str) >= 64 else result_str
        await payment_instances[job_id].complete_payment(payment_id, result_hash)
        logger.info(f"Payment completed for job {job_id}")

        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["payment_status"] = "completed"
        jobs[job_id]["result"] = result
        jobs[job_id]["analysis"] = legal
        jobs[job_id]["invoice_info"] = invoice_dictionary

        # Stop monitoring payment status
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]
    except Exception as e:
        logger.error(f"Error processing payment {payment_id} for job {job_id}: {str(e)}", exc_info=True)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        
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
    logger.info(f"Checking status for job {job_id}")
    if job_id not in jobs:
        logger.warning(f"Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    # Check latest payment status if payment instance exists
    if job_id in payment_instances:
        try:
            status = await payment_instances[job_id].check_payment_status()
            job["payment_status"] = status.get("data", {}).get("status")
            logger.info(f"Updated payment status for job {job_id}: {job['payment_status']}")
        except ValueError as e:
            logger.warning(f"Error checking payment status: {str(e)}")
            job["payment_status"] = "unknown"
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}", exc_info=True)
            job["payment_status"] = "error"

    return {
        "job_id": job_id,
        "status": job["status"],
        "payment_status": job["payment_status"],
        "result": job.get("result")
    }

# ─────────────────────────────────────────────────────────────────────────────
# 4) Check Server Availability (MIP-003: /availability)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/availability")
async def check_availability():
    """ Checks if the server is operational """
    return {
        "status": "available",
        "agentIdentifier": os.getenv("AGENT_IDENTIFIER"),
        "message": "The server is running smoothly."
    }

# ─────────────────────────────────────────────────────────────────────────────
# 5) Retrieve Input Schema (MIP-003: /input_schema)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/input_schema")
async def input_schema():
    """
    Returns the expected input schema for the /start_job endpoint.
    Fulfills MIP-003 /input_schema endpoint.
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
# 7) Provide Input (MIP-003: /provide_input)
# ─────────────────────────────────────────────────────────────────────────────
"""
@app.post("/provide_input")
async def provide_input(request_body: ProvideInputRequest):
    
    Allows users to send additional input.
    Fulfills MIP-003 /provide_input endpoint.
    
    In this example we can add any additional info to the invoice, or fill in any required information.
    

    job_id = request_body.job_id

    if job_id not in jobs:
        return {"status": "error", "message": "Job not found"}

    job = jobs[job_id]

    input_data = request_body.model_dump()

    # Iterate over the input data and update the invoice_dictionary
    for key, value in input_data.items():
        if value not in [None, "string"]:  # Check if value is not None and not "string"
            job["invoice_info"][key] = value
       
    # Update the Invoice_Agents crew with the modified invoice_info
    invoice_info = f
    Sender: {job["invoice_info"]["sender"]}
    Sender Address: {job["invoice_info"]["sender_address"]}
    Sender Country: {job["invoice_info"]["sender_country"]}
    Sender Contact: {job["invoice_info"]["sender_contact"]}
    Sender tax number: {job["invoice_info"]["sender_tax_number"]}
    
    Recipient: {job["invoice_info"]["recipient"]}
    Recipient Address: {job["invoice_info"]["recipient_address"]}
    Recipient Country: {job["invoice_info"]["recipient_country"]}
    Recipient Contact: {job["invoice_info"]["recipient_contact"]}
    Recpient tax number: {job["invoice_info"]["recipient_tax_number"]}

    Due Date: {job["invoice_info"]["due_date"]}
    
    Transactions: {job["invoice_info"]["transactions"]}
        
    Logo: {job["invoice_info"]["logo"]}
    Payment Instructions: {job["invoice_info"]["payment_instructions"]}
    Invoice Notes: {job["invoice_info"]["invoice_notes"]}

    Extra Charges: {job["invoice_info"]["extra_charges"]}

    Taxes: {job["invoice_info"]["taxes"]}

    Transaction_notes: {job["invoice_info"]["transaction_notes"]}

    Currency: {job["invoice_info"]["currency"]}

    
    invoice_crew = Invoice_Agents(invoice_info, job["legal_analysis"])

    result, legal = invoice_crew.run_analysis()  # Re-run analysis with updated info

    InvoicePDF = export_invoice_to_pdf(result)
    
    #Update job with new result
    job["result"] = InvoicePDF
    job["status"] = "Success"



    return {
        "status": "awaiting input",
        "job_id": job_id,
        "current_pdf": InvoicePDF,
        "legal_analysis":legal
    }
"""
# ─────────────────────────────────────────────────────────────────────────────
# Main logic if called as a script
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY is missing. Please check your .env file.")
        return
    """
    invoice_text = str(input("Enter invoice information:\n"))

    if not invoice_text.strip():
        print("Invoice data is required.")
        return
        
    """
    try:
        sample_invoice = {
    "sender_info": [
        "Franz Shih.",
        "198 New Seskin Court", 
        "Whitestown Way"
    ],
    "sender_country": "Ireland",
    "recipient_info": [
        "utxo AG",
        "Döttingerstrasse 21",
        "CH5303 Würenlingen"
    ],
    "recipient_country": "Switzerland",
    "due_date": "02/05/25",
    "transactions": [
        "Customer service",
        "NMKR agent",
        "Masumi Payment"
    ],
    "quantities": [
        "1""""""",  # Assuming each transaction is for one unit
        "2",
        "1"
    ],
    "unit_prices": [
        "30.00",
        "40.00",
        "25.00"
    ],
    "unit_totals": [
        "30.00",
        "40.00",
        "25.00"
    ],
    "total": "95.00",  # Total of all transactions
    "logo": "C:/Users/hungl/Downloads/logo.png",
    "reciever_VAT": "CH VAT CHE494.509.135 MWST",
    "payment_notes":"IBAN: CH30 0857 3102 5022 0181 4"
      # Placeholder for legal analysis
}
        # Create invoice processing agents
        """
        agents = Invoice_Agents(invoice_text)
        
        # Run analysis
        results = agents.run_analysis()

        print(results['legal'])
        
        # Check for errors
        print("Here is your Invoice PDF: {export_path}")
        if "error" in results:
            print(f"Error processing invoice: {results['error']}")
        else:
            print("Invoice processed successfully!")
            """   
            # Export to PDF
        export_path = export_invoice_to_pdf(sample_invoice)
        print(f"Invoice exported to PDF: {export_path}")
  
    except Exception as e:
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        print(f"Error processing invoice: {error_msg}")
        print("Error details:")
        print(stack_trace)
        logger.error(f"Error processing invoice: {e}", exc_info=True)
        

if __name__ == "__main__":
    import sys

    # If 'api' argument is passed, start the FastAPI server
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        print("Starting FastAPI server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        main()
