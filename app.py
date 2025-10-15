import os
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
# ✅ Cấu hình lại đúng cú pháp mới nhất của Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ⚠️ Dùng đúng tên model hiện có, không cần chữ 'models/'
MODEL_NAME = "gemini-1.5-flash"  # hoặc gemini-1.5-pro nếu bạn cần kết quả chi tiết hơn

PROMPT_TEMPLATE = """
Bạn là một trợ lý AI chuyên tạo kịch bản video dưới dạng JSON.
Hãy đọc đoạn transcript và chia nó thành các cảnh (scene) với cấu trúc JSON như sau:
[
  {{
    "scene_id": "scene_1",
    "setting": "Miêu tả bối cảnh",
    "time": "Thời gian trong ngày",
    "location": "Vị trí",
    "characters": [{{"name": "Tên", "description": "Miêu tả"}}],
    "dialogue": "Lời thoại chính trong cảnh"
  }}
]
Sử dụng mô tả nhân vật nếu được cung cấp.
Transcript: {transcript}
Mô tả nhân vật: {character_description}
"""

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    transcript = data.get('transcript')
    char_desc = data.get('character_description', 'Không có')

    if not transcript:
        return jsonify({"error": "Transcript không được để trống"}), 400

    prompt = PROMPT_TEMPLATE.format(transcript=transcript, character_description=char_desc)

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Làm sạch kết quả JSON
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1]

        try:
            data_json = json.loads(text)
        except:
            data_json = {"raw_text": text}

        return jsonify(data_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

