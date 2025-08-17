import requests
from app.config import FOLDER_ID
from app.adapters.yc_token import get_iam_token_from_metadata

def gpt_evaluate(text, prompt, scale=(1, 10), feedback=True):
    iam_token = get_iam_token_from_metadata()
    system_prompt = (
        prompt
        + f"\nШкала оценивания: {scale[0]}–{scale[1]}."
        + ("\nДобавь краткий комментарий." if feedback else "")
        + "\nОТВЕЧАЙ СТРОГО ОДНИМ ВАЛИДНЫМ JSON-ОБЪЕКТОМ БЕЗ КОДОВЫХ БЛОКОВ И ЛИШНЕГО ТЕКСТА."
        + "\nФормат: {\"score\": int, \"comment\": \"текст\"}."
    )
    r = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers={
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json",
        },
        json={
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.2,
                "maxTokens": 400,
            },
            "messages": [
                {"role": "system", "text": system_prompt},
                {"role": "user", "text": text},
            ],
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()["result"]["alternatives"][0]["message"]["text"]
