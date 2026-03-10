import os
import gradio as gr
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """
אתה מומחה אבטחה ו-CLI. תפקידך להמיר הוראות לפקודות טרמינל עבור Windows.

חוקים נוקשים:
1. פלט: החזר אך ורק את הפקודה. ללא הסברים, ללא Markdown.
2. אבטחה (קריטי): אם ההוראה כוללת מחיקת קבצי מערכת, פרמוט דיסק, כיבוי/ריסטארט של המחשב, או כל פעולה הרסנית - החזר בדיוק את המילים: "Error: Dangerous command blocked".
3. אי-הבנה: אם ההוראה מעורפלת (כמו 'תסדר בלגן'), החזר: "Error: Instruction unclear".
4. שפה: תמוך בהוראות בעברית ובאנגלית, אך הפלט תמיד יהיה פקודת Windows.
"""


def translate_to_cli(user_input):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nInstruction: {user_input}"}]}]}

    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        response_json = response.json()

        # הדפסה לטרמינל כדי שנוכל לראות מה גוגל אומרת
        print("Response from Google:", response_json)

        if 'error' in response_json:
            return f"שגיאת API: {response_json['error']['message']}"

        if 'candidates' in response_json:
            answer = response_json['candidates'][0]['content']['parts'][0]['text']
            return answer.strip()

        return "השרת החזיר תשובה ריקה - בדקי את תקינות המפתח"
    except Exception as e:
        return f"שגיאה כללית: {str(e)}"

# ממשק Gradio
with gr.Blocks(title="סוכן CLI חכם") as demo:
    gr.Markdown(" 🖥️ סוכן CLI ")
    input_text = gr.Textbox(label="מה תרצו לבצע?")
    output_text = gr.Textbox(label="פקודת ה-CLI:")
    submit_btn = gr.Button("צור פקודה")
    submit_btn.click(fn=translate_to_cli, inputs=input_text, outputs=output_text)

if __name__ == "__main__":
    demo.launch()