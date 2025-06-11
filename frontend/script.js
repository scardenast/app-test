let conversationHistory = [];

async function askAssistant() {
  const input = document.getElementById("instruction");
  const chatBox = document.getElementById("chat");
  const instruction = input.value.trim();
  if (!instruction) return;

  appendMessage("user", instruction);
  input.value = "";
  appendMessage("system", "🤖 Pensando...");

  conversationHistory.push({ role: "user", content: instruction });

  try {
    const res = await fetch("/chat", {  // ✅ Corregido el endpoint
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ instruction })
    });

    const data = await res.json();
    chatBox.lastChild.remove();

    const reply = data.reply || "🤖 No tengo una respuesta clara aún.";
    appendMessage("assistant", reply);
    conversationHistory.push({ role: "assistant", content: reply });

    // Habilitar botón si hay intención de generar flujo
    if (reply.includes("workflow") || reply.includes("automático")) {
      document.getElementById("generateBtn").disabled = false;
      document.getElementById("generateBtn").style.opacity = 1;
    }
  } catch (err) {
    chatBox.lastChild.remove();
    appendMessage("assistant", `❌ Error: ${err.message}`);
  }
}

async function generateWorkflow() {
  const chatBox = document.getElementById("chat");
  const link = document.getElementById("downloadLink");
  const copyBtn = document.getElementById("copyBtn");

  appendMessage("system", "⏳ Generando workflow...");

  try {
    const response = await fetch("/generate-workflow", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ instruction: conversationHistory.map(x => x.content).join("\n") })
    });

    const data = await response.json();
    chatBox.lastChild.remove();

    if (data.workflow_json?.content) {
      const rawJSON = JSON.parse(data.workflow_json.content);
      const formatted = syntaxHighlight(rawJSON);

      appendMessage("assistant", `
        <div><strong>✅ Workflow generado:</strong></div>
        <pre class="json">${formatted}</pre>
      `);

      if (data.workflow_json.improvement) {
        appendMessage("assistant", `💡 <em>${data.workflow_json.improvement}</em>`);
      }

      link.href = "/download-workflow";
      link.style.display = "inline-block";
      copyBtn.style.display = "inline-block";
    } else {
      appendMessage("assistant", `❌ No se recibió JSON válido.`);
    }
  } catch (err) {
    chatBox.lastChild.remove();
    appendMessage("assistant", `❌ Error: ${err.message}`);
  }
}

function appendMessage(sender, content) {
  const chatBox = document.getElementById("chat");
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  msg.innerHTML = `<div class="bubble">${content}</div>`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function syntaxHighlight(json) {
  if (typeof json !== "string") {
    json = JSON.stringify(json, null, 2);
  }
  json = json.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return json.replace(
    /(\"(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\\"])*\"(?:\s*:)?|\b(true|false|null)\b|\b\d+\b)/g,
    match => {
      let cls = "number";
      if (/^\"/.test(match)) {
        cls = /:$/.test(match) ? "key" : "string";
      } else if (/true|false/.test(match)) {
        cls = "boolean";
      } else if (/null/.test(match)) {
        cls = "null";
      }
      return `<span class="${cls}">${match}</span>`;
    }
  );
}

function copiarJSON() {
  const jsonBlocks = document.querySelectorAll(".json");
  if (jsonBlocks.length === 0) return alert("❌ No hay JSON para copiar.");
  const lastJson = jsonBlocks[jsonBlocks.length - 1].innerText;
  navigator.clipboard.writeText(lastJson)
    .then(() => alert("✅ JSON copiado al portapapeles"))
    .catch(() => alert("❌ No se pudo copiar"));
}

function limpiarChat() {
  const chatBox = document.getElementById("chat");
  chatBox.innerHTML = "";
  conversationHistory = [];
  document.getElementById("generateBtn").disabled = true;
  document.getElementById("generateBtn").style.opacity = 0.5;
}
