import telebot
from telebot import types
import sqlite3


bd = sqlite3.connect("user_of_chat.db", check_same_thread=False)
with bd:
    cur = bd.cursor()
    cur.execute("""
        CREATE TABLE  IF NOT EXISTS USER (`id_user` STRING, `status` STRING, `ban` STRING,  tag 'STRING')
    """)
    bd.commit()

TOKEN = "5623172253:AAFZ979nLsFAbj6jafbCLjfTMtyFdiR-7wo"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def hello_message(message):
    bot.send_message(message.chat.id, "Привет, " + message.from_user.first_name + "! Для того, чтобы узнать, что умеет"
                                                                                  " бот ведите команду  /help")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "Этот бот может следующее:"
                     + "\n1) банить людей в чате"
                     + "\n2) разбанивать людей"
                     + "\n3) показываьть статистику"
                     + "\n4) делать пользователей админами" +
                     "\n5) ухадить из группы")


@bot.message_handler(content_types=["new_chat_members"])
def user_joined(message: types.Message):
    user_name = message.from_user.username
    id_user = str(message.from_user.id)
    status = 'USER'
    ban = "NO_BAN"
    tag = "@" + message.from_user.username
    cursor = bd.cursor()
    info = cursor.execute('SELECT * FROM USER WHERE id_user=?', (id_user,)).fetchone()
    if info is None:
        with bd:
            cursor.execute('INSERT INTO USER (id_user, status, ban, tag) VALUES (?, ?, ?, ?)',
                           (id_user, status, ban, tag))
            bd.commit()
    bot.send_message(message.chat.id, "Привет, " + user_name + "! Как дела?")
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(content_types=["left_chat_member"])
def user_leave_chat(message: types.Message):
    id_user = str(message.from_user.id)
    cursor = bd.cursor()
    sql_delete_query = """DELETE from USER where id_user = ?"""
    cursor.execute(sql_delete_query, (id_user,))
    bd.commit()


@bot.inline_handler(func=lambda query: len(query.query) == 0)
def empty_query(inline_query):
    statistics = types.InlineQueryResultArticle('1', 'показать статистику',
                                                types.InputTextMessageContent("статистика: "))
    leave_chat = types.InlineQueryResultArticle('2', 'заставить бота уйти',
                                                types.InputTextMessageContent("Бот покинул чат"))
    bot.answer_inline_query(inline_query.id, [statistics, leave_chat])


@bot.inline_handler(func=lambda query: query.query[0] == '@')
def query_text(inline_query):
    user_name = inline_query.query
    cursor = bd.cursor()
    info = cursor.execute('SELECT * FROM USER WHERE tag=?', (user_name,)).fetchone()
    if info is not None:
        cursor = bd.cursor()
        sqlite_select_query = """SELECT * from USER where tag= ?"""
        cursor.execute(sqlite_select_query, (user_name,))
        record = cursor.fetchone()
        if record[2] == "NO_BAN":
            ban = types.InlineQueryResultArticle('1', 'Забанить пользователя', types.InputTextMessageContent(
                message_text="Пользователь " + user_name + " забанин"))
            admin = types.InlineQueryResultArticle('2', 'Сделать пользователя админом', types.InputTextMessageContent(
                message_text="Пользователь " + user_name + " стал админом"))
            bd.commit()
            bot.answer_inline_query(inline_query.id, [ban, admin])
        elif record[2] == "BAN":
            unban = types.InlineQueryResultArticle('3', 'Разбанить пользователя', types.InputTextMessageContent(
                message_text="Пользователь " + user_name + " разбанин"))
            bd.commit()
            bot.answer_inline_query(inline_query.id, [unban])
    else:
        no_search = types.InlineQueryResultArticle('4', 'пользователь не найден', types.InputTextMessageContent(
            message_text="введите корректное имя"))
        bd.commit()
        bot.answer_inline_query(inline_query.id, [no_search])


@bot.message_handler()
def commands(message: types.Message):
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    if status in ['moderator', 'creator']:
        text = message.text.split()
        if len(text) == 3:
            if text[1][0] == "@":
                user_name = text[1]
                cursor = bd.cursor()
                sqlite_select_query = """SELECT * from USER where tag= ?"""
                cursor.execute(sqlite_select_query, (user_name,))
                record = cursor.fetchone()
                if text[0] == "Пользователь" and text[2] == "забанин":
                    if record[2] == "NO_BAN":
                        bot.ban_chat_member(chat_id=message.chat.id, user_id=int(record[0]))
                        cursor = bd.cursor()
                        sql = """UPDATE USER SET ban = ? WHERE id_user = ?"""
                        cursor.execute(sql, ("BAN", record[0]))
                        bd.commit()
                        cursor.close()
                if text[0] == "Пользователь" and text[2] == "разбанин":
                    if record[2] == "BAN":
                        cursor = bd.cursor()
                        sql = """UPDATE USER SET ban = ? WHERE id_user = ?"""
                        cursor.execute(sql, ("NO_BAN", record[0]))
                        bd.commit()
                        bot.unban_chat_member(chat_id=message.chat.id, user_id=int(record[0]))
                        cursor.close()
                if text[0] == "Бот" and text[1] == "покинул" and text[2] == "группу":
                    bot.leave_chat(message.chat.id)
        elif len(text) == 4:

            if text[0] == "Пользователь" and text[2] == "стал" and text[3] == "админом":
                user_name = text[1]
                cursor = bd.cursor()
                sqlite_select_query = """SELECT * from USER where tag= ?"""
                cursor.execute(sqlite_select_query, (user_name,))
                record = cursor.fetchone()
                if record[2] == "NO_BAN":
                    sql = """UPDATE USER SET status = ? WHERE id_user = ?"""
                    cursor.execute(sql, ("ADMIN", record[0]))
                    bd.commit()
                    cursor.close()
                    bot.promote_chat_member(message.chat.id, int(record[0]), True, True, True)
        elif len(text) == 1:
            if text[0] == "статистика:":
                count_admin = 0
                count_user = 0
                with bd:
                    cursor = bd.cursor()
                    cursor.execute("SELECT * FROM `USER`")
                    data = cursor.fetchall()
                    for row in data:
                        if row[2] == "NO_BAN":
                            count_user += 1
                            if row[1] == "ADMIN":
                                count_admin += 1
                bot.send_message(message.chat.id,
                                 "число участников: " + str(count_user) + "\nчисло админов :" + str(count_admin))


bot.polling(none_stop=True, interval=0)
