# Тайна 31-го огонька (редакция v2)

31 письмо Дедушки Мороза по русским сказкам + карта огоньков.  
Рамки — **русское прикладное искусство**: хохлома, гжель, дымка, городец, жостово, палех, мезень, филимоново.

## Скачать

- `tayna-31-ogonyka-print.pdf` — карта + 31 письмо  
- `print/letters-a5.pdf`, `print/letters-a4-2up.pdf`, `print/map-a4-landscape.pdf`

GitHub (ветка PR):  
https://github.com/Maer-Yakov/vpn-client/raw/cursor/tayna-31-ogonyka-design-8ad7/advent-tayna-31/tayna-31-ogonyka-print.pdf

## Сборка

```bash
pip install -r requirements.txt
python3 compose_letters.py
python3 compose_map.py
python3 sync_letters_md.py
python3 build_print_pdf.py
```

Нужны шрифты с кириллицей (`fonts-liberation` / `fonts-dejavu`) и папка `assets/` (frames + scenes).

## Источники

- PDF «31 красочных писем»
- DOCX-чеклист 29.10.2026
