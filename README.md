# RAG_HSE: RAG over `strategy.pdf`

Система строит индекс только по `strategy.pdf`, затем отвечает на вопросы из тестового файла и заполняет колонку `answer`.

## Ограничения
- Единственный источник фактов: `strategy.pdf`.
- Если ответа нет в извлечённом контексте: `В документе не указано.`
- В XLSX записывается только текст ответа в колонку `answer`.

## Структура
- `src/` — модули пайплайна (extract/clean/chunk/embed/retrieve/generate/fill).
- `scripts/build_index.py` — построение индекса.
- `scripts/run_fill_testset.py` — заполнение `answer` в XLSX.
- `scripts/smoke_test.py` — быстрый прогон.
- `data/` — chunks + FAISS.
- `outputs/` — итоговый XLSX и debug JSONL.

## Быстрый старт (Windows, PowerShell)
1. Создать окружение и установить зависимости:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Настроить переменные среды:
- скопировать `.env.example` в `.env`
- заполнить `OPENAI_API_KEY`

3. Построить индекс:
```powershell
python scripts\build_index.py
```

4. Заполнить тестовый файл:
```powershell
python scripts\run_fill_testset.py --in test_set_Shalugin_Dmitrii.xlsx --out outputs\test_set_Shalugin_Dmitrii.xlsx
```

## Debug
Для каждого вопроса пишется JSONL запись в `outputs/debug_retrieval.jsonl`:
- вопрос
- ответ
- найденные чанки (id/section/pages/score)
- timestamp

## Примечание
Скрипты используют OpenAI API для эмбеддингов и генерации ответа (`gpt-5.4`).
