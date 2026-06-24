const form = document.querySelector("#aura-form");
const auraOrb = document.querySelector("#aura-orb");
const auraName = document.querySelector("#aura-name");
const auraMeaning = document.querySelector("#aura-meaning");
const auraScore = document.querySelector("#aura-score");
const scoreBar = document.querySelector("#score-bar");
const focusReading = document.querySelector("#focus-reading");
const bindingLabel = document.querySelector("#binding-label");
const bindingScore = document.querySelector("#binding-score");
const bindingCopy = document.querySelector("#binding-copy");

function updateResult(reading) {
  auraOrb.style.setProperty("--aura-color", reading.color);
  auraName.textContent = reading.aura;
  auraMeaning.textContent = reading.meaning;
  auraScore.textContent = reading.score;
  scoreBar.style.width = `${reading.score}%`;
  focusReading.textContent = reading.focus_reading;
  bindingLabel.textContent = reading.binding_label;

  if (reading.binding_score === null) {
    bindingScore.textContent = "--";
    bindingCopy.textContent = "Add another name to test whether the two frequencies pull, clash, or bind.";
    return;
  }

  bindingScore.textContent = `${reading.binding_score}%`;
  bindingCopy.textContent = `${reading.name} and ${reading.binding_name} are reading as ${reading.binding_label.toLowerCase()}.`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const data = new FormData(form);
  const payload = {
    name: data.get("name"),
    birth_month: Number(data.get("birth_month")),
    mood: data.get("mood"),
    focus: data.get("focus"),
    binding_name: data.get("binding_name"),
  };

  const response = await fetch("/api/aura", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    bindingCopy.textContent = "The aura scanner glitched. Try again with a shorter name.";
    return;
  }

  updateResult(await response.json());
});

scoreBar.style.width = "88%";
