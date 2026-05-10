from fastapi import FastAPI, Request
from src.lambda_function import lambda_handler # Import your existing code
import uvicorn

app = FastAPI()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_lambda(request: Request, path: str):
    # Convert FastAPI request to the "event" format your Lambda expects
    body = await request.body()
    event = {
        "httpMethod": request.method,
        "path": f"/{path}",
        "pathParameters": {"patient_id": path.split('/')[-1]} if '/' in path else {},
        "body": body.decode('utf-8'),
        "queryStringParameters": dict(request.query_params)
    }
    
    # Call your existing function
    result = lambda_handler(event, None)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)