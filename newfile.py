import datetime
import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Функция для определения времени (если утро - доброе утро, если вечер - добрый вечер)
def get_time_of_day():
    current_hour = datetime.datetime.now().hour

    if 6 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"

# Пример базы данных логинов и паролей (можно заменить на реальную базу данных)
users = {
    'Taylon': 'kamaz123',  # Логин: пароль
}

# Храним информацию о текущих авторизованных пользователях
authorized_users = set()

# Функция для получения информации по IP
def get_info_by_ip(ip='127.0.0.1'):
    try:
        response = requests.get(url=f'http://ip-api.com/json/{ip}').json()
        data = {
            '[IP]': response.get('query'),
            '[Internet Provider]': response.get('isp'),
            '[Organization]': response.get('org'),
            '[Country]': response.get('country'),
            '[Region Name]': response.get('regionName'),
            '[City]': response.get('city'),
            '[ZIP]': response.get('zip'),
            '[Latitude]': response.get('lat'),
            '[Longitude]': response.get('lon'),
            '[Time Zone]': response.get('timezone'),
        }
        result = '\n'.join([f'{k}: {v}' for k, v in data.items()])
        return result
    except requests.exceptions.ConnectionError:
        return '[!] Проверьте соединение [!]'

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('txt.jpg', 'rb') as f:
        await update.message.reply_photo(photo=InputFile(f, filename="txt.jpg"))
    greeting = get_time_of_day()
    await update.message.reply_text(f'{greeting}, mister Taylon! Не могли бы авторизоваться?')

# Команда для отображения доступных команд
async def helpme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Команды которые могут использоваться: \n /auth - Авторизация \n/ip - После авторизации можете узнать данные по IP адресу \n/start - стартовое приветствие \n/logout - выйти')
async def notcommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Неизвестная команда введите /help для уточнение.')
# Команда для авторизации (логин и пароль)
async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Проверяем, если пользователь уже авторизован
    if user_id in authorized_users:
        await update.message.reply_text('Вы уже авторизованы!')
        return

    # Если логин еще не введен, то ждем логин
    if 'login' not in context.chat_data:
        if len(context.args) == 0:
            await update.message.reply_text('Пожалуйста, введите логин. Например: /auth Nick')
            return
        
        login = context.args[0]

        # Проверяем, существует ли такой логин
        if login in users:
            context.chat_data['login'] = login  # Сохраняем логин
            await update.message.reply_text(f'Логин {login} найден. Пожалуйста, введите пароль.')
        else:
            await update.message.reply_text('Неверный логин. Пожалуйста, попробуйте снова.')
            return

    # Если логин был введен, теперь проверяем пароль
    elif 'login' in context.chat_data:
        login = context.chat_data['login']
        if len(context.args) == 0:
            await update.message.reply_text('Пожалуйста, введите пароль.')
            return
        
        password = context.args[0]

        # Проверяем пароль
        if users[login] == password:
            authorized_users.add(user_id)
            await update.message.reply_text(f'Добро пожаловать, {login}! Вы авторизованы.')
            del context.chat_data['login']  # Очищаем данные логина
        else:
            await update.message.reply_text('Неверный пароль. Попробуйте снова.')

# Команда для выхода (разавторизации)
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in authorized_users:
        authorized_users.remove(user_id)
        await update.message.reply_text('Вы разавторизованы.')
    else:
        await update.message.reply_text('Вы не авторизованы.')

# Команда для получения информации по IP
async def ip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in authorized_users:
        await update.message.reply_text('Вы не авторизованы! Пожалуйста, авторизуйтесь.')
        return

    if len(context.args) == 0:
        await update.message.reply_text('Пожалуйста, укажите IP-адрес после команды.')
    else:
        ip = context.args[0]
        info = get_info_by_ip(ip)
        await update.message.reply_text(f'Информация по IP:\n{info}')

def main():
    app = ApplicationBuilder().token('').build() # Your tg token  

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("auth", auth))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("ip", ip_info))
    app.add_handler(CommandHandler("help", helpme))

    # Последняя команда обязательно
    app.add_handler(MessageHandler(filters.TEXT, notcommand)) 

    app.run_polling()

if __name__ == '__main__':
    main()
