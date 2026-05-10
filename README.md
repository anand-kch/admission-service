# Admission Service (HealthCheck)

A microservice dedicated to handling patient registration and admissions using HL7v2 messaging.

## Technology Stack
- **Language:** Python 3.14
- **Framework:** AWS Lambda (REST API)
- **Database:** Amazon DynamoDB
- **Messaging Standards:** HL7v2 (ADT Messages)

## Repository Structure
- `src/`: Contains `lambda_function.py` (CRUD logic).
- `requirements.txt`: Python dependencies (`python-hl7`, `boto3`).
- `tests/`: Local testing scripts for HL7 parsing.

## API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/admission` | Register a new patient (Ingest HL7 ADT) |
| GET | `/admission/{patient_id}` | Retrieve most recent admission record |
| PUT | `/admission/{patient_id}` | Update patient status or ID type |
| DELETE | `/admission/{patient_id}?ts={timestamp}` | Delete a specific admission entry |

## Local Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Test HL7 parsing: `python src/lambda_function.py` (with local event mock)

### Project Structure

```text
healthcheck-admission-service/
├── src/
│   ├── main.py                # FastAPI Wrapper (Adapter)
│   ├── lambda_function.py     # Core HL7 ADT Logic
│   └── encoders.py            # JSON Decimal handling
├── tests/
│   ├── mock_events/
│   │   └── adt_event.json     # Mock API Gateway event
│   └── test_parser.py         # HL7 Unit Tests
├── requirements.txt           # Dependencies (hl7, fastapi, etc.)
├── Dockerfile                 # Container configuration
├── .gitignore                 # Standard Python exclusions
├── admission-deployment.yaml  # Kubernetes Manifest
└── README.md                  # This file
