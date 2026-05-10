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

healthcheck/admission-service/
├── src/
│   ├── main.py                 # FastAPI Adapter
│   ├── lambda_function.py      # Finalized CRUD logic for Admissions
│   └── encoders.py             # Custom DecimalEncoder for JSON
├── tests/
│   ├── mock_events/
│   │   └── adt_event.json      # Mock API Gateway event with HL7 ADT body
│   └── test_parser.py          # Unit tests for PID segment extraction
├── requirements.txt            # Dependencies: python-hl7, boto3
├── Dockerfile                  # Containerization for Kubernetes deployment
├── .gitignore                  # Prevents __pycache__ and local env files
└── README.md                   # Documentation for the Admission Service
└── admisson-deployment.yaml    # K8s Manifest