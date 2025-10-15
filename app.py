import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# 1️⃣ Tải biến môi trường
load_dotenv()

# 2️⃣ Cấu hình Flask
app = Flask(__name__)

# 3️⃣ Cấu hình API key Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 4️⃣ Đặt tên model TRƯỚC khi khởi tạo
MODEL_NAME = "gemini-1.5-flash"  # hoặc "gemini-1.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

# 5️⃣ Prompt template
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
        # ✅ Gọi Gemini API
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Làm sạch định dạng JSON
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1]

        # Cố gắng parse JSON
        try:
            data_json = json.loads(text)
        except:
            data_json = {"raw_text": text}

        return jsonify(data_json)

    except Exception as e:
    import traceback
    print("❌ LỖI CHI TIẾT:\n", traceback.format_exc())  # in stack trace ra console
    return jsonify({"error": str(e)}), 500



@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    # 6️⃣ Khởi chạy server
    app.run(host='0.0.0.0', port=5000)

