import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, Application
from datetime import time
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize the shopping list as an empty list
shopping_list = []
queue = []
SHOPPING_LIST_FILE = 'shopping_list.txt'
QUEUE_LIST_FILE = 'queue_list.txt'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    job_repeat.enabled = False


if os.path.exists(SHOPPING_LIST_FILE):
    with open(SHOPPING_LIST_FILE, 'r') as file:
        shopping_list = [line.strip() for line in file.readlines()]
else:
    shopping_list = []

if os.path.exists(QUEUE_LIST_FILE):
    with open(QUEUE_LIST_FILE, 'r') as file:
        queue = [line.strip() for line in file.readlines()]
else:
    queue = []


async def save_shopping_list():
    # Save the shopping list to the file
    with open(SHOPPING_LIST_FILE, 'w') as file:
        for item in shopping_list:
            file.write(item + '\n')


async def save_queue_list():
    # Save the shopping list to the file
    with open(QUEUE_LIST_FILE, 'w') as file:
        for item in queue:
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


async def add_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Request the item to add from the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the people to add:")
    context.user_data['command'] = 'qadd'
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


async def delete_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Display the current shopping list
    queue_message = await view_queue(update, context)
    # Request the index of the item to delete from the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Enter the index of the peole to delete:")
    context.user_data['command'] = 'qdel'
    context.user_data['message_to_delete'] = message.message_id
    # Delete the command message (/qdel)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    # Return the list message to delete
    return queue_message


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Process user's message based on the command
    if 'command' not in context.user_data:
        # No command has been issued, so ignore the message
        return
    command = context.user_data.get('command')
    if command is not None:
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

        if command == 'qadd':
            # Add the item to the shopping list
            item = update.message.text
            queue.append(item)
            await save_queue_list()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Added '{item}' to the queue.")
        elif command == 'qdel':
            # Remove the item from the queue by index
            try:
                index = int(update.message.text) - 1
                item = queue.pop(index)
                await save_queue_list()
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Removed '{item}' from the queue.")
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Invalid index provided or item not found in the queue.")

        if command == 'swap':
            # Swap the people in the queue by indices
            try:
                index1, index2 = map(int, update.message.text.split())
                queue[index1 - 1], queue[index2 - 1] = queue[index2 - 1], queue[index1 - 1]
                await save_queue_list()
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Swapped people at positions {index1} and {index2} in the queue.")
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Invalid indices provided or people not found in the queue.")

        # Delete the command message and related messages

        command_message_id = context.user_data.get('message_to_delete')
        if command_message_id:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=command_message_id)
        list_message = context.user_data.pop('list_message_to_delete', None)
        if list_message:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=list_message.message_id)
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

        # queue_message = context.user_data.pop('queue_message_to_delete', None)
        # if queue_message:
        #     await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=list_message.message_id)
        # await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


        # Clear the command and message to delete from user data
        context.user_data.pop('command', None)
        context.user_data.pop('message_to_delete', None)


async def send_shopping_list(context: ContextTypes.DEFAULT_TYPE):
    # Check if the shopping list is empty
    if not shopping_list:
        await context.bot.send_message(chat_id=context.job.context, text="The shopping list is empty.")
    else:
        # Send the current shopping list with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(shopping_list))
        await context.bot.send_message(chat_id=context.job.context, text=message)


async def send_queue(context: ContextTypes.DEFAULT_TYPE):
    # Check if the queue is empty
    if not queue:
        await context.bot.send_message(chat_id=context.job.context, text="The queue list is empty.")
    else:
        # Send the current shopping list with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(queue))
        await context.bot.send_message(chat_id=context.job.context, text=message)


async def swap_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Display the current queue
    queue_message = await view_queue(update, context)
    # Request the indices of the people to swap from the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Enter in order the 2 indexes you want to swap:")
    context.user_data['command'] = 'swap'
    context.user_data['message_to_delete'] = message.message_id
    # Delete the command message (/swap)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    # Return the queue message to delete
    return queue_message


async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the shopping list is empty
    if not shopping_list:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The shopping list is empty.")
    else:
        # Send the current shopping list with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(shopping_list))
        list_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        # Return the list message
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return list_message

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)



async def view_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the queue is empty
    if not queue:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The queue is empty.")
    else:
        # Send the current queue with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(queue))
        queue_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        # Store the list message in user data
        context.user_data['queue_message_to_delete'] = queue_message

        # Return the list message
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return queue_message
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


async def send_first_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the queue is empty
    if not queue:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The queue is empty.")
    else:
        # Send the person at the first index of the queue
        message = f"Person at the first index of the queue: {queue[0]}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def callback_minute(context):
    if not queue:
        await context.bot.send_message(chat_id='@hostel5517', text='The queue is empty.')
    else:
        # Send the person at the first index of the queue
        message = f"Person at the first index of the queue: {queue[0]}"
        await context.bot.send_message(chat_id='@hostel5517', text=message)


async def callback_repeat(context):
    job_minute = job_queue.run_repeating(callback_minute, interval=10, first=1)


if __name__ == '__main__':
    application = ApplicationBuilder().token('6254290442:AAE0yr5QjX_Rxft3Am-zAtbTsNLcUDtkxm4').build()
    job_queue = application.job_queue
    #job_minute = job_queue.run_repeating(callback_minute, interval=10, first=1)

    timer = time(hour=21, minute=36, second=00)
    #timer = time(11, 34, 56)
    #print(time)
    job_repeat = job_queue.run_daily(callback_repeat, time(hour=21, minute=39, second=30))

    start_handler = CommandHandler('start', start)
    add_item_handler = CommandHandler('add', add_item)
    delete_item_handler = CommandHandler('del', delete_item)
    view_list_handler = CommandHandler('list', view_list)
    clear_list_handler = CommandHandler('clear', clear_list)
    add_people_handler = CommandHandler('qadd', add_people)
    delete_people_handler = CommandHandler('qdel', delete_people)
    view_people_handler = CommandHandler('qlist', view_queue)
    swap_people_handler = CommandHandler('swap', swap_people)
    message_handler = MessageHandler(None, handle_message)

    application.add_handler(start_handler)
    application.add_handler(add_item_handler)
    application.add_handler(delete_item_handler)
    application.add_handler(view_list_handler)
    application.add_handler(clear_list_handler)
    application.add_handler(add_people_handler)
    application.add_handler(delete_people_handler)
    application.add_handler(view_people_handler)
    application.add_handler(swap_people_handler)
    application.add_handler(message_handler)

    application.run_polling()