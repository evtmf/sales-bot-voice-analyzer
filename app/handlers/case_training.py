# app/handlers/case_training.py
from app.adapters.yandex_gpt import gpt_evaluate
from app.utils.case_state import get_user_case_session
from app.adapters.telegram import send_message, send_keyboard
import json, re

def _extract_json_block(text: str) -> str | None:
    # вырезаем ```json ... ``` и ищем первый {...}
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.IGNORECASE)
    m = re.search(r"\{.*\}", t, flags=re.S)
    return m.group(0) if m else None

def parse_score_feedback(raw: str):
    try:
        payload = _extract_json_block(raw) or raw
        data = json.loads(payload)
        return data.get("score"), data.get("comment", "")
    except Exception:
        # не валидный JSON — не блокируем тренажёр
        return None, raw.strip()

def _local_keywords_eval(step, text: str):
    kw = [k.lower() for k in step.get("expected_keywords", [])]
    found = [k for k in kw if k in (text or "").lower()]
    return len(found), f"Найдено ключевых слов: {len(found)} из {len(kw)} ({', '.join(found)})"

def handle_case_voice(chat_id: int, file_id: str):
    try:
        session = get_user_case_session(chat_id)
        if not session:
            send_message(chat_id, "❗️Сессия не найдена. Нажмите «Начать тренажёр».")
            return
        from app.handlers.voice import stt_to_text
        user_answer_text = stt_to_text(file_id)

        step = session.get_current_step()
        if step is None:
            send_message(chat_id, "⚠️ Тренажёр уже завершён! Нажмите «Начать тренажёр» для нового запуска.")
            return

        eval_type = step.get('evaluation')

        # локальные режимы, чтобы не зависеть от GPT
        if eval_type == "manual":
            score, feedback = 1, "Ответ получен."
        elif eval_type == "keywords":
            score, feedback = _local_keywords_eval(step, user_answer_text)
        else:
            crit = session.criteria[eval_type]
            raw = gpt_evaluate(
                text=user_answer_text,
                prompt=crit['prompt'],
                scale=crit['scale'],
                feedback=crit.get('feedback', True)
            )
            score, feedback = parse_score_feedback(raw)

        session.save_result(step['id'], user_answer_text, score, feedback)
        nxt = session.next_step()
        if nxt:
            send_message(chat_id, f"Оценка: {score if score is not None else '-'}\nКомментарий: {feedback}\n\nСледующий шаг:\n📝 {nxt['question']}")
        else:
            send_message(chat_id, "👍 Все этапы пройдены! Нажмите кнопку ниже, чтобы получить отчёт.")
            send_keyboard(chat_id, [["Завершить тренажёр"]])
    except Exception as e:
        send_message(chat_id, f"❗️Ошибка в обработке голоса: {e}")

def handle_case_text(chat_id: int, text: str):
    try:
        session = get_user_case_session(chat_id)
        if not session:
            send_message(chat_id, "❗️Сессия не найдена. Нажмите «Начать тренажёр».")
            return

        step = session.get_current_step()
        if step is None:
            send_message(chat_id, "⚠️ Тренажёр уже завершён! Нажмите «Начать тренажёр».")
            return

        eval_type = step.get('evaluation')

        if eval_type == "manual":
            score, feedback = 1, "Ответ получен."
        elif eval_type == "keywords":
            score, feedback = _local_keywords_eval(step, text)
        else:
            crit = session.criteria[eval_type]
            raw = gpt_evaluate(
                text=text,
                prompt=crit['prompt'],
                scale=crit['scale'],
                feedback=crit.get('feedback', True)
            )
            score, feedback = parse_score_feedback(raw)

        session.save_result(step['id'], text, score, feedback)
        nxt = session.next_step()
        if nxt:
            send_message(chat_id, f"Оценка: {score if score is not None else '-'}\nКомментарий: {feedback}\n\nСледующий шаг:\n📝 {nxt['question']}")
        else:
            send_message(chat_id, "👍 Все этапы пройдены! Нажмите кнопку ниже, чтобы получить отчёт.")
            send_keyboard(chat_id, [["Завершить тренажёр"]])
    except Exception as e:
        send_message(chat_id, f"❗️Ошибка обработки текста: {e}")

def finish_case(chat_id: int):
    try:
        session = get_user_case_session(chat_id)
        if not session:
            send_message(chat_id, "❗️Нет активной сессии тренажёра.")
            return

        pdf_path = f"/tmp/{chat_id}_report.pdf"

        # общий summary просим у модели, но это не критично
        all_answers = "\n".join([str(r.get('answer','')) for r in session.results if r.get('answer')])
        summary = None
        try:
            summary = gpt_evaluate(
                text=all_answers,
                prompt="Сформируй короткий разбор по всему тренажёру (сильные стороны, зоны роста, рекомендации). Верни 100–200 слов.",
                scale=(1,1),
                feedback=True
            )
        except Exception:
            summary = None

        session.export_pdf(pdf_path, summary=summary)
        from app.adapters.telegram import send_document
        send_document(chat_id, pdf_path, caption="Ваш отчёт по тренажёру!")
        send_message(chat_id, "🎉 Тренажёр завершён! Отчёт отправлен.")
        # тут же можно обнулять сессию, если хочешь
        from app.utils.case_state import set_user_case_session
        set_user_case_session(chat_id, None)
    except Exception as e:
        send_message(chat_id, f"❗️Ошибка в finish_case: {e}")
