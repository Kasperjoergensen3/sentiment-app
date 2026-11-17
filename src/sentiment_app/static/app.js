// static/app.js
const form = document.getElementById("predict-form");
const input = document.getElementById("text");
const result = document.getElementById("result");
const history = document.getElementById("history");

const percent = (score) => `${Math.round(score * 100)}%`;

async function loadHistory() {
  const response = await fetch("/api/predictions?limit=10");
  if (!response.ok) return;
  const rows = await response.json();
  history.replaceChildren(
    ...rows.map((row) => {
      const item = document.createElement("li");
      // textContent (never innerHTML) so user text cannot inject HTML
      item.textContent = `${row.label} (${percent(row.score)}): ${row.text}`;
      return item;
    }),
  );
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  result.textContent = "Analysing…";
  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    result.textContent = `Something went wrong (HTTP ${response.status}).`;
    return;
  }
  const data = await response.json();
  result.textContent = `${data.label}, ${percent(data.score)} confident (model ${data.model_version})`;
  input.value = "";
  await loadHistory();
});

loadHistory();