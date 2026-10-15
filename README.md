# 🗺️ MoodMap

Интерактивная карта мест и дневник настроения. Отмечай, где ты был, ставь одну из 10 улыбок и смотри, как менялось твоё настроение во времени и пространстве.

![Django](https://img.shields.io/badge/Django-6.x-092E20?logo=django)
![Python](https://img.shields.io/badge/Python-3.13.3-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900?logo=leaflet&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?logo=chartdotjs&logoColor=white)

---

## Что умеет

- **Карта мира** на Leaflet + OpenStreetMap — клик по любой точке создаёт запись.
- **10 улыбок** — оценка места от 😭 до 🤯, каждая с собственным цветом.
- **Дневник настроения** — привязка к дате, заметки и названия мест.
- **Кластеризация маркеров** и **тепловая карта** поверх — видно «счастливые зоны».
- **Три графика** на Chart.js:
  - динамика настроения по дням,
  - распределение оценок,
  - активность по дням.
- **Персональный вердикт** — «путешественник», «домосед» или «где-то посередине».
- **Живой фон** — небо, солнце и птицы, которые появляются в зависимости от среднего балла.
- **Публичный профиль** `/u/<username>/` с экспортом в GeoJSON.
- **Экспорт вердикта в PNG** через Pillow — картинка для соцсетей.
- **Streak** — сколько дней подряд ведёшь дневник.

---

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Python 3.13.3+, Django 6.12 |
| БД | PostgreSQL (прод) / SQLite (dev) |
| Frontend | Django templates, Tailwind CSS (CDN), vanilla JS |
| Карта | Leaflet, Leaflet.markercluster, Leaflet.heat |
| Графики | Chart.js 4 |
| Статика | WhiteNoise |
| Медиа | Cloudinary (опционально) |
| Деплой | Render |
| Тесты | pytest-django |

---

## Как запустить проект.

### 1. Клонировать и поставить зависимости

```bash
git clone https://github.com/your_nickname/moodmap.git
cd moodmap
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
2. Переменные окружения
Скопируй .env.example в .env и заполни:

bash
cp .env.example .env
env
SECRET_KEY=dev-secret-change-me
DEBUG=True
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=
# DATABASE_URL=postgres://user:pass@host:5432/dbname
# CLOUDINARY_URL=cloudinary://key:secret@cloud
3. Миграции + фикстура улыбок
bash
python manage.py migrate
python manage.py loaddata moods
4. Суперпользователь
bash
python manage.py createsuperuser
5. Запуск
bash
python manage.py runserver
Открой http://127.0.0.1:8000/ — зарегистрируйся, кликни по карте, поставь улыбку.

Структура
text
moodmap/
├── moodmap/              # настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/             # аутентификация и профили
│   ├── models.py         # Profile (phone, bio) + сигналы
│   ├── forms.py
│   ├── views.py
│   └── templates/accounts/
├── diary/                # основное приложение
│   ├── models.py         # Mood, Entry
│   ├── views.py
│   ├── api.py            # JSON API для графиков
│   ├── stats.py          # агрегации (кэш)
│   ├── verdict.py        # логика вердикта
│   ├── mood_theme.py     # выбор темы фона
│   ├── share.py          # PNG через Pillow
│   ├── fixtures/moods.json
│   └── templates/diary/
├── static/
│   ├── css/              # app.css, sky.css
│   └── js/               # map.js, charts.js, api.js
├── requirements.txt
├── render.yaml
├── build.sh
└── manage.py
Шкала из 10 улыбок
Score	Эмодзи	Название	Цвет
1	😭	Ужасно	#7f1d1d
2	😞	Плохо	#991b1b
3	😕	Так себе	#b45309
4	😐	Нейтрально	#a16207
5	🙂	Норм	#ca8a04
6	😊	Хорошо	#65a30d
7	😄	Отлично	#16a34a
8	🤩	Вау!	#059669
9	🥳	Восторг	#0d9488
10	🤯	Лучшее место в жизни	#7c3aed
Цвета — градиент от красного к фиолетовому, чтобы маркеры на карте образовывали красивую тепловую картину.

Живой фон
Фон сайта меняется в зависимости от записей:

Уровень	Условие	Вид
empty	нет записей	почти белый, полупрозрачные облака
homebody	< 5 записей, средний балл < 5	тёплый беж, мягкие облака
balanced	средний балл 5–6	рассветное небо
traveler	средний балл ≥ 6 и ≥ 5 записей	яркое небо, солнце, птицы

Всё на чистом CSS + SVG, без картинок — быстро и адаптивно.


API
Метод	URL	Описание
GET	/api/stats/?period=week|month|year|all	JSON с агрегатами, точками, KPI
POST	/api/entries/	Создать запись
POST	/api/entries/<id>/delete/	Удалить запись
GET	/api/verdict.png	PNG-картинка вердикта
GET	/u/<username>/	Публичный профиль
GET	/u/<username>/geojson/	Экспорт в GeoJSON
💡 Архитектурные решения
Минимум нагрузки на БД. Составные индексы (user, date) и (user, mood), select_related, values().annotate() вместо Python-циклов. Агрегаты кэшируются на 5 минут.


GitHub: https://github.com/SoYaMin1/

Email: pandawow0700148815@gmail.com

Сделано с 💜 на Django.