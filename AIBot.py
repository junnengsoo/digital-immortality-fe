
import os

import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, LabeledPrice, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          MessageHandler, PreCheckoutQueryHandler, filters, Application)

# Load the .env file
load_dotenv()

# Get the tokens from the environment variables
bot_token = "6526375040:AAHyjRA67xM5AfbNb0jMWtHwEfdZc5Wg9-M"
stripe_token = "284685063:TEST:ZTYzNTRhN2FmYmQy"
API_BASE_URL = "https://mex.chat/api/v1" # Replace accordingly
influencer = "fabian" # Replace accordingly

# State for checking if the user is in conversation
AWAITING_TEMPERATURE, LISTENING = range(2)

users=[]

STRIPE_TOKEN = stripe_token
PRICE = 500

if not os.path.exists("users.txt"):
    # If it doesn't exist, create it
    with open("users.txt", "w") as userfile:
        userfile.write("")  # This will create an empty file

with open("users.txt") as userfile:
    for line in userfile:
        user_id = line.strip()  # This will remove any leading or trailing whitespace, including newlines
        users.append(user_id)

# display list
userfile.close()

keyboard = [[InlineKeyboardButton("Refresh", callback_data="1")]]
    
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if str(user_id) not in users:
        print("WARNING: Unauthorized access denied for {}.".format(user_id))
        await update.message.reply_text("Hey, you need to subscribe.")
    else:
        await update.message.reply_text("Please enter a temperature value between 0 and 1:")
        return AWAITING_TEMPERATURE

async def get_temperature(update: Update, context: CallbackContext):
    try:
        temperature = float(update.message.text)
        print(temperature)
        if 0 <= temperature <= 1:
            response = requests.post(f"{API_BASE_URL}/startchat?user={update.effective_user.id}&influencer={influencer}&temperature={temperature}", timeout=60)
            if response.status_code == 200:
                await update.message.reply_text(response.text)
            else:
                print(f"Error in start function. Status code: {response.status_code}. Response: {response.text}")
                await update.message.reply_text("Error initializing chat.")
            return LISTENING
        else:
            await update.message.reply_text("Invalid temperature. Please enter a value between 0 and 1:")
            return AWAITING_TEMPERATURE
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a value between 0 and 1:")
        return AWAITING_TEMPERATURE
    
# Constantly listens for text after /start
async def listen(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_input = update.message.text
    # update.message.reply_text(f"You said: {user_input}") # For debugging
    headers = {"Content-Type": "application/json"}
    data = {
        "message": user_input
    }
    response = requests.post(f"{API_BASE_URL}/chat?user={user_id}&influencer={influencer}", json=data, headers=headers, timeout=60)

    # Check if the request was successful (HTTP 200 status)
    if response.status_code == 200:
        json_response = response.json()

        # Assuming the API returns a JSON object with a "Message" key
        api_message = json_response.get("Message", "Sorry, I didn't understand that.")

        # Reply to the user with the message from the API
        await update.message.reply_text(api_message)
    else:
        # Handle API errors (e.g., if the API is down or returns an error code)
        await update.message.reply_text("Sorry, I'm having some issues right now. Please try again later.")
    return LISTENING

async def help(update: Update, context: CallbackContext):
	await update.message.reply_text("""Available Commands :-
	/start - Gatekeeping. To check if you can continue to use the bot.
	/subscribe - 
    or simply chat if you are subscribed! """)

# def save(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     response = requests.post(f"{API_BASE_URL}/save?user={user_id}&influencer={influencer}")
#     if response.status_code == 200:
#         # Successfully saved
#         update.message.reply_text("Chat has been saved successfully.")
#         return ConversationHandler.END
#     else:
#         # Handle error
#         update.message.reply_text("Error saving chat.")
#         return LISTENING
    # update.message.reply_text("Saved")
    # return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END


async def subscribe(update: Update, context: CallbackContext):
    out = await context.bot.send_invoice(
        chat_id=update.message.chat_id,
        title="Subscribe",
        description="Amount payable for 1 month usage",
        payload="Chat with Fabian",
        provider_token=STRIPE_TOKEN,
        currency="SGD",
        prices=[LabeledPrice("Pay", PRICE)],
        need_name=False,
    )

async def pre_checkout_handler(update: Update, context: CallbackContext):
    """https://core.telegram.org/bots/api#answerprecheckoutquery"""
    query = update.pre_checkout_query
    await query.answer(ok=True)
    
async def successful_payment_callback(update: Update, context):
    # Extract user_id from the update
    user_id = update.message.from_user.id

    # Add user_id to users.txt
    with open("users.txt", "a") as file:
        file.write(str(user_id) + '\n')

    users.append(str(user_id))

    await update.message.reply_text("Thank you for subscribing! You may continue chatting")

async def unknown_text(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)  # Convert user_id to string for comparison with users list

    if user_id in users:
        await update.message.reply_text("Please use /start to initiate a chat.")
    else:
        await update.message.reply_text("You need to subscribe to use this bot. Use /subscribe to subscribe.")
   
#Admin Functions
async def checkSub(update: Update, context: CallbackContext): 
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
    await update.message.reply_text("Bot Users: {}".format(users))
	#update.message.reply_text("Bot Users: {}".format(config_IDs))
    
async def addWL(update: Update, context: CallbackContext):
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
        await update.message.reply_text("User added successfully.")
    else:
        print("User already exists in the list. Current users:", users) # Print users to console
        await update.message.reply_text("User already exists in the list.")

if __name__ == "__main__":
    application = Application.builder().token(bot_token).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
        AWAITING_TEMPERATURE: [MessageHandler(filters.ALL, get_temperature)],
        LISTENING: [MessageHandler(filters.ALL, listen)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Filters out unknown messages.
    application.add_handler(MessageHandler(filters.ALL, unknown_text))
    
    print("starting to poll...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)