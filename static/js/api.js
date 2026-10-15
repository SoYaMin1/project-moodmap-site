(async () => {
  // ─────────────────────────────────────────────
  // 1. Проверка, что конфиг и модули доступны
  // ─────────────────────────────────────────────
  if (!window.STATS_URL) {
    console.error("[MoodMap] STATS_URL не задан. Проверь #django-config в шаблоне");
    return;
  }
  if (!window.MOODMAP || !window.MOODMAP.renderPoints) {
    console.error("[MoodMap] MOODMAP не готов. Проверь map.js");
    return;
  }

  // ─────────────────────────────────────────────
  // 2. Обновление данных по периоду
  // ─────────────────────────────────────────────
  async function refresh(period = "all") {
    try {
      const r = await fetch(`${STATS_URL}?period=${period}`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!r.ok) {
        console.error("[MoodMap] Ошибка статистики:", r.status);
        return;
      }
      const stats = await r.json();

      // Сохраняем точки для клика по тепловой карте
      window.__lastPoints = stats.points || [];

      // Маркеры на карте
      window.MOODMAP.renderPoints(window.__lastPoints);

      // Графики + KPI
      if (window.renderCharts) {
        window.renderCharts(stats);
      }
    } catch (e) {
      console.error("[MoodMap] Сетевая ошибка статистики:", e);
    }
  }
  window.refresh = refresh;

  // ─────────────────────────────────────────────
  // 3. Переключатель периодов
  // ─────────────────────────────────────────────
  const periodBtns = document.querySelectorAll(".period-btn");

  // Классы активной/неактивной кнопки
  const ACTIVE_CLASSES = ["bg-slate-900", "text-white"];
  const INACTIVE_CLASSES = ["text-slate-600", "hover:bg-slate-100"];

  function setActivePeriod(btn) {
    periodBtns.forEach((b) => {
      b.classList.remove(...ACTIVE_CLASSES);
      b.classList.add(...INACTIVE_CLASSES);
    });
    btn.classList.remove(...INACTIVE_CLASSES);
    btn.classList.add(...ACTIVE_CLASSES);
  }

  periodBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      setActivePeriod(btn);
      refresh(btn.dataset.period || "all");
    });
  });

  // ─────────────────────────────────────────────
  // 4. Клик по точке на графике → центрируем карту
  // ─────────────────────────────────────────────
  if (window.__lineChart) {
    window.__lineChart.canvas.addEventListener("click", (e) => {
      const pts = window.__lineChart.getElementsAtEventForMode(
        e,
        "nearest",
        { intersect: true },
        true
      );
      if (!pts.length) return;

      const idx = pts[0].index;
      const date = window.__lineChart.data.labels[idx];
      const matching = (window.__lastPoints || []).filter(
        (p) => p.date === date
      );
      if (!matching.length) return;

      const map = window.MOODMAP.map;

      if (matching.length === 1) {
        // одна точка — просто центрируем и приближаем
        map.setView(
          [matching[0].latitude, matching[0].longitude],
          13,
          { animate: true }
        );
      } else {
        // несколько точек за один день — вписываем bounds
        const bounds = L.latLngBounds(
          matching.map((p) => [p.latitude, p.longitude])
        );
        map.fitBounds(bounds, { padding: [50, 50], animate: true });
      }
    });
  }

  // ─────────────────────────────────────────────
  // 5. Первичная загрузка
  // ─────────────────────────────────────────────
  refresh("all");
})();