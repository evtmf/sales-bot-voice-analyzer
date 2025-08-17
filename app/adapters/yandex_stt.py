import requests
from app.config import YC_API_KEY, FOLDER_ID, TG_TOKEN

def recognize_speech(audio: bytes) -> str:
    r = requests.post(
        "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        headers={"Authorization": f"Api-Key {YC_API_KEY}"},
        params={
            "folderId": FOLDER_ID,
            "lang": "ru-RU",
            "format": "oggopus"  # 💡 Обязательно укажи формат
        },
        data=audio,
        timeout=15,
    )
    r.raise_for_status()
    return r.json().get("result", "")

def transcribe_voice_by_file_id(file_id: str) -> str:
    # Получаем путь к файлу от Telegram
    resp = requests.get(
        f"https://api.telegram.org/bot{TG_TOKEN}/getFile",
        params={"file_id": file_id},
        timeout=10,
    )
    file_path = resp.json()["result"]["file_path"]

    # Скачиваем .oga (Ogg Opus)
    voice_file = requests.get(
        f"https://api.telegram.org/file/bot{TG_TOKEN}/{file_path}",
        timeout=10
    ).content

    # Напрямую отправляем в SpeechKit без перекодировки
    return recognize_speech(voice_file)