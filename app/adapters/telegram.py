import requests
from app.config import TG_TOKEN

def send_document(chat_id: int, file_path: str, caption: str = None) -> None:
    with open(file_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument",
            data=data,
            files=files,
            timeout=20
        )

def send_message(chat_id: int, text: str) -> None:
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=5,
    )

def get_voice_file(file_id: str) -> bytes:
    info_resp = requests.get(
        f"https://api.telegram.org/bot{TG_TOKEN}/getFile?file_id={file_id}",
        timeout=5,
    ).json()
    file_path = info_resp["result"]["file_path"]
    file_url  = f"https://api.telegram.org/file/bot{TG_TOKEN}/{file_path}"
    return requests.get(file_url, timeout=10).content

def send_keyboard(chat_id: int, keyboard) -> None:
    # Простая реализация отправки ReplyKeyboardMarkup (обычные кнопки под строкой ввода)
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "Выберите действие:",
            "reply_markup": {
                "keyboard": keyboard,
                "resize_keyboard": True,
                "one_time_keyboard": True
            }
        },
        timeout=5,
    )
