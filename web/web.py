import gradio as gr
import requests

API_URL = "http://api:8000"  

def redact_text(user_input):
    try:
        response = requests.post(f"{API_URL}/redact", json={"text": user_input}, timeout=10)
        return response.json().get("redacted", "Error: No redacted text found.")
    except requests.exceptions.RequestException:
        return "Error: Unable to connect to API."

def get_history():
    try:
        response = requests.get(f"{API_URL}/history", timeout=5)
        history_data = response.json()
        return "\n".join([f"{item['id']}: {item['user_input']} -> {item['redacted_text']}" for item in history_data])
    except requests.exceptions.RequestException:
        return "Error: Unable to fetch history."

with gr.Blocks() as demo:
    gr.Markdown("# PII Detection & Redaction Web App")

    with gr.Row():
        input_text = gr.Textbox(label="Enter Text", placeholder="Type here...")
        output_text = gr.Textbox(label="Redacted Result")

    redact_button = gr.Button("Redact Text")
    redact_button.click(fn=redact_text, inputs=input_text, outputs=output_text)

    with gr.Row():
        history_button = gr.Button("View History")
        history_output = gr.Textbox(label="History", interactive=False)

    history_button.click(fn=get_history, outputs=history_output)

demo.launch(server_name="0.0.0.0", server_port=7860)
