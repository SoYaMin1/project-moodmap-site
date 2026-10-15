(() => {
  // ─────────────────────────────────────────────
  // 1. Читаем конфиг из шаблона
  // ─────────────────────────────────────────────
  const moodsDataEl = document.getElementById("moods-data");
  if (!moodsDataEl) {
    console.error("[MoodMap] Не найден #moods-data. Проверь {{ moods_json|json_script:'moods-data' }} в шаблоне.");
    return;
  }

  let MOODS_LOCAL;
  try {
    MOODS_LOCAL = JSON.parse(moodsDataEl.textContent);
    if (typeof MOODS_LOCAL === "string") {
      MOODS_LOCAL = JSON.parse(MOODS_LOCAL);
    }
  } catch (e) {
    console.error("[MoodMap] Не могу распарсить moods-data:", e, moodsDataEl.textContent);
    return;
  }

  if (!Array.isArray(MOODS_LOCAL) || MOODS_LOCAL.length === 0) {
    console.error("[MoodMap] moods-data пустой или не массив. Загрузи фикстуру: python manage.py loaddata moods");
    return;
  }

  window.MOODS = MOODS_LOCAL;
  window.MOODS_BY_ID = Object.fromEntries(MOODS_LOCAL.map(m => [m.id, m]));

  const cfgEl = document.getElementById("django-config");
  if (!cfgEl) {
    console.error("[MoodMap] Не найден #django-config");
    return;
  }
  window.STATS_URL = cfgEl.dataset.statsUrl;
  window.ENTRY_URL = cfgEl.dataset.entryUrl;
  window.CSRF = cfgEl.dataset.csrf;

  // ─────────────────────────────────────────────
  // 2. Карта — центр на Бишкеке, зум 12
  // ─────────────────────────────────────────────
  const BISHKEK = [42.8746, 74.5698];
  const map = L.map("map", { zoomControl: true }).setView(BISHKEK, 12);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19,
    referrerPolicy: 'strict-origin-when-cross-origin',
  }).addTo(map);

  const cluster = L.markerClusterGroup({ showCoverageOnHover: false });
  map.addLayer(cluster);
  let heatLayer = null;

  const modal = document.getElementById("entry-modal");
  const moodGrid = document.getElementById("mood-grid");
  const fLat = document.getElementById("f-lat");
  const fLng = document.getElementById("f-lng");
  const fDate = document.getElementById("f-date");
  let selectedMoodId = null;

  // ─────────────────────────────────────────────
  // 3. Кнопки улыбок — рендерим сразу
  // ─────────────────────────────────────────────
  moodGrid.innerHTML = "";
  MOODS_LOCAL.forEach(m => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "mood-btn";
    b.style.background = (m.color || "#e2e8f0") + "14";
    b.dataset.id = m.id;
    b.innerHTML = `<span class="emoji">${m.emoji}</span><span class="score">${m.score}</span>`;
    b.title = m.name || "";
    b.addEventListener("click", () => {
      moodGrid.querySelectorAll(".mood-btn").forEach(x => x.classList.remove("selected"));
      b.classList.add("selected");
      selectedMoodId = m.id;
    });
    moodGrid.appendChild(b);
  });
  console.log("[MoodMap] Кнопки оценок отрисованы:", MOODS_LOCAL.length);

  // ─────────────────────────────────────────────
  // 4. Модалка
  // ─────────────────────────────────────────────
  map.on("click", (e) => {
    const { lat, lng } = e.latlng;
    fLat.value = lat;
    fLng.value = lng;
    fDate.value = new Date().toISOString().slice(0, 10);
    selectedMoodId = null;
    moodGrid.querySelectorAll(".mood-btn").forEach(x => x.classList.remove("selected"));
    modal.classList.add("show");
  });

  const closeModal = () => modal.classList.remove("show");
  document.getElementById("close-modal").onclick = closeModal;
  document.getElementById("cancel-modal").onclick = closeModal;

  // ─────────────────────────────────────────────
  // 5. Сохранение
  // ─────────────────────────────────────────────
  document.getElementById("entry-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!selectedMoodId) {
      alert("Поставь оценку");
      return;
    }
    const fd = new FormData(e.target);
    const payload = {
      mood_id: selectedMoodId,
      latitude: parseFloat(fd.get("latitude")),
      longitude: parseFloat(fd.get("longitude")),
      title: fd.get("title") || "",
      note: fd.get("note") || "",
      date: fd.get("date"),
    };
    try {
      const r = await fetch(ENTRY_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF },
        body: JSON.stringify(payload),
      });
      if (r.ok) {
        closeModal();
        e.target.reset();
        if (window.refresh) await window.refresh("all");
        setTimeout(() => location.reload(), 300);
      } else {
        const t = await r.text();
        console.error("[MoodMap] Ошибка сохранения:", r.status, t);
        alert("Ошибка сохранения: " + r.status);
      }
    } catch (err) {
      console.error("[MoodMap] Сетевая ошибка:", err);
      alert("Сетевая ошибка. Смотри консоль.");
    }
  });

  // ─────────────────────────────────────────────
  // 6. Отрисовка маркеров
  // ─────────────────────────────────────────────
  function renderPoints(points) {
    cluster.clearLayers();
    if (heatLayer) {
      map.removeLayer(heatLayer);
      heatLayer = null;
    }

    points.forEach(p => {
      const color = p["mood__color"];
      const emoji = p["mood__emoji"];
      const icon = L.divIcon({
        className: "",
        html: `<div class="mood-marker" style="background:${color};width:30px;height:30px;">${emoji}</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });
      const marker = L.marker([p.latitude, p.longitude], { icon });
      const title = p.title ? `<b>${p.title}</b><br>` : "";
      marker.bindPopup(`${title}${emoji} ${p.date}<br>${p.note ? `<span style="color:#64748b">${p.note}</span>` : ""}`);
      marker._entry = p;
      cluster.addLayer(marker);
    });

    const heatToggle = document.getElementById("heat-toggle");
    if (heatToggle && heatToggle.checked) {
      buildHeat(points);
    }
  }

  function buildHeat(points) {
    const data = points.map(p => [p.latitude, p.longitude, p["mood__score"] / 10]);
    heatLayer = L.heatLayer(data, {
      radius: 30,
      blur: 22,
      maxZoom: 12,
      gradient: {
        0.2: "#7f1d1d",
        0.5: "#ca8a04",
        0.8: "#0d9488",
        1.0: "#7c3aed",
      },
    }).addTo(map);
  }

  const heatToggle = document.getElementById("heat-toggle");
  if (heatToggle) {
    heatToggle.addEventListener("change", (e) => {
      if (!window.__lastPoints) return;
      if (e.target.checked) buildHeat(window.__lastPoints);
      else if (heatLayer) {
        map.removeLayer(heatLayer);
        heatLayer = null;
      }
    });
  }

  window.MOODMAP = { map, renderPoints, cluster };
})();