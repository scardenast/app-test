from backend.supabase_client import insert_session
import uuid


prueba = insert_session({
    "id": str(uuid.uuid4()),
    "instruction": "Quiero un workflow que reciba datos por webhook y los envíe a Telegram",
    "workflow_json": '{"nodes": [...]}',
    "improvement_suggestions": "Considera usar nodos de control de errores",
    "source_forum": None,
    "source_github": None
})


print(prueba)
