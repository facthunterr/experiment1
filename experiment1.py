import os
import json
import requests
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Google Fact Check Tools API key
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')

# Bard AI API key
BARD_AI_API_KEY = os.environ.get('BARD_AI_API_KEY')

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Create a Telegram bot
updater = Updater(token=TELEGRAM_BOT_TOKEN)
dispatcher = updater.dispatcher

# Define a command handler for the /factcheck command
def factcheck(update, context):
    # Get the user's input
    input_text = update.message.text
    input_text = input_text.replace('/factcheck ', '')

    try:
        # Check if the input is a URL
        if input_text.startswith('http'):
            # Use the Google Fact Check Tools API to verify the claim
            url = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
            params = {
                'key': GOOGLE_FACT_CHECK_API_KEY,
                'query': input_text
            }
            response = requests.get(url, params=params)
            data = response.json()

            # Check if the API returned any results
            if data.get('claims'):
                # Get the first claim
                claim = data['claims'][0]

                # Get the claim's rating
                rating = claim['claimReview']['textualRating']

                # Get the claim's review
                review = claim['claimReview']['textualReview']

                # Send the response to the user
                update.message.reply_text(f"Claim: {claim['text']}\nRating: {rating}\nReview: {review}")
            else:
                raise ValueError("No results found.")
        else:
            # Use Bard AI to verify the claim
            url = 'https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {BARD_AI_API_KEY}'
            }
            data = {
                'prompt': {
                    'text': f"Is the following claim true or false? {input_text}"
                }
            }
            response = requests.post(url, headers=headers, json=data)
            data = response.json()

            # Get the Bard AI response
            response = data['candidates'][0]['output']

            # Send the response to the user
            update.message.reply_text(f"Bard AI response: {response}")

    except Exception as e:
        # Handle exceptions and inform the user
        update.message.reply_text(f"An error occurred: {str(e)}")

# Add the command handler to the dispatcher
dispatcher.add_handler(CommandHandler('factcheck', factcheck))

# Start the bot
updater.start_polling()
updater.idle()
