import json
from datetime import datetime

import json

class CaseSession:
    def __init__(self, case_path, criteria_path):
        self.case = self.load_json(case_path)
        self.criteria = self.load_json(criteria_path)
        self.current_step = 0
        self.results = []

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_current_step(self):
        # Возвращает None если шаг вне диапазона — ЗАЩИТА ОТ СЛЁТА
        if 0 <= self.current_step < len(self.case['steps']):
            return self.case['steps'][self.current_step]
        return None

    def next_step(self):
        self.current_step += 1
        if self.current_step < len(self.case['steps']):
            return self.case['steps'][self.current_step]
        return None

    def save_result(self, step_id, answer, score, feedback=None):
        self.results.append({
            "step_id": step_id,
            "answer": answer,
            "score": score,
            "feedback": feedback
        })

    def export_pdf(self, filename, summary=None):
        from app.utils.pdf_export import make_pdf_report
        make_pdf_report(self.case, self.results, filename, summary)


