import json
import logging
import ollama
import requests
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

#Telegram Bot API Key
telegram_bot_api_key = "Your Telegram Bot Token"

# Logging Confuguration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Start Handler
async def start(update: Update, context):
    await update.message.reply_text("Welcome to Evo AI! How can I help you?")
    return

# Info Handler
async def info(update: Update, context):
    await update.message.reply_text("Evo AI is your smart assistant, ready to answer your questions instantly. It can provide responses based on a predefined knowledge base and even generate AI-powered replies when needed. Whether you need quick information or a casual chat, Evo AI is here to help!")
    return

# Get data from json file
def load_json_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: can't get json data!")
        return {"questions": []}
    
# JSON Handler
def get_response_from_json(user_input, json_data):
    for question in json_data['questions']:
        if isinstance(question['question'], list):
            for q in question['question']:
                if q.lower() in user_input.lower():
                    return question['message']
        else:
            if question['question'].lower() in user_input.strip().lower():
                return question['message']
    return None

# Mistral AI Handler
async def get_response_from_mistral(user_input):
    try:
        ai_response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": user_input}]
        )
        return ai_response['message']['content']
    
        # -------------------------------------------------
        # IF YOU ARE USING DOCKER, USE THE CODE BELOW
        # -------------------------------------------------

        # url = "http://172.17.0.2:11434/api/generate"
        # data = {"model": "mistral", "prompt": user_input, "stream": True}
        # async with httpx.AsyncClient(timeout=120) as client:
        #     response = await client.post(
        #         url,
        #         data=json.dumps(data),
        #         headers={'Content-Type': 'Application/json'}
        #     )
        # responses_lines = [line for line in response.text.strip().split('\n') if line]
        # response_dicts = [json.loads(line) for line in responses_lines]
        # return '' .join(response_dict.get('response', '') for response_dict in response_dicts)
    except Exception as e:
        return(f"⚠️ Error while processing AI: {e}")

# Message Handler
async def handle_message(update: Update, context):
    user_input = update.message.text
    logger.info(f"Received '{user_input}' from {update.message.from_user.username}")
    
    json_data = load_json_data()  # Load JSON

    while True:

        if user_input.lower() in ["bye", "exit", "stop"]:
            await update.message.reply_text("Goodbye! If you have any other questions or need further assistance, feel free to ask. Have a great day!")
            return

        response = get_response_from_json(user_input, json_data)
        
        # Response from JSON
        if response:
            await update.message.reply_text(f"{response}")
            return

        # Response from Mistral AI
        else:
            await update.message.reply_text("✨ Evo is working on it, hang tight...")
            response = await get_response_from_mistral(user_input)
            await update.message.reply_text(f"{response}")
            return

# Main Function
def main():

    app = Application.builder().token(telegram_bot_api_key).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Evo AI is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
