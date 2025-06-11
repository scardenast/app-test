from fastapi import FastAPI, Request
from backend.openai_client import generate_workflow

app = FastAPI()

@app.post("/generate-workflow")
async def create_workflow(request: Request):
    data = await request.json()
    user_input = data.get("instruction", "")
    result = generate_workflow(user_input)
    return {"workflow_json": result}
