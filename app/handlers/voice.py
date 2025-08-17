import logging
from app.adapters.telegram import send_message, get_voice_file
from app.adapters.yandex_stt import recognize_speech, transcribe_voice_by_file_id
from app.adapters.yandex_gpt import gpt_evaluate

def handle_voice(chat_id: int, file_id: str) -> None:
    try:
        audio = get_voice_file(file_id)
        text = recognize_speech(audio)
        # Всегда передаём prompt!
        analysis = gpt_evaluate(
            text,
            "Ты — эксперт по B2B-продажам. Оцени это голосовое сообщение как холодный звонок. Определи уровень профессионализма, наличие приветствия, установления контакта, выявления потребности и завершения диалога. Укажи ошибки и сильные стороны."
        )
        send_message(
            chat_id,
            f"🗣 Распознанный текст:\n{text}\n\n📊 Оценка:\n{analysis}",
        )
    except Exception as e:
        logging.exception("Voice processing error")
        send_message(chat_id, f"⚠️ Ошибка обработки: {e}")

def stt_to_text(file_id: str) -> str:
    return transcribe_voice_by_file_id(file_id)
