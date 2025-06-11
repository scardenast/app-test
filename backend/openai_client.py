import openai
import os

# Usa tu API Key desde variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_workflow(prompt_text: str):
    prompt = f"""You are an expert in building n8n workflows. A user wants the following automation:\n\n{prompt_text}\n\nGenerate the entire JSON workflow ready to import into n8n, and nothing else."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an n8n expert bot."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
