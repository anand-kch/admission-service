import hl7
import boto3
import json
from decimal import Decimal
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Helper to handle DynamoDB Decimals for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    # Initialize Table (Standardized to lowercase)
    table = boto3.resource('dynamodb').Table('HealthCheck_Admissions')
    
    method = event.get('httpMethod')
    path_params = event.get('pathParameters', {})
    
    # Extract patient_id from the URL path /admission/{patient_id}
    p_id_from_path = path_params.get('patient_id') if path_params else None

    # --- 1. CREATE (POST /admission) ---
    if method == 'POST':
        try:
            # Prepare HL7 message (handle newline to carriage return)
            raw_hl7 = event.get('body', '').replace('\n', '\r')
            h = hl7.parse(raw_hl7)
            pid_seg = h.segment('PID')
            
            # Extract clean ID and ID Type (MRN) from sub-components
            # pid_seg[3][0] is the first ID repeat
            # [0] is the ID number, [4] is the ID type (MRN)
            patient_id_field = pid_seg[3][0]
            clean_id = str(patient_id_field[0])
            
            try:
                id_type = str(patient_id_field[4]) if len(patient_id_field) > 4 else "ADT"
            except (IndexError, AttributeError):
                id_type = "ADT"
            
            item = {
                'patient_id': clean_id,
                'patient_id_type': id_type,
                'timestamp': datetime.utcnow().isoformat(),
                'FullName': f"{pid_seg[5][0][1]} {pid_seg[5][0][0]}",
                'MessageType': 'ADT',
                'Status': 'Admitted',
                'RawMessage': raw_hl7
            }
            
            table.put_item(Item=item)
            return {
                "statusCode": 201, 
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Success", "id": clean_id, "type": id_type})
            }
        except Exception as e:
            return {
                "statusCode": 400, 
                "body": json.dumps({"error": f"HL7 Parsing/DB Error: {str(e)}"})
            }

    # --- 2. READ (GET /admission/{patient_id}) ---
    elif method == 'GET':
        if not p_id_from_path:
            return {"statusCode": 400, "body": "Missing patient_id in path"}
            
        try:
            # Querying by patient_id, sorting by latest timestamp
            response = table.query(
                KeyConditionExpression=Key('patient_id').eq(p_id_from_path),
                ScanIndexForward=False,
                Limit=1
            )
            
            if response.get('Items'):
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(response['Items'][0], cls=DecimalEncoder)
                }
            return {"statusCode": 404, "body": json.dumps({"message": "Patient not found"})}
        except Exception as e:
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    # --- 3. UPDATE (PUT /admission/{patient_id}) ---
    elif method == 'PUT':
        if not p_id_from_path:
            return {"statusCode": 400, "body": "Missing patient_id"}
        
        try:
            body = json.loads(event.get('body', '{}'))
            # Get the new values from the request body
            new_type = body.get('patient_id_type')
            new_status = body.get('status')
            
            # Find the latest record to get its timestamp
            latest = table.query(
                KeyConditionExpression=Key('patient_id').eq(p_id_from_path),
                ScanIndexForward=False, Limit=1
            )
            
            if not latest['Items']:
                return {"statusCode": 404, "body": "Record not found"}
            
            ts = latest['Items'][0]['timestamp']
            
            # Update multiple attributes
            table.update_item(
                Key={'patient_id': p_id_from_path, 'timestamp': ts},
                UpdateExpression="set patient_id_type = :t, #s = :s",
                ExpressionAttributeNames={'#s': 'Status'},
                ExpressionAttributeValues={
                    ':t': new_type if new_type else latest['Items'][0].get('patient_id_type', 'MRN'),
                    ':s': new_status if new_status else latest['Items'][0].get('Status', 'Admitted')
                }
            )
            return {"statusCode": 200, "body": json.dumps({"message": "Update Successful"})}
        except Exception as e:
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

# --- 4. DELETE (DELETE /admission/{patient_id}) ---
    elif method == 'DELETE':
        # Safely handle NoneType for queryStringParameters
        query_params = event.get('queryStringParameters') or {}
        ts = query_params.get('ts')
        
        if p_id_from_path and ts:
            table.delete_item(Key={'patient_id': p_id_from_path, 'timestamp': ts})
            return {
                "statusCode": 200, 
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Record deleted"})
            }
        
        return {
            "statusCode": 400, 
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Provide patient_id in path and 'ts' in query string"})
        }
    return {"statusCode": 405, "body": "Method Not Allowed"}