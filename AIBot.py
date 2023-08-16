
import requests
import json
import time
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram import ParseMode, InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext.filters import Filters
from telegram.ext import Updater, CommandHandler, MessageHandler

from telegram import LabeledPrice, ParseMode
from telegram.ext import PreCheckoutQueryHandler

updater = Updater("6383862027:AAGqH0gFFf-KFhrJpqW6AKdfr1qlsD9X4fo",
				use_context=True)
users=[]


STRIPE_TOKEN = "284685063:TEST:ZjdiNWRkYmI5NDYz"
with open("shifu/users.txt") as userfile :
    for line in userfile:
        # remove linebreak from a current name
        # linebreak is the last character of each line
        x = line[:-1]

        # add current item to the list
        users.append(x)

# display list
userfile.close()
PRICE = 500

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
        update.message.reply_text("Good day Sir.")

def help(update: Update, context: CallbackContext):
	update.message.reply_text("""Available Commands :-
	/start - Gatekeeping. To check if you can continue to use the bot.
	/subscribe - 
or simply chat if you are subscribed! """)

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
    with open("shifu/users.txt") as userfile :
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
    #config_IDs.insert(0,context.args[0])
    # open file in write mode
        # open file and read the content in a list
    users = []
    with open("shifu/users.txt") as userfile :
        for line in userfile:
            # remove linebreak from a current name
            # linebreak is the last character of each line
            x = line[:-1]

            # add current item to the list
            users.append(x)
    userfile.close()
    users.append(context.args[0])
    # display list

    with open(r'shifu/users.txt', 'w') as userfile:
        for item in users:
            # write each item on a new line
            userfile.write("%s\n" % item)
        #print('Done')
    #print (context.args[0])
    userfile.close()
    update.message.reply_text("Bot Users: {}".format(users))    

#def unknown(update: Update, context: CallbackContext):
#	update.message.reply_text(
#		"Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext): #chats with verified user is here
    if (update.message.from_user['id'] == 5229876508):
        update.message.reply_text(update.message.text)
    
def _add_handlers(updater):
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('subscribe', subscribe))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    updater.dispatcher.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters._SuccessfulPayment, successful_payment_callback))
    #Admin
    updater.dispatcher.add_handler(CommandHandler('addWL', addWL))

#updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
#updater.dispatcher.add_handler(MessageHandler(
#	Filters.command, unknown)) # Filters out unknown commands

# Filters out unknown messages.
    updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))


if __name__ == "__main__":
    _add_handlers(updater)
    print("starting to poll...")
    updater.start_polling()