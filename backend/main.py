from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.openai_client import generate_workflow, ask_gpt  # asegúrate que ask_gpt está implementado
from backend.routes.chat_contextual import router as chat_router

import os
import requests

app = FastAPI(title="n8n Workflow Generator API")

# -----------------------------------
# 🌐 CORS Middleware (opcional)
# -----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto si tienes frontend en otro dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# 📥 Modelo de entrada
# -----------------------------------
class WorkflowRequest(BaseModel):
    instruction: str

# -----------------------------------
# 🚀 Generar workflow
# -----------------------------------
@app.post("/generate-workflow")
async def create_workflow(data: WorkflowRequest):
    result = generate_workflow(data.instruction)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"workflow_json": result}

@app.post("/chat")
async def chat_with_assistant(data: WorkflowRequest):
    try:
        respuesta = ask_gpt(data.instruction)
        return {"reply": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# -----------------------------------
# 📦 Descargar workflow generado
# -----------------------------------
@app.get("/download-workflow")
def download_workflow():
    file_path = "workflows/generated_workflow.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename="workflow_n8n.json"
    )

# -----------------------------------
# 🔄 Actualizar feed del foro n8n
# -----------------------------------
@app.get("/actualizar-feed")
def actualizar_feed(q: str = "n8n"):
    try:
        url = f"https://community.n8n.io/search.json?q={q}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        topics = res.json().get("topics", [])

        markdown = "\n".join(
            f"• [{t.get('title', 'Sin título')}]({f'https://community.n8n.io/t/{t.get('slug', '')}'})"
            for t in topics[:10]
        )

        os.makedirs("knowledge", exist_ok=True)
        with open("knowledge/feed_forum.md", "w", encoding="utf-8") as f:
            f.write(markdown)

        return {"message": "Feed actualizado", "topics": len(topics)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------
# 🔄 Actualizar issues GitHub
# -----------------------------------
@app.get("/actualizar-github")
def actualizar_github(q: str = "n8n"):
    try:
        url = f"https://api.github.com/search/issues?q=repo:n8n-io/n8n+{q}"
        headers = {"Accept": "application/vnd.github+json"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        items = res.json().get("items", [])

        markdown = "\n".join(
            f"• [{i.get('title', 'Sin título')}]({i.get('html_url', '')})"
            for i in items[:10]
        )

        os.makedirs("knowledge", exist_ok=True)
        with open("knowledge/feed_github.md", "w", encoding="utf-8") as f:
            f.write(markdown)

        return {"message": "Issues actualizados", "issues": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------
# 📁 Frontend
# -----------------------------------
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
