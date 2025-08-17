# app/utils/pdf_export.py
from fpdf import FPDF

GREEN = (0, 185, 86)

class ReportPDF(FPDF):
    def header(self):
        # зелёная полоска + заголовок
        self.set_fill_color(*GREEN)
        self.rect(0, 0, 210, 18, 'F')
        self.set_font('Arial', 'B', 15)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'Отчёт по тренажёру B2B', 0, 1, 'C')
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120)
        self.cell(0, 10, f'Стр. {self.page_no()}', 0, 0, 'R')

    # те самые методы, которых не хватало
    def section_title(self, title: str):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*GREEN)
        self.cell(0, 10, title, ln=True)
        self.set_text_color(0, 0, 0)

    def section_body(self, text: str):
        self.set_font('Arial', '', 12)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 7, text)
        self.ln(2)

def make_pdf_report(case, results, filename, summary=None, user_name=None, start_time=None):
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # шапка с инфо
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"Тренажёр: {case.get('name','')}", ln=True)
    pdf.ln(1)
    if case.get('description'):
        pdf.section_title("Описание")
        pdf.section_body(case['description'])

    # таблица результатов
    pdf.section_title("Результаты шагов")

    pdf.set_font('Arial', 'B', 11)
    pdf.set_fill_color(*GREEN)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(68, 8, "Вопрос", 1, 0, 'C', True)
    pdf.cell(50, 8, "Ответ", 1, 0, 'C', True)
    pdf.cell(15, 8, "Баллы", 1, 0, 'C', True)
    pdf.cell(45, 8, "Комментарий", 1, 1, 'C', True)

    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(30, 30, 30)

    total = 0
    steps_by_id = {s['id']: s for s in case.get('steps', [])}
    for r in results:
        step = steps_by_id.get(r['step_id'], {})
        q = (step.get('question') or '')[:60]
        a = (str(r.get('answer') or ''))[:50]
        s = r.get('score')
        f = (str(r.get('feedback') or ''))[:60]

        pdf.cell(68, 8, q, 1)
        pdf.cell(50, 8, a, 1)
        pdf.cell(15, 8, '-' if s is None else str(s), 1, 0, 'C')
        pdf.cell(45, 8, f, 1, 1)

        if isinstance(s, int):
            total += s

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 8, f"Итоговый балл: {total}", ln=True)

    if summary:
        pdf.ln(4)
        pdf.section_title("Общий разбор")
        pdf.section_body(summary)

    pdf.output(filename)