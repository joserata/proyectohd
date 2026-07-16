/* Dashboard DevSecOps: la lista de herramientas se genera en Django. */
const reports = {};
const csrf = document.querySelector('[name="csrfmiddlewaretoken"]')?.value || "";

function runUrl(tool) {
    return (window.securityRunUrlTemplate || "/security/run/__tool__/").replace("__tool__", encodeURIComponent(tool));
}

function selectedTools() {
    return [...document.querySelectorAll(".tool-check:checked")].map((input) => input.value);
}

async function runTool(tool) {
    const target = document.getElementById("target_url").value.trim();
    setStatus(tool, "Ejecutando...", "warning");
    try {
        const response = await fetch(runUrl(tool), {
            method: "POST",
            headers: { "X-CSRFToken": csrf, "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ target_url: target }),
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            setStatus(tool, "Error", "danger");
            alert(data.message || "No fue posible ejecutar la herramienta.");
            return false;
        }
        reports[tool] = data;
        updateCard(tool, data);
        return true;
    } catch (error) {
        console.error(error);
        setStatus(tool, "Error", "danger");
        return false;
    }
}

async function runSelected() {
    const tools = selectedTools();
    if (!tools.length) return alert("Seleccione al menos una herramienta.");
    disableButtons(true);
    for (const tool of tools) await runTool(tool);
    disableButtons(false);
}

async function runAll() {
    document.querySelectorAll(".tool-check").forEach((input) => { input.checked = true; });
    await runSelected();
}

function updateCard(tool, data) {
    document.getElementById(`${tool}_status`).textContent = data.status;
    document.getElementById(`${tool}_status`).className = `status ${data.status}`;
    document.getElementById(`${tool}_duration`).textContent = `${data.duration} s`;
    document.getElementById(`${tool}_findings`).textContent = data.findings ?? 0;
    const score = document.getElementById(`${tool}_score`);
    if (score) score.textContent = data.score ?? "--";
}

function setStatus(tool, text, color) {
    const element = document.getElementById(`${tool}_status`);
    if (element) { element.textContent = text; element.className = `status ${color}`; }
}

function disableButtons(disabled) {
    document.querySelectorAll("button").forEach((button) => { button.disabled = disabled; });
}

function openReport(tool) {
    if (!reports[tool]) return alert("Debe ejecutar primero esta herramienta.");
    document.getElementById("reportModal").style.display = "block";
    document.getElementById("modalTitle").textContent = tool.toUpperCase();
    document.getElementById("modalRecommendation").textContent = reports[tool].recommendation || "Sin información.";
    document.getElementById("modalOutput").textContent = reports[tool].output || "";
}

function closeReport() { document.getElementById("reportModal").style.display = "none"; }

function downloadReport(tool) {
    if (!reports[tool]) return alert("Debe ejecutar primero esta herramienta.");
    const blob = new Blob([JSON.stringify(reports[tool], null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob); link.download = `${tool}_report.json`; link.click();
    URL.revokeObjectURL(link.href);
}

function clearDashboard() {
    Object.keys(reports).forEach((tool) => delete reports[tool]);
    document.querySelectorAll(".tool-card").forEach((card) => {
        const status = card.querySelector(".status");
        if (status) { status.textContent = "Pendiente"; status.className = "status waiting"; }
        card.querySelectorAll("strong").forEach((field) => {
            if (field.id.endsWith("_findings")) field.textContent = "0";
            if (field.id.endsWith("_score") || field.id.endsWith("_duration")) field.textContent = "--";
        });
    });
    document.getElementById("globalScore").textContent = "--";
    document.getElementById("riskLevel").textContent = "Sin ejecutar";
}
