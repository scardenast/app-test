import os
import uuid
import json
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Accept-Charset": "utf-8"
}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def insert_session(payload: dict):
    url = f"{SUPABASE_URL}/rest/v1/sessions"
    try:
        # Asegurarse que todo el contenido es UTF-8 serializable
        encoded_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        response = httpx.post(url, headers=headers, content=encoded_payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("❌ Error al insertar en Supabase:", e)
        return {"error": str(e)}

def leer_archivo(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def ask_gpt(mensaje: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente experto en automatización usando n8n. "
                        "Responde con claridad, ejemplos y si es necesario, explica cómo resolver problemas comunes. "
                        "Evita responder si no sabes con certeza."
                    )
                },
                {
                    "role": "user",
                    "content": mensaje
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"No tengo una respuesta clara aún. ({str(e)})"


def suggest_improvement(json_workflow: str) -> str:
    prompt = f"""
Este es un workflow de n8n generado por IA:

```json
{json_workflow}
```

Por favor, sugiere mejoras técnicas u optimizaciones que podrían hacerse.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Actúa como un auditor experto en workflows de n8n. Devuelve recomendaciones claras y concisas."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"No se pudo generar sugerencias: {str(e)}"

def generate_workflow(prompt_text: str):
    forum_knowledge = leer_archivo("knowledge/feed_forum.md")
    github_knowledge = leer_archivo("knowledge/feed_github.md")
    nodes_reference = leer_archivo("knowledge/nodes_reference.md")

    prompt = f"""
Eres un generador profesional de workflows de n8n. Tu trabajo es preciso, técnico y limpio. A continuación, tienes el contexto:

### Referencia de nodos válidos de n8n:
{nodes_reference}

### Temas recientes del foro de n8n:
{forum_knowledge}

### Issues recientes del repositorio oficial de GitHub:
{github_knowledge}

Ahora, genera un workflow de n8n que resuelva la siguiente necesidad del usuario:

{prompt_text}

⚠️ Solo devuelve el JSON válido del workflow, sin explicaciones, sin comentarios, sin etiquetas markdown.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un experto en creación de workflows en n8n. Devuelve siempre JSON válido."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```json"):
            content = content.replace("```json", "").strip()
        if content.endswith("```"):
            content = content[:-3].strip()

        # Validar formato JSON
        try:
            json.loads(content)
        except json.JSONDecodeError:
            return {"error": "La respuesta de OpenAI no es un JSON válido"}

        # Guardar archivo
        os.makedirs("workflows", exist_ok=True)
        file_path = "workflows/generated_workflow.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Generar sugerencias de mejora
        improvement = suggest_improvement(content)

        # Insertar en Supabase
        insert_session({
            "id": str(uuid.uuid4()),
            "instruction": prompt_text,
            "workflow_json": content,
            "improvement_suggestions": improvement,
            "source_forum": forum_knowledge[:500],
            "source_github": github_knowledge[:500],
            "user_id": None
        })

        return {
            "message": "Workflow generado correctamente",
            "file_path": file_path,
            "content": content,
            "improvement": improvement
        }

    except Exception as e:
        return {"error": str(e)}
