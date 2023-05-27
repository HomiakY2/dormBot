import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize the shopping list as an empty list
shopping_list = []
SHOPPING_LIST_FILE = 'shopping_list.txt'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


if os.path.exists(SHOPPING_LIST_FILE):
    with open(SHOPPING_LIST_FILE, 'r') as file:
        shopping_list = [line.strip() for line in file.readlines()]
else:
    shopping_list = []


async def save_shopping_list():
    # Save the shopping list to the file
    with open(SHOPPING_LIST_FILE, 'w') as file:
        for item in shopping_list:
            file.write(item + '\n')


async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear the shopping list
    shopping_list.clear()
    await save_shopping_list()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cleared the shopping list.")
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Request the item to add from the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the item to add:")
    context.user_data['command'] = 'add'
    context.user_data['message_to_delete'] = message.message_id
    # Delete the command message (/add)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Display the current shopping list
    list_message = await view_list(update, context)
    # Request the index of the item to delete from the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Enter the index of the item to delete:")
    context.user_data['command'] = 'del'
    context.user_data['message_to_delete'] = message.message_id
    # Delete the command message (/del)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    # Return the list message to delete
    return list_message


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Process user's message based on the command
    command = context.user_data.get('command')
    if command == 'add':
        # Add the item to the shopping list
        item = update.message.text
        shopping_list.append(item)
        await save_shopping_list()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Added '{item}' to the shopping list.")
    elif command == 'del':
        # Remove the item from the shopping list by index
        try:
            index = int(update.message.text) - 1
            item = shopping_list.pop(index)
            await save_shopping_list()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Removed '{item}' from the shopping list.")
        except (ValueError, IndexError):
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Invalid index provided or item not found in the shopping list.")

    # Delete the command message and related messages
    command_message_id = context.user_data.get('message_to_delete')
    if command_message_id:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=command_message_id)
    list_message = context.user_data.pop('list_message_to_delete', None)
    if list_message:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=list_message.message_id)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

    # Clear the command and message to delete from user data
    context.user_data.pop('command', None)
    context.user_data.pop('message_to_delete', None)


async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the shopping list is empty
    if not shopping_list:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The shopping list is empty.")
    else:
        # Send the current shopping list with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(shopping_list))
        list_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        # Store the list message in user data
        context.user_data['list_message_to_delete'] = list_message

        # Return the list message
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return list_message
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


if __name__ == '__main__':
    application = ApplicationBuilder().token('6199978304:AAFnQ5r1POtsFCbr2gZPpFyKD1YdQJHKfgs').build()

    start_handler = CommandHandler('start', start)
    add_item_handler = CommandHandler('add', add_item)
    delete_item_handler = CommandHandler('del', delete_item)
    view_list_handler = CommandHandler('list', view_list)
    clear_list_handler = CommandHandler('clear', clear_list)
    message_handler = MessageHandler(None, handle_message)

    application.add_handler(start_handler)
    application.add_handler(add_item_handler)
    application.add_handler(delete_item_handler)
    application.add_handler(view_list_handler)
    application.add_handler(clear_list_handler)
    application.add_handler(message_handler)

    application.run_polling()
