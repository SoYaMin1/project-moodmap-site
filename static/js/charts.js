(() => {
  // ─────────────────────────────────────────────
  // 1. Проверяем, что canvas'ы есть на странице
  // ─────────────────────────────────────────────
  const lineEl = document.getElementById("lineChart");
  const doughEl = document.getElementById("doughnutChart");
  const barEl = document.getElementById("barChart");

  if (!lineEl || !doughEl || !barEl) {
    console.warn("[MoodMap] Нет одного из canvas — графики не будут построены");
    return;
  }

  const lineCtx = lineEl.getContext("2d");
  const doughCtx = doughEl.getContext("2d");
  const barCtx = barEl.getContext("2d");

  // ─────────────────────────────────────────────
  // 2. Общие настройки — светлая тема
  // ─────────────────────────────────────────────
  const baseOpts = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        labels: {
          color: "#475569",
          font: { size: 12, family: "Inter, system-ui, sans-serif" },
          boxWidth: 12,
          padding: 12,
        },
      },
      tooltip: {
        backgroundColor: "#0f172a",
        titleColor: "#f1f5f9",
        bodyColor: "#cbd5e1",
        padding: 10,
        cornerRadius: 6,
        displayColors: false,
        titleFont: { size: 12, weight: "600" },
        bodyFont: { size: 12 },
      },
    },
    scales: {
      x: {
        ticks: { color: "#94a3b8", font: { size: 11 } },
        grid: { color: "#f1f5f9", drawBorder: false },
        border: { display: false },
      },
      y: {
        ticks: { color: "#94a3b8", font: { size: 11 } },
        grid: { color: "#f1f5f9", drawBorder: false },
        border: { display: false },
      },
    },
  };

  // ─────────────────────────────────────────────
  // 3. Line — динамика настроения
  // ─────────────────────────────────────────────
  const lineChart = new Chart(lineCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Настроение",
          data: [],
          tension: 0.35,
          borderColor: "#0f172a",
          borderWidth: 2,
          pointBackgroundColor: [],
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointHoverBorderWidth: 2,
          fill: true,
          backgroundColor: "rgba(15,23,42,0.04)",
        },
      ],
    },
    options: {
      ...baseOpts,
      scales: {
        ...baseOpts.scales,
        y: {
          ...baseOpts.scales.y,
          min: 0,
          max: 10,
          ticks: { ...baseOpts.scales.y.ticks, stepSize: 2 },
        },
      },
      interaction: { mode: "nearest", intersect: true },
    },
  });

  // ─────────────────────────────────────────────
  // 4. Doughnut — распределение оценок
  // ─────────────────────────────────────────────
  const doughnutChart = new Chart(doughCtx, {
    type: "doughnut",
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          backgroundColor: [],
          borderWidth: 2,
          borderColor: "#ffffff",
          hoverOffset: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "65%",
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#475569",
            font: { size: 11, family: "Inter, system-ui, sans-serif" },
            boxWidth: 10,
            padding: 10,
            usePointStyle: true,
            pointStyle: "circle",
          },
        },
        tooltip: {
          backgroundColor: "#0f172a",
          titleColor: "#f1f5f9",
          bodyColor: "#cbd5e1",
          padding: 10,
          cornerRadius: 6,
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.parsed} шт.`,
          },
        },
      },
    },
  });

  // ─────────────────────────────────────────────
  // 5. Bar — активность по месяцам
  // ─────────────────────────────────────────────
  const barChart = new Chart(barCtx, {
    type: "bar",
    data: {
      labels: [],
      datasets: [
        {
          label: "Записей",
          data: [],
          backgroundColor: "#0f172a",
          hoverBackgroundColor: "#1e293b",
          borderRadius: 4,
          maxBarThickness: 40,
        },
      ],
    },
    options: {
      ...baseOpts,
      plugins: {
        ...baseOpts.plugins,
        legend: { display: false },
      },
    },
  });

  // ─────────────────────────────────────────────
  // 6. Публичная функция — обновить графики + KPI
  // ─────────────────────────────────────────────
  window.renderCharts = (stats) => {
    if (!stats) {
      console.warn("[MoodMap] renderCharts: пустые данные");
      return;
    }

    // KPI
    const kpiTotal = document.getElementById("kpi-total");
    const kpiDays = document.getElementById("kpi-days");
    const kpiAvg = document.getElementById("kpi-avg");
    if (kpiTotal) kpiTotal.textContent = stats.kpi.total;
    if (kpiDays) kpiDays.textContent = stats.kpi.unique_days;
    if (kpiAvg) kpiAvg.textContent = stats.kpi.avg;

    // ── Line
    const labels = stats.line.map((r) => r.date);
    const data = stats.line.map((r) => r.avg);
    const colors = stats.line.map((r) => {
      const score = Math.round(r.avg);
      const mood = (window.MOODS || []).find((m) => m.score === score);
      return mood ? mood.color : "#94a3b8";
    });

    lineChart.data.labels = labels;
    lineChart.data.datasets[0].data = data;
    lineChart.data.datasets[0].pointBackgroundColor = colors;
    lineChart.update();

    // ── Doughnut
    doughnutChart.data.labels = stats.distribution.map(
      (d) => `${d.emoji} ${d.name}`
    );
    doughnutChart.data.datasets[0].data = stats.distribution.map((d) => d.cnt);
    doughnutChart.data.datasets[0].backgroundColor = stats.distribution.map(
      (d) => d.color
    );
    doughnutChart.update();

    // ── Bar
    barChart.data.labels = stats.months.map((m) => {
      // "2026-10-15" → "15.10"
      const parts = m.month.split("-");
      return parts.length === 3 ? `${parts[2]}.${parts[1]}` : m.month;
    });
    barChart.data.datasets[0].data = stats.months.map((m) => m.cnt);
    barChart.update();
  };

  // Экспортируем ссылку на line — она нужна api.js для клика по точке
  window.__lineChart = lineChart;
})();