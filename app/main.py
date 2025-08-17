import logging
from flask import Flask, request

from app.utils.middleware import FixWSGIMiddleware
from app.handlers.start import handle_start, handle_case_start
from app.handlers.voice import handle_voice
from app.handlers.case_training import handle_case_text, handle_case_voice
from app.utils.case_state import is_user_in_case

app = Flask(__name__)
app.wsgi_app = FixWSGIMiddleware(app.wsgi_app)
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["POST"])
def webhook():
    payload = request.get_json(force=True, silent=True)
    if not payload or "message" not in payload:
        return "ok"

    message = payload["message"]
    chat_id = message["chat"]["id"]
    logging.info("Incoming message: %s", message)

    text = message.get("text", "")
    voice = message.get("voice", {})

    # 1. Обработка команды старта
    if text == "/start":
        handle_start(chat_id)

    # 2. Обработка команды старта кейса (совместимость)
    elif text == "/case":
        handle_case_start(chat_id)

    # 3. Обработка нажатия на кнопку "Начать тренажёр"
    elif text == "Начать тренажёр":
        handle_case_start(chat_id)

    # 4. Голосовые сообщения (если пользователь в кейсе — обработка как шаг тренажёра)
    elif voice:
        if is_user_in_case(chat_id):
            handle_case_voice(chat_id, voice["file_id"])
        else:
            handle_voice(chat_id, voice["file_id"])

    # 5. Завершение тренажёра кнопкой
    elif text == "Завершить тренажёр":
        from app.handlers.case_training import finish_case
        finish_case(chat_id)

    # 6. ОБРАБОТКА ЛЮБОГО ДРУГОГО ТЕКСТА во время тренажёра
    elif is_user_in_case(chat_id) and text:
        handle_case_text(chat_id, text)

    return "ok"