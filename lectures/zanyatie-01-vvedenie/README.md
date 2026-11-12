# Занятие 1. Введение в музыкально-ритмическое развитие ребёнка

Материалы для студентов педагогических колледжей (специальность «Дошкольное образование»).

## Файлы

| Файл | Назначение |
|---|---|
| `Scenariy_zanyatiya_1_Muzykalno_ritmicheskoe_razvitie.pdf` | Сценарий **для педагога** (без картинок, прямое обращение к студентам) |
| `Prezentaciya_zanyatie_1_Muzykalno_ritmicheskoe_razvitie.pptx` | Презентация со схемами и иллюстрациями |
| `konspekt.md` | Текстовый конспект |
| `assets/` | Иллюстрации и схемы |
| `generate_diagrams.py` / `generate_materials.py` | Скрипты пересборки материалов |

## Хронометраж (90 мин)

1. Организационный момент — 10 мин  
2. Теоретический блок — 35 мин  
3. Музыкально-двигательная пауза — 10 мин  
4. Практический блок — 30 мин  
5. Рефлексия и итог — 5 мин  

## Пересборка

### Зависимости

```bash
python3 -m pip install pillow reportlab python-pptx
```

Нужны шрифты с кириллицей (предпочтительно DejaVu):

```bash
# Debian / Ubuntu
sudo apt install fonts-dejavu
```

Скрипты ищут DejaVu, Liberation Sans или Noto Sans в стандартных путях Linux/macOS.

### Команды

```bash
# только сценарий для педагога (без картинок)
python3 generate_scenario_pdf.py

# презентация (+ сценарий)
python3 generate_diagrams.py
python3 generate_materials.py
```
