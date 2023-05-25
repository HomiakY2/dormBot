import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize the shopping list as an empty list
shopping_list = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add the item to the shopping list
    item = ' '.join(context.args)
    shopping_list.append(item)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Added {item} to the shopping list.")

async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Remove the item from the shopping list
    item = ' '.join(context.args)
    if item in shopping_list:
        shopping_list.remove(item)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Removed {item} from the shopping list.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{item} is not in the shopping list.")

async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send the current shopping list
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n".join(shopping_list))

if __name__ == '__main__':
    application = ApplicationBuilder().token('6199978304:AAFnQ5r1POtsFCbr2gZPpFyKD1YdQJHKfgs').build()

    start_handler = CommandHandler('start', start)
    add_item_handler = CommandHandler('add', add_item)
    delete_item_handler = CommandHandler('delete', delete_item)
    view_list_handler = CommandHandler('list', view_list)

    application.add_handler(start_handler)
    application.add_handler(add_item_handler)
    application.add_handler(delete_item_handler)
    application.add_handler(view_list_handler)

    application.run_polling()
