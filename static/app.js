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
const resultCards = document.querySelectorAll(".result-line, .below-readout");
const authState = document.querySelector("#auth-state");
const authProvider = document.querySelector("#auth-provider");
const createAccountBtn = document.querySelector("#create-account-btn");
const loginBtn = document.querySelector("#login-btn");
const navCreateBtn = document.querySelector("#nav-create-btn");
const navLoginBtn = document.querySelector("#nav-login-btn");
const googleLogin = document.querySelector("#google-login");
const instagramLogin = document.querySelector("#instagram-login");
const authModal = document.querySelector("#auth-modal");
const closeAuth = document.querySelector("#close-auth");
const authModalButtons = document.querySelectorAll(".auth-providers-modal button");
const bindingPlatformInput = document.querySelector("#binding-platform");
const platformButtons = document.querySelectorAll(".platform-picker button");

let signedInProvider = null;
let selectedPlatform = "";

function setAuthState(provider) {
  signedInProvider = provider;
  authState.textContent = provider ? `${provider} signed in` : "Not signed in";
  authProvider.textContent = provider
    ? `Bound account access for ${provider}`
    : "Use Google or Instagram to start.";
}

function updateResult(reading) {
  document.documentElement.style.setProperty("--aura-color", reading.color);
  auraOrb.style.setProperty("--aura-color", reading.color);
  auraName.textContent = reading.aura;
  auraMeaning.textContent = reading.meaning;
  auraScore.textContent = reading.score;
  scoreBar.style.width = `${reading.score}%`;
  focusReading.textContent = reading.focus_reading;
  bindingLabel.textContent = reading.binding_label;
  resultCards.forEach((card) => {
    card.classList.remove("is-fresh");
    window.requestAnimationFrame(() => card.classList.add("is-fresh"));
  });

  if (reading.binding_score === null) {
    bindingScore.textContent = "--";
    bindingCopy.textContent = "Type an account and bind the visual.";
    return;
  }

  bindingScore.textContent = `${reading.binding_score}%`;
  if (reading.binding_platform) {
    const platformLabel = reading.binding_platform === "x" ? "X" : reading.binding_platform.charAt(0).toUpperCase() + reading.binding_platform.slice(1);
    bindingCopy.textContent = `${reading.binding_name} on ${platformLabel} / ${reading.binding_label.toLowerCase()}`;
  } else {
    bindingCopy.textContent = `${reading.binding_name} / ${reading.binding_label.toLowerCase()}`;
  }
}

function openAuthModal() {
  authModal.classList.remove("hidden");
}

function closeAuthModal() {
  authModal.classList.add("hidden");
}

function handleProviderSignIn(provider) {
  setAuthState(provider);
  closeAuthModal();
}

function selectPlatform(platform) {
  selectedPlatform = platform;
  bindingPlatformInput.value = platform;
  platformButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.platform === platform);
  });
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
    binding_platform: data.get("binding_platform"),
  };

  if (!payload.binding_name?.trim()) {
    bindingCopy.textContent = "Choose a social handle and a platform to bind.";
    return;
  }

  if (!payload.binding_platform) {
    bindingCopy.textContent = "Pick Google, Instagram, TikTok, or X before binding.";
    return;
  }

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

createAccountBtn.addEventListener("click", openAuthModal);
loginBtn.addEventListener("click", openAuthModal);
navCreateBtn?.addEventListener("click", openAuthModal);
navLoginBtn?.addEventListener("click", openAuthModal);
googleLogin.addEventListener("click", () => handleProviderSignIn("Google"));
instagramLogin.addEventListener("click", () => handleProviderSignIn("Instagram"));
closeAuth.addEventListener("click", closeAuthModal);

authModalButtons.forEach((button) => {
  button.addEventListener("click", () => handleProviderSignIn(button.dataset.provider));
});

platformButtons.forEach((button) => {
  button.addEventListener("click", () => selectPlatform(button.dataset.platform));
});

scoreBar.style.width = "0%";
setAuthState(null);
selectPlatform("instagram");
