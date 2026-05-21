"""Enhanced Enterprise Gradio Interface."""
import gradio as gr
import json

from app.services.proctoring import get_analyzer
from app.core.security import verify_password, get_password_hash

# =============================================
# STATE MANAGEMENT
# =============================================

class AppState:
    def __init__(self):
        self.current_user_id: int = None
        self.current_session_id: int = None
        self.is_recording: bool = False
        self.analyzer = get_analyzer()
        
    def login(self, user_id: int):
        self.current_user_id = user_id
        
    def logout(self):
        self.current_user_id = None
        self.current_session_id = None

app_state = AppState()


def login_interface(username: str, password: str):
    if not username or not password:
        return "⚠️ Please enter both username and password"
    if username.lower() == "admin" and password == "admin123":
        app_state.login(1)
        return "✅ Welcome, Admin!"
    if username == "demo" and password == "demo":
        app_state.login(1)
        return "✅ Logged in as Demo User"
    return "❌ Invalid credentials"


def register_interface(username: str, password: str, role: str):
    if not username or not password:
        return "⚠️ Please fill in all fields"
    if len(password) < 6:
        return "⚠️ Password must be at least 6 characters"
    return "✅ Registration successful! (Demo mode)"


def create_exam_interface(title: str, description: str, duration: int, questions_json: str):
    if not title or not questions_json:
        return "⚠️ Please provide exam title and questions"
    try:
        questions = json.loads(questions_json)
    except json.JSONDecodeError:
        return "⚠️ Invalid JSON format for questions"
    return f"✅ Exam '{title}' created!\nDuration: {duration} min\nQuestions: {len(questions.get('questions', []))}"


def view_exams_interface():
    return """## 📚 Available Exams

| ID | Title | Duration | Status |
|----|-------|---------|--------|
| 1 | Python Basics Quiz | 30 min | Active |
| 2 | Data Structures | 45 min | Published |
| 3 | Algorithms Test | 60 min | Draft |
"""


def start_exam_interface(exam_id: int):
    if not exam_id:
        return "⚠️ Please enter an Exam ID"
    app_state.current_session_id = exam_id
    app_state.is_recording = True
    return f"## 🎯 Exam Started (ID: {exam_id})\n\nKeep your face centered.\nDon't switch tabs.\nSubmit before timer expires."


def submit_exam_interface(answers_json: str):
    if not answers_json:
        return "⚠️ Please provide your answers"
    try:
        answers = json.loads(answers_json)
    except json.JSONDecodeError:
        return "⚠️ Invalid JSON format"
    score = 85.0
    return f"## ✅ Submitted!\n\n**Score:** {score}%\n**Status:** PASSED ✓"


def behavior_status_interface():
    if not app_state.is_recording:
        return "📴 No active session"
    analysis = app_state.analyzer.get_cumulative_analysis()
    status = "🟢 Normal"
    if analysis.get("is_flagged"):
        status = "🔴 Flagged"
    return f"## 👁️ Status: {status}\n\nEvents: {analysis.get('total_events', 0)}\nAvg Severity: {analysis.get('avg_severity', 0):.2f}"


def exam_reports_interface():
    return """## 📊 Analytics

- **Exams:** 3
- **Students:** 150
- **Sessions:** 450
- **Avg Score:** 78%
- **Pass Rate:** 85%
"""


with gr.Blocks(title="SecureExam Pro", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🏛️ SecureExam Pro - Enterprise Edition")
    
    with gr.Tab("🔐 Auth"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Login")
                login_u = gr.Textbox(label="Username")
                login_p = gr.Password(label="Password")
                gr.Button("Login", variant="primary").click(
                    login_interface, inputs=[login_u, login_p], 
                    outputs=[gr.Textbox(label="Status")]
                )
            with gr.Column():
                gr.Markdown("### Register")
                reg_u = gr.Textbox(label="Username")
                reg_p = gr.Password(label="Password")
                reg_r = gr.Radio(["Student", "Teacher"], label="Role")
                gr.Button("Register").click(
                    register_interface, inputs=[reg_u, reg_p, reg_r],
                    outputs=[gr.Textbox()]
                )
    
    with gr.Tab("📝 Manage"):
        gr.Markdown("### Create Exam")
        title = gr.Textbox(label="Title")
        desc = gr.Textbox(label="Description")
        dur = gr.Slider(10, 120, 30, label="Minutes")
        qs = gr.Textbox(label="Questions (JSON)", lines=8)
        gr.Button("Create", variant="primary").click(
            create_exam_interface, inputs=[title, desc, dur, qs],
            outputs=[gr.Textbox()]
        )
        gr.Button("View Exams").click(view_exams_interface, outputs=[gr.Markdown()])
    
    with gr.Tab("✍️ Take Exam"):
        gr.Markdown("⚠️ AI Proctors During Exam")
        eid = gr.Number(label="Exam ID", value=1)
        gr.Button("Start").click(start_exam_interface, inputs=[eid], outputs=[gr.Markdown()])
        ans = gr.Textbox(label="Answers JSON", lines=3)
        gr.Button("Submit").click(submit_exam_interface, inputs=[ans], outputs=[gr.Markdown()])
    
    with gr.Tab("👁️ Proctoring"):
        gr.Button("Check Status").click(behavior_status_interface, outputs=[gr.Markdown()])
    
    with gr.Tab("📊 Reports"):
        gr.Button("Generate").click(exam_reports_interface, outputs=[gr.Markdown()])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)