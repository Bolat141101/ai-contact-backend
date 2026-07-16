const form = document.querySelector("#contact-form");
const submitButton = form?.querySelector("button[type='submit']");
const formStatus = document.querySelector("#form-status");
const aiResponse = document.querySelector("#ai-response");
const aiReply = document.querySelector("#ai-reply");
const aiMeta = document.querySelector("#ai-meta");
const yearElement = document.querySelector("#current-year");

if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}

const messages = {
  valueMissing: "Заполните это поле.",
  typeMismatch: "Проверьте формат значения.",
  tooShort: "Значение слишком короткое.",
  tooLong: "Значение слишком длинное.",
};

function clearFeedback() {
  form?.querySelectorAll(".field").forEach((field) => field.classList.remove("has-error"));
  form?.querySelectorAll(".field-error").forEach((error) => { error.textContent = ""; });
  if (formStatus) {
    formStatus.className = "form-status";
    formStatus.textContent = "";
  }
  aiResponse?.classList.remove("is-visible");
  if (aiReply) aiReply.textContent = "";
  if (aiMeta) aiMeta.textContent = "";
}

function showFieldError(name, message) {
  const input = form?.elements.namedItem(name);
  const error = document.querySelector(`#${name}-error`);
  input?.closest(".field")?.classList.add("has-error");
  if (error) error.textContent = message;
}

function validateForm() {
  let isValid = true;
  form?.querySelectorAll("input, textarea").forEach((input) => {
    if (!input.validity.valid) {
      const reason = Object.keys(messages).find((key) => input.validity[key]);
      showFieldError(input.name, messages[reason] || "Проверьте значение.");
      isValid = false;
    }
  });
  return isValid;
}

function showServerErrors(details) {
  const errors = details?.json || {};
  Object.entries(errors).forEach(([field, fieldMessages]) => {
    const message = Array.isArray(fieldMessages) ? fieldMessages[0] : String(fieldMessages);
    showFieldError(field, message);
  });
}

function setLoading(isLoading) {
  if (!submitButton || !form) return;
  submitButton.disabled = isLoading;
  submitButton.classList.toggle("is-loading", isLoading);
  form.setAttribute("aria-busy", String(isLoading));
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFeedback();

  if (!validateForm()) return;

  const data = Object.fromEntries(new FormData(form));
  Object.keys(data).forEach((key) => { data[key] = data[key].trim(); });
  setLoading(true);

  try {
    const response = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const payload = await response.json();

    if (!response.ok) {
      showServerErrors(payload.error?.details);
      const message = response.status === 429
        ? "Слишком много попыток. Пожалуйста, попробуйте немного позже."
        : payload.error?.message || "Не удалось отправить обращение.";
      throw new Error(message);
    }

    form.reset();
    formStatus.className = "form-status is-success";
    formStatus.textContent = `Спасибо! Обращение №${payload.id} принято.`;
    if (aiResponse && aiReply && aiMeta) {
      aiReply.textContent = payload.ai.reply;
      aiMeta.textContent = payload.ai_processed
        ? `${payload.ai.category} · ${payload.ai.sentiment} · ${payload.ai.priority}`
        : "Шаблонный ответ · AI временно недоступен";
      aiResponse.classList.add("is-visible");
    }
  } catch (error) {
    formStatus.className = "form-status is-error";
    formStatus.textContent = error instanceof Error
      ? error.message
      : "Сервис временно недоступен. Попробуйте позже.";
  } finally {
    setLoading(false);
  }
});
