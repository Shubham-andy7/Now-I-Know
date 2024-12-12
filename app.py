from flask import Flask, render_template, request, jsonify
from ChatBot import ChatBot
import asyncio

app = Flask(__name__)
chatbot = ChatBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    response = asyncio.run(chatbot.process_message(user_message))
    return jsonify(response)

@app.route('/reset', methods=['POST'])
def reset():
    chatbot.reset_conversation()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
