
import requests
import json
import time
from telegram import Update
from telegram.ext import CallbackContext
from telegram import ParseMode, InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext.filters import Filters
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler

from telegram import LabeledPrice, ParseMode
from telegram.ext import PreCheckoutQueryHandler
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the tokens from the environment variables
bot_token = os.getenv('BOT_TOKEN')
stripe_token = os.getenv('STRIPE_TOKEN')
API_BASE_URL = "localhost:5000" # Replace accordingly
influencer = "fabian" # Replace accordingly

# State for checking if the user is in conversation
LISTENING = 1

updater = Updater(bot_token,
				use_context=True)
users=[]

STRIPE_TOKEN = stripe_token
PRICE = 500

if not os.path.exists("users.txt"):
    # If it doesn't exist, create it
    with open("users.txt", "w") as userfile:
        userfile.write("")  # This will create an empty file

with open("users.txt") as userfile :
    for line in userfile:
        # remove linebreak from a current name
        # linebreak is the last character of each line
        x = line[:-1]

        # add current item to the list
        users.append(x)

# display list
userfile.close()

keyboard = [[InlineKeyboardButton("Refresh", callback_data="1")]]
 
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in users:
        print("WARNING: Unauthorized access denied for {}.".format(user_id))
        reply_markup = InlineKeyboardMarkup(keyboard)
        #update.message.sendPhoto(chat_id=chat_id, photo="img.png", caption="This is the test photo caption")
        update.message.reply_text("""
            Hey, you need to subscribe. """)
        #return  # quit function
    else:
        # # Initialize chat in the backend by calling the API
        # response = requests.post(f"{API_BASE_URL}/startChat?user={user_id}&influencer={influencer}")
        # if response.status_code == 200:
        #     # Successful connection to the API and chat initialized
        #     update.message.reply_text(response.text)
        # else:
        #     # Handle error
        #     update.message.reply_text("Error initializing chat.")
        update.message.reply_text("Hello started")
        return LISTENING
    
# Constantly listens for text after /start
def listen(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_input = update.message.text
    update.message.reply_text(f"You said: {user_input}") # For debugging
    # data = {
    #     "message": user_input
    # }
    # response = requests.post(f"{API_BASE_URL}/chat?user={user_id}&influencer={influencer}", json=data)

    # # Check if the request was successful (HTTP 200 status)
    # if response.status_code == 200:
    #     json_response = response.json()

    #     # Assuming the API returns a JSON object with a "Message" key
    #     api_message = json_response.get("Message", "Sorry, I didn't understand that.")

    #     # Reply to the user with the message from the API
    #     update.message.reply_text(api_message)
    # else:
    #     # Handle API errors (e.g., if the API is down or returns an error code)
    #     update.message.reply_text("Sorry, I'm having some issues right now. Please try again later.")
    return LISTENING

def help(update: Update, context: CallbackContext):
	update.message.reply_text("""Available Commands :-
	/start - Gatekeeping. To check if you can continue to use the bot.
	/subscribe - 
    or simply chat if you are subscribed! """)

def save(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    # response = requests.post(f"{API_BASE_URL}/save?user={user_id}&influencer={influencer}")
    # if response.status_code == 200:
    #     # Successfully saved
    #     update.message.reply_text("Chat has been saved successfully.")
    #     return ConversationHandler.END
    # else:
    #     # Handle error
    #     update.message.reply_text("Error saving chat.")
    #     return LISTENING
    update.message.reply_text("Saved")
    return ConversationHandler.END


def subscribe(update: Update, context: CallbackContext):
    out = context.bot.send_invoice(
        chat_id=update.message.chat_id,
        title="Subscribe",
        description="Amount payable for 1 month usage",
        payload="Chat with Fabian",
        provider_token=STRIPE_TOKEN,
        currency="SGD",
        prices=[LabeledPrice("Pay", PRICE)],
        need_name=False,
    )

def pre_checkout_handler(update: Update, context: CallbackContext):
    """https://core.telegram.org/bots/api#answerprecheckoutquery"""
    query = update.pre_checkout_query
    query.answer(ok=True)
    
def successful_payment_callback(update: Update, context):
    #add to user db
    update.message.reply_text("Thank you for subscribing! You may continue chatting")

   
#Admin Functions
def checkSub(update: Update, context: CallbackContext): 
    users = []
    # open file and read the content in a list
    with open("users.txt") as userfile :
        for line in userfile:
            # remove linebreak from a current name
            # linebreak is the last character of each line
            x = line[:-1]

            # add current item to the list
            users.append(x)

    # display list
    userfile.close()
    update.message.reply_text("Bot Users: {}".format(users))
	#update.message.reply_text("Bot Users: {}".format(config_IDs))
    
def addWL(update: Update, context: CallbackContext):
    users = []
    with open("users.txt") as userfile:
        for line in userfile:
            x = line[:-1]
            users.append(x)
    userfile.close()

    new_user_id = context.args[0]
    if new_user_id not in users:
        users.append(new_user_id)
        with open(r'users.txt', 'w') as userfile:
            for item in users:
                userfile.write("%s\n" % item)
        userfile.close()
        print("User added. Current users:", users) # Print users to console
        update.message.reply_text("User added successfully.")
    else:
        print("User already exists in the list. Current users:", users) # Print users to console
        update.message.reply_text("User already exists in the list.")

def unknown_text(update: Update, context: CallbackContext): #chats with verified user is here
    if (update.message.from_user['id'] == 5229876508):
        update.message.reply_text(update.message.text)
    
def _add_handlers(updater):
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LISTENING: [MessageHandler(Filters.text & ~Filters.command, listen)]
        },
        fallbacks=[CommandHandler('save', save)]
    )

    updater.dispatcher.add_handler(conversation_handler)

    updater.dispatcher.add_handler(CommandHandler('subscribe', subscribe))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    updater.dispatcher.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters._SuccessfulPayment, successful_payment_callback))
    
    #Admin
    updater.dispatcher.add_handler(CommandHandler('addWL', addWL))

    # Filters out unknown messages.
    updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))


if __name__ == "__main__":
    _add_handlers(updater)
    print("starting to poll...")
    updater.start_polling()