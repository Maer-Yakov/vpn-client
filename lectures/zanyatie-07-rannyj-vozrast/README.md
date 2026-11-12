# Занятие 7. Музыкально-ритмическое развитие детей от 1,5 до 3 лет

Материалы для студентов педагогических колледжей (специальность «Дошкольное образование»).

## Файлы

| Файл | Назначение |
|---|---|
| `Scenariy_zanyatiya_7_Muzykalno_ritmicheskoe_razvitie_1_5_3.pdf` | Сценарий занятия (формат практического конспекта) |
| `konspekt.md` | Текстовый конспект |
| `generate_scenario_pdf.py` | Скрипт пересборки сценария |
| `font_paths.py` | Поиск кириллических шрифтов |

## Хронометраж (90 мин)

1. Вводная часть — 15 мин  
2. Основная часть — 50 мин  
3. Заключительная часть — 25 мин  

## Пересборка

Нужны шрифты с кириллицей (предпочтительно DejaVu):

```bash
# Debian / Ubuntu
sudo apt install fonts-dejavu
```

Рекомендуемый способ установки зависимостей — виртуальное окружение (на Debian/Ubuntu 12+ системный `pip` может быть запрещён из‑за PEP 668):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install reportlab
python generate_scenario_pdf.py
```

Альтернатива через пакеты дистрибутива (если доступны):

```bash
sudo apt install python3-reportlab
python3 generate_scenario_pdf.py
```
