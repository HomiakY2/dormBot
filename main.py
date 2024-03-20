# -*- coding: utf-8 -*-
import logging
import os
from telegram-bot import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, Application
from datetime import datetime, time
from zoneinfo import ZoneInfo
from datetime import timedelta

# Set up logging
logger = logging.getLogger('user_actions')
logger.setLevel(logging.INFO)  # D://c for university//2 семестр лабки//Курсова ООП//user_actions.log

# Create a file handler
handler = logging.FileHandler("user_actions.log")
handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)

def log_user_action(update, command):
    user_id = update.effective_user.id
    action = f"User {user_id} issued command {command}"
    logger.info(action)


# Initialize the shopping list as an empty list
def load_list_from_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return [line.strip() for line in file.readlines()]
    else:
        return []


SHOPPING_LIST_FILE = 'shopping_list.txt'
QUEUE_LIST_FILE = 'queue_list.txt'
WATER_LIST_FILE = 'water_list.txt'

shopping_list = load_list_from_file(SHOPPING_LIST_FILE)
queue = load_list_from_file(QUEUE_LIST_FILE)
water = load_list_from_file(WATER_LIST_FILE)
repeating_job = None
repeating_job_water = None


def get_next_run_time(hours=24):
    # Get the current time
    now = datetime.now()
    # Calculate the next run time
    next_run_time = datetime(now.year, now.month, now.day, 12) + timedelta(hours=hours)
    # If the next run time is in the past, add 24 hours to it
    if next_run_time <= now:
        next_run_time += timedelta(hours=24)
    return next_run_time


async def complete_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global repeating_job
    # If the repeating job is currently running, stop it
    if repeating_job is not None:
        repeating_job.schedule_removal()
        repeating_job = None
        if queue:
            queue.append(queue.pop(0))
            await save_list_to_file(queue, QUEUE_LIST_FILE)
        log_user_action(update, '/complete')
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Черга успішно виконана!")
        # Schedule the next message at 12:00 in 48 hours
        next_run_time = get_next_run_time(hours=48)
        repeating_job = job_queue.run_once(callback_minute, next_run_time)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Черга сьогодні вже виконана!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, '/start')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вітаю тебе у боті для управління завданнями та планування у спільному житловому середовищі")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введи в чат '/' для списку всіх можливостей бота")


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, '/command')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="/start - привітання від бота \n/add - додати товар \n/del - видалити товар \n/list - переглянути список \n/clear - очистити список покупок \n/qadd - додати людину до черги(прибирання) \n/qdel - видалити людину з черги(прибирання) \n/qlist - переглянути список черги(прибирання) \n/swap - введіть два індекса для свапу людей(прибирання) \n/wswap - введіть два індекса для свапу людей(вода) \n/wclear - очистити чергу на воду \n/wadd - додати людину до черги(вода) \n/wdel - видалити людину з черги(вода) \n/wlist - переглянути список черги(вода) \n/skip - відкласти прибирання на 1 день \n/complete - підтвердити виконання прибирання \n/improve - отримати контакти розробника для пропозицій \n/command - вивід всіх команд бота")


async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global repeating_job
    # If the repeating job is currently running, stop it
    if repeating_job is not None:
        repeating_job.schedule_removal()
        repeating_job = None
        log_user_action(update, '/skip')
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Черга успішно пропущена!")
        # Schedule the next message at 12:00 tomorrow
        next_run_time = get_next_run_time(hours=24)
        repeating_job = job_queue.run_once(callback_minute, next_run_time)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Черга сьогодні вже пропущена!")


async def save_list_to_file(list_to_save, file_name):
    # Save the list to the file
    with open(file_name, 'w') as file:
        for item in list_to_save:
            file.write(item + '\n')


async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear the shopping list
    shopping_list.clear()
    log_user_action(update, '/clear')
    await save_list_to_file(shopping_list, SHOPPING_LIST_FILE)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Список покупок очищений.")
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


async def clear_water_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear the shopping list
    water.clear()
    log_user_action(update, '/wclear')
    await save_list_to_file(water, WATER_LIST_FILE)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Список черги на воду очищений.")
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


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
            await save_list_to_file(shopping_list, SHOPPING_LIST_FILE)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Добавлено '{item}' до списку покупок.")
        elif command == 'del':
            # Remove the item from the shopping list by index
            try:
                index = int(update.message.text) - 1
                item = shopping_list.pop(index)
                await save_list_to_file(shopping_list, SHOPPING_LIST_FILE)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Видалено '{item}' зі списку покупок.")
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Вказано неправильний індекс!")

        if command == 'qadd':
            # Add the item to the shopping list
            item = update.message.text
            queue.append(item)
            await save_list_to_file(queue, QUEUE_LIST_FILE)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Людину '{item}' додано до черги.")
        elif command == 'qdel':
            # Remove the item from the queue by index
            try:
                index = int(update.message.text) - 1
                item = queue.pop(index)
                await save_list_to_file(queue, QUEUE_LIST_FILE)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Людину '{item}' вилучено з черги.")
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Вказано неправильний індекс!")

        if command == 'wadd':
            # Add the item to the shopping list
            item = update.message.text
            water.append(item)
            await save_list_to_file(water, WATER_LIST_FILE)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Людину '{item}' додано до черги.")
        elif command == 'wdel':
            # Remove the item from the queue by index
            try:
                index = int(update.message.text) - 1
                item = water.pop(index)
                await save_list_to_file(water, WATER_LIST_FILE)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Людину '{item}' вилучено з черги.")
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Вказано неправильний індекс!")

        if command == 'swap':
            # Swap the people in the queue by indices
            try:
                index1, index2 = map(int, update.message.text.split())
                queue[index1 - 1], queue[index2 - 1] = queue[index2 - 1], queue[index1 - 1]
                await save_list_to_file(queue, QUEUE_LIST_FILE)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Помінялися люди на позиціях {index1} та {index2} у черзі.")
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Надані невірні індекси в черзі.")

        if command == 'wswap':
            # Swap the people in the queue by indices
            try:
                index1, index2 = map(int, update.message.text.split())
                water[index1 - 1], water[index2 - 1] = water[index2 - 1], water[index1 - 1]
                await save_list_to_file(water, WATER_LIST_FILE)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Помінялися люди на позиціях {index1} та {index2} у черзі.")
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Надані невірні індекси в черзі.")

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


async def send_shopping_list(context: ContextTypes.DEFAULT_TYPE):
    # Check if the shopping list is empty
    if not shopping_list:
        await context.bot.send_message(chat_id=context.job.context, text="Список покупок порожній.")
    else:
        # Send the current shopping list with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(shopping_list))
        await context.bot.send_message(chat_id=context.job.context, text=message)


async def send_water_list(context: ContextTypes.DEFAULT_TYPE):
    # Check if the shopping list is empty
    if not water:
        await context.bot.send_message(chat_id=context.job.context, text="Список покупок порожній.")
    else:
        # Send the current shopping list with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(water))
        await context.bot.send_message(chat_id=context.job.context, text=message)


async def send_queue(context: ContextTypes.DEFAULT_TYPE):
    # Check if the queue is empty
    if not queue:
        await context.bot.send_message(chat_id=context.job.context, text="Список черги порожній.")
    else:
        # Send the current shopping list with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(queue))
        await context.bot.send_message(chat_id=context.job.context, text=message)


async def swap_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Display the current queue
    queue_message = await view_queue(update, context)
    # Request the indices of the people to swap from the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Введіть по порядку 2 індекси, які ви хочете поміняти місцями:")
    log_user_action(update, '/swap')
    context.user_data['command'] = 'swap'
    context.user_data['message_to_delete'] = message.message_id
    # Delete the command message (/swap)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    # Return the queue message to delete
    return queue_message


async def swap_people_for_water(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Display the current queue
    water_message = await view_water(update, context)
    # Request the indices of the people to swap from the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Введіть по порядку 2 індекси, які ви хочете поміняти місцями:")
    log_user_action(update, '/wswap')
    context.user_data['command'] = 'wswap'
    context.user_data['message_to_delete'] = message.message_id
    # Delete the command message (/swap)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    # Return the queue message to delete
    return water_message


async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the shopping list is empty
    if not shopping_list:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Список покупок порожній.")
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Черга порожня.")
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


async def view_water(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the queue is empty
    if not water:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Черга порожня.")
    else:
        # Send the current queue with indices
        message = "\n".join(f"{i + 1}: {item}" for i, item in enumerate(water))
        water_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        # Store the list message in user data
        context.user_data['queue_message_to_delete'] = water_message

        # Return the list message
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return water_message
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


async def callback_minute(context):
    if not queue:
        await context.bot.send_message(chat_id='@hostel5517', text='Черга порожня.')
    else:
        # Send the person at the first index of the queue
        message = f"Чому кімната не прибрана, {queue[0]}?"
        await context.bot.send_message(chat_id='@hostel5517', text=message)


async def callback_repeat(context):
    global repeating_job
    repeating_job = job_queue.run_repeating(callback_minute, interval=20, first=1)


async def for_fun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global repeating_job
    repeating_job = job_queue.run_repeating(callback_minute, interval=20, first=1)


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the command that was issued
    command = update.message.text.split()[0].split('@')[0][1:]
    # Check the command and set the appropriate value in context.user_data['command']
    if command == 'add':
        message_text = "Введіть предмет для додавання:"
        log_user_action(update, '/add')
        context.user_data['command'] = 'add'
    elif command == 'qadd':
        message_text = "Введіть людину для додавання:"
        log_user_action(update, '/qadd')
        context.user_data['command'] = 'qadd'
    elif command == 'wadd':
        message_text = "Введіть людей для списку черги:"
        log_user_action(update, '/wadd')
        context.user_data['command'] = 'wadd'
    else:
        # If the command is not recognized, return
        return

    # Send the appropriate message to the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
    context.user_data['message_to_delete'] = message.message_id

    # Delete the command message
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the command that was issued
    command = update.message.text.split()[0].split('@')[0][1:]
    # Check the command and set the appropriate value in context.user_data['command']
    if command == 'del':
        await view_list(update, context)
        message_text = "Введіть індекс предмета для видалення:"
        log_user_action(update, '/del')
        context.user_data['command'] = 'del'
    elif command == 'qdel':
        await view_queue(update, context)
        log_user_action(update, '/qdel')
        message_text = "Введіть індекс людини для виводу:"
        context.user_data['command'] = 'qdel'
    elif command == 'wdel':
        await view_water(update, context)
        log_user_action(update, '/wdel')
        message_text = "Введіть індекс предмета для видалення:"
        context.user_data['command'] = 'wdel'
    else:
        # If the command is not recognized, return
        return

    # Send the appropriate message to the user
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
    context.user_data['message_to_delete'] = message.message_id

    # Delete the command message
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the command that was issued

    command = update.message.text.split()[0].split('@')[0][1:]
    # Check the command and set the appropriate value in context.user_data['command']
    if command == 'list':
        log_user_action(update, '/list')
        await view_list(update, context)
    elif command == 'qlist':
        log_user_action(update, '/qlist')
        await view_queue(update, context)
    elif command == 'wlist':
        log_user_action(update, '/wlist')
        await view_water(update, context)
    else:
        # If the command is not recognized, return
        return


async def send_water_message(context: ContextTypes.DEFAULT_TYPE):
    if water:
        # Отримати першу людину зі списку water
        first_person = water[0]
        # Відправити повідомлення про першу людину
        message = f"По воду повинен іти користувач: {first_person}"
        await context.bot.send_message(chat_id='@hostel5517', text=message)


async def water_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global repeating_job_water
    log_user_action(update, '/wstart')
    # Перевірте, чи repeating_job не запущено
    if repeating_job_water is None:
        # Запускаємо повторювану роботу на відправку повідомлення кожну годину
        repeating_job_water = job_queue.run_repeating(send_water_message, interval=5, first=1)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Початок відправки повідомлень про чергу на воду.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Повідомлення про чергу на воду вже відправляються.")


async def improve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_action(update, '/improve')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Якщо у вас є якісь пропозиції для покращення бота, звертайтесь в приватні повідомлення @tesliam")


async def water_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global repeating_job_water
    log_user_action(update, '/wstop')
    # Перевірте, чи repeating_job запущено
    if repeating_job_water is not None:
        # Зупиняємо повторювану роботу
        repeating_job_water.schedule_removal()
        repeating_job_water = None
        # Переміщуємо першу людину в кінець списку
        if water:
            first_person = water.pop(0)
            water.append(first_person)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Зупинено відправку повідомлень про чергу на воду.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Відправка повідомлень про чергу на воду не запущена.")


if __name__ == '__main__':
    application = ApplicationBuilder().token('6254290442:AAE0yr5QjX_Rxft3Am-zAtbTsNLcUDtkxm4').build()

    t = time(12, 00, 00, 000000, tzinfo=ZoneInfo("Europe/Kyiv"))
    job_queue = application.job_queue
    job_queue.run_daily(callback_repeat, t)

    start_queue = CommandHandler('qstart', for_fun)
    start_handler = CommandHandler('start', start)
    skip_handler = CommandHandler('skip', skip)
    clear_list_handler = CommandHandler('clear', clear_list)
    swap_people_handler = CommandHandler('swap', swap_people)
    swap_people_for_water_handler = CommandHandler('wswap', swap_people_for_water)
    complete_queue_handler = CommandHandler('complete', complete_queue)
    clear_water_handler = CommandHandler('wclear', clear_water_list)
    add_handler = CommandHandler(['add', 'qadd', 'wadd'], add)
    delete_handler = CommandHandler(['del', 'qdel', 'wdel'], delete)
    list_handler = CommandHandler(['list', 'qlist', 'wlist'], list)
    water_start_handler = CommandHandler('wstart', water_start)
    water_stop_handler = CommandHandler('wstop', water_stop)
    improve_handler = CommandHandler('improve', improve_command)
    command_handler = CommandHandler('command', command)

    message_handler = MessageHandler(None, handle_message)

    application.add_handler(command_handler)
    application.add_handler(start_queue)
    application.add_handler(start_handler)
    application.add_handler(water_start_handler)
    application.add_handler(improve_handler)
    application.add_handler(water_stop_handler)
    application.add_handler(list_handler)
    application.add_handler(swap_people_for_water_handler)
    application.add_handler(delete_handler)
    application.add_handler(add_handler)
    application.add_handler(skip_handler)
    application.add_handler(clear_list_handler)
    application.add_handler(swap_people_handler)
    application.add_handler(complete_queue_handler)
    application.add_handler(clear_water_handler)
    application.add_handler(message_handler)

    application.run_polling()
