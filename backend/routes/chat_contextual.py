from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from backend.openai_client import ask_gpt, client  # ✅ Import correcto

router = APIRouter()

class Message(BaseModel):
    role: str  # "user" o "assistant"
    content: str

class ChatRequest(BaseModel):
    history: List[Message]

@router.post("/asistente-contextual")
async def chat_contextual(data: ChatRequest):
    try:
        # Construcción del historial de mensajes con mensaje de sistema inicial
        messages = [{
            "role": "system",
            "content": (
                "Eres un asistente experto en automatización con n8n. Ayudas paso a paso, entiendes el contexto, "
                "detectas si el usuario está listo para generar un workflow y lo guías antes de generar el JSON."
            )
        }] + [msg.dict() for msg in data.history]

        # Llamada a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip()

        # Heurística para detectar intención de generación
        ready_phrases = [
            "generar el workflow", "crear el flujo", "listo para generar",
            "haz el json", "puedes hacer el workflow", "exporta el flujo", "genera el flujo"
        ]
        ready_to_generate = any(phrase in reply.lower() for phrase in ready_phrases)

        return {"reply": reply, "ready_to_generate": ready_to_generate}

    except Exception as e:
        return {"reply": f"❌ Error en asistente contextual: {str(e)}", "ready_to_generate": False}
