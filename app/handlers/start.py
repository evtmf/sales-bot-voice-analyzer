from app.adapters.telegram import send_message, send_keyboard

def handle_start(chat_id: int) -> None:
    send_message(
        chat_id,
        "👋 Привет! Готов пройти тренажёр по B2B-продажам?\n"
        "Нажми кнопку ниже, чтобы начать.",
    )
    send_keyboard(
        chat_id,
        [["Начать тренажёр"]],
    )

def handle_case_start(chat_id: int) -> None:
    from app.trainers.trainer import CaseSession
    from app.utils.case_state import set_user_case_session

    CASE_PATH = "cases/dub_i_buk_case.json"
    CRITERIA_PATH = "cases/dub_i_buk_criteria.json"
    session = CaseSession(CASE_PATH, CRITERIA_PATH)
    set_user_case_session(chat_id, session)

    # Сначала описание кейса!
    description = session.case.get("description", "")
    if description:
        send_message(chat_id, f"ℹ️ {description}")

    # Затем первый вопрос
    first_task = session.get_current_step()
    send_message(chat_id, f"📝 {first_task['question']}")
