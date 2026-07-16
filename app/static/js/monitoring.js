const healthBadge = document.querySelector("#health-badge");
const metricsForm = document.querySelector("#metrics-form");
const metricsEmpty = document.querySelector("#metrics-empty");
const metricsContent = document.querySelector("#metrics-content");
const metricsError = document.querySelector("#metrics-error");

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error("Service unavailable");
    const health = await response.json();
    setText("#health-database", health.database);
    setText("#health-ai", health.ai);
    setText("#health-email", health.email);
    healthBadge.className = "health-badge is-online";
    healthBadge.querySelector("span").textContent = "Работает";
  } catch {
    healthBadge.className = "health-badge is-offline";
    healthBadge.querySelector("span").textContent = "Недоступен";
  }
}

metricsForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  metricsError.textContent = "";
  const apiKey = document.querySelector("#metrics-key").value;

  try {
    const response = await fetch("/api/metrics", { headers: { "X-API-Key": apiKey } });
    if (!response.ok) {
      throw new Error(response.status === 401 ? "Неверный API-ключ." : "Не удалось загрузить метрики.");
    }
    const metrics = await response.json();
    setText("#metric-total", metrics.total);
    setText("#metric-recent", metrics.last_24_hours);
    setText("#metric-fallbacks", metrics.ai_fallbacks);
    setText("#metric-email-errors", metrics.email_failures);

    const categoryList = document.querySelector("#category-list");
    categoryList.replaceChildren();
    const entries = Object.entries(metrics.by_category);
    const categories = entries.length ? entries : [["Данных пока нет", 0]];
    categories.forEach(([category, count]) => {
      const item = document.createElement("span");
      item.className = "category-item";
      item.textContent = entries.length ? `${category}: ${count}` : category;
      categoryList.append(item);
    });

    metricsEmpty.style.display = "none";
    metricsContent.classList.add("is-visible");
  } catch (error) {
    metricsContent.classList.remove("is-visible");
    metricsEmpty.style.display = "block";
    metricsError.textContent = error.message;
  }
});

loadHealth();

