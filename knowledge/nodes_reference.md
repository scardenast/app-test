# Referencia de Nodos de n8n

Esta es una guía resumida de los nodos más comunes y cómo estructurarlos en un JSON válido para n8n.

---

## Webhook
- type: `n8n-nodes-base.webhook`
- parameters:
  - httpMethod: `"POST"` | `"GET"`
  - path: `"webhook-path"`
  - responseMode: `"onReceived"` o `"lastNode"`

Ejemplo:
```json
{
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "entrada",
    "responseMode": "onReceived"
  }
}

HTTP Request
type: n8n-nodes-base.httpRequest

parameters:

url: URL de destino

method: "GET" | "POST" | "PUT" | "DELETE"

Ejemplo:
```json
{
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "https://api.ejemplo.com/data",
    "method": "POST"
  }
}

Gmail
type: n8n-nodes-base.gmail

parameters:

resource: "message"

operation: "send"

to: correo destino

subject: asunto

message: cuerpo

Ejemplo:
```json
{
  "type": "n8n-nodes-base.gmail",
  "parameters": {
    "resource": "message",
    "operation": "send",
    "to": "usuario@ejemplo.com",
    "subject": "Confirmación",
    "message": "Gracias por tu mensaje"
  }
}

Google Sheets
type: n8n-nodes-base.googleSheets

parameters:

operation: "append" o "update"

sheetId: ID del documento

range: "A1:C1" (por ejemplo)

data: JSON de datos

Set
type: n8n-nodes-base.set

parameters:

values: secciones de tipo (string, number, boolean)

Ejemplo:

```json
{
  "type": "n8n-nodes-base.set",
  "parameters": {
    "values": {
      "string": [
        { "name": "mensaje", "value": "Hola Mundo" }
      ]
    }
  }
}

IF
type: n8n-nodes-base.if

parameters:

conditions: define condiciones con operadores

Ejemplo:
```json
{
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "string": [
        {
          "value1": "={{$json[\"estado\"]}}",
          "operation": "equal",
          "value2": "activo"
        }
      ]
    }
  }
}

Regla General
Cada nodo debe incluir:

"name": nombre visible

"type": tipo del nodo

"typeVersion": casi siempre 1

"position": coordenadas X/Y (ej. [200, 300])

Y todos los nodos deben estar dentro de la lista "nodes", más "connections" aparte.


