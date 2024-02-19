
import telebot
import sqlite3
import random
from datetime import datetime, timedelta
bonus7_date = []
bonus1_date = []
bet = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # список ставок
balance = []
#бд
conn = sqlite3.connect('database.db',check_same_thread=False)
cursor = conn.cursor()

#таблица
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        balance INTEGER,
        bonus1_date TEXT,
        bonus7_date TEXT
    )
""")
conn.commit()

bot = telebot.TeleBot("6880574062:AAFOtPHH6fTjsF2jgP3abmIndODfQHY2uVk")


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    #есть ли в базе
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        #регистрация
        cursor.execute("INSERT INTO users (id, balance, bonus1_date, bonus7_date) VALUES (?, 0, NULL, NULL)",
                       (user_id,))
        conn.commit()
        bot.reply_to(message, f"Для просмотра команд пропишите команду /help, ваш баланс: 0")
    else:
        bot.reply_to(message, "Ваш id уже имеется в базе данных")

#cmd
@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.from_user.id
    bot.send_message(user_id,
                     "\n/start - регистрация\n/help - помощь по командам\n/balance - баланс\n/deposit - пополнение счета\n/bonus1 - ежедневный бонус\n/bonus7 - еженедельный бонус\n/or - игра\n/time - дата/время\n/info - информация о боте")

#info o bote
@bot.message_handler(commands=['info'])
def info(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Это бот для игры в "орёл или решка" на настоящие деньги.')

#cigel
@bot.message_handler(commands=['time'])
def time_command(message):
    date = datetime.now()
    bot.reply_to(message, f'Дата/время на сегодняшний день: {date}')

#balance
@bot.message_handler(commands=['balance'])
def balance_command(message):
    user_id = message.from_user.id
#balance iz bd
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()[0]

    bot.reply_to(message, f"Ваш текущий баланс: {balance}")

#igra
@bot.message_handler(commands=['or'])
def game_command(message):
    user_id = message.from_user.id
#balance iz bd
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()[0]

    #babki na balance
    if balance >= 10:
        bet = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        markup = telebot.types.InlineKeyboardMarkup()

        for amount in bet:
            markup.add(telebot.types.InlineKeyboardButton(text=str(amount), callback_data=str(amount)))

        bot.send_message(user_id, 'Выберите ставку:', reply_markup=markup)
    else:
        bot.send_message(user_id,
                         "На вашем балансе недостаточно средств. Пополните счет через /deposit для участия в игре.")


@bot.callback_query_handler(func=lambda call: call.data in [str(amount) for amount in bet])
def game_callback(call):
    user_id = call.from_user.id
    bet = int(call.data)

    #babki iz bd
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()[0]

    if balance >= bet:
        result = random.choice(['win', 'lose'])

        if result == 'win':
            balance += bet
            bot.send_message(user_id, f"Вы выиграли {bet}. Ваш баланс: {balance}")
        else:
            balance -= bet
            bot.send_message(user_id, f"Вы проиграли {bet}. Ваш баланс: {balance}")

            if balance < 10:
                bot.send_message(user_id,
                                 "У вас недостаточно средств на балансе. Пополните счет через /deposit для участия в игре.")

        #obnova balance
        cursor.execute("UPDATE users SET balance=? WHERE id=?", (balance, user_id))
        conn.commit()
    else:
        bot.send_message(user_id, "Недостаточно средств для выбранной ставки. Пополните счет через /deposit.")

#popolnenie
@bot.message_handler(commands=['deposit'])
def deposit_command(message):
    user_id = message.from_user.id
    bot.reply_to(message,
                 f"Ваш текущий баланс: 0\nДля пополнения баланса свяжитесь с администратором\nhttps://vk.com/adfromelb")

#bonus1
@bot.message_handler(commands=['bonus1'])
def bonus1_command(message):
    user_id = message.from_user.id

    #last bonus
    cursor.execute("SELECT bonus1_date FROM users WHERE id=?", (user_id,))
    bonus1_date = cursor.fetchone()[0]

    now = datetime.now()

    if bonus1_date is None or (now - datetime.fromisoformat(bonus1_date) >= timedelta(days=1)):
        cursor.execute("UPDATE users SET bonus1_date=?, balance=balance+10 WHERE id=?", (now.isoformat(), user_id))
        conn.commit()
        bot.reply_to(message, f"Вы получили ежедневный бонус в размере 10 монет. Ваш баланс: {balance + 10}")
    else:
        bot.reply_to(message, "Вы уже получили бонус сегодня.")

#bonus7
@bot.message_handler(commands=['bonus7'])
def bonus7_command(message):
    user_id = message.from_user.id

    #last bonus7
    cursor.execute("SELECT bonus7_date FROM users WHERE id=?", (user_id,))
    bonus7_date = cursor.fetchone()[0]

    now = datetime.now()

    if bonus7_date is None or (now - datetime.fromisoformat(bonus7_date) >= timedelta(days=7)):
        cursor.execute("UPDATE users SET bonus7_date=?, balance=balance+30 WHERE id=?", (now.isoformat(), user_id))
        conn.commit()
        bot.reply_to(message, f"Вы получили еженедельный бонус в размере 30 монет. Ваш баланс: {balance + 30}")
    else:
        bot.reply_to(message, "Вы уже получили бонус на этой неделе.")


bot.polling()

#close bd
conn.close()
