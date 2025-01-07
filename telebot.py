import datetime
import requests
import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Константы
USER_DATA = {'Taylon': 'kamaz123'}  # Логин: пароль
AUTHORIZED_USERS = set()

# Функция для определения времени суток
def get_time_of_day():
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"

# Функция для получения данных по IP
def get_info_by_ip(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}').json()
        if response.get('status') != 'success':
            return '[!] Неверный IP или данные недоступны [!]'
        return '\n'.join([f'{k}: {v}' for k, v in response.items() if v])
    except requests.RequestException:
        return '[!] Ошибка подключения к серверу [!]'

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greeting = get_time_of_day()
    await update.message.reply_text(f'{greeting}, {update.effective_user.first_name}! Используйте /auth для авторизации.')

async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in AUTHORIZED_USERS:
        await update.message.reply_text('Вы уже авторизованы!')
        return

    if len(context.args) < 2:
        await update.message.reply_text('Введите логин и пароль через пробел: /auth <логин> <пароль>')
        return

    login, password = context.args[0], context.args[1]
    if USER_DATA.get(login) == password:
        AUTHORIZED_USERS.add(user_id)
        await update.message.reply_text(f'Добро пожаловать, {login}!')
    else:
        await update.message.reply_text('Неверный логин или пароль. Попробуйте снова.')

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in AUTHORIZED_USERS:
        AUTHORIZED_USERS.remove(user_id)
        await update.message.reply_text('Вы успешно вышли.')
    else:
        await update.message.reply_text('Вы не авторизованы.')

async def ip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text('Сначала авторизуйтесь через /auth.')
        return

    if not context.args:
        await update.message.reply_text('Укажите IP-адрес: /ip <IP>')
        return

    ip = context.args[0]
    info = get_info_by_ip(ip)
    await update.message.reply_text(f'Информация по IP:\n{info}')

async def helpme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = (
        "/start - Приветствие\n"
        "/auth - Авторизация\n"
        "/logout - Выход\n"
        "/ip <IP> - Получение информации по IP\n"
        "/help - Список команд"
    )
    await update.message.reply_text(commands)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Неизвестная команда. Используйте /help.')

# Основной блок
def main():
    app = ApplicationBuilder().token(os.environ.get('BOT_TOKEN')).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("auth", auth))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("ip", ip_info))
    app.add_handler(CommandHandler("help", helpme))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    app.run_polling()

if __name__ == "__main__":
    main()
