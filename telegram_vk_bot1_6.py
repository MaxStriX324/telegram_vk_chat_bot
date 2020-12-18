#Библиотеки***************************************************************
import sqlite3
import difflib
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import random
import datetime
import logging
import configparser
#Библиотеки***************************************************************

#Настройки и переменные***************************************************
#tokentelegram = "1327174945:AAEYbr3ni0zKz61av09Lkcn38h3r6or6a3Q"
#tokenvk = "e8e132ae4f6e8240687aafb8b079c878717012a3f1043fa254a357e4a613a94235f3e2cdc1106f65bdf88"
#publikid = "200853388"
#bdpath = "database.db"
#Настройки и переменные***************************************************
def word_count(myfile):
    logging.basicConfig(level=logging.DEBUG, filename='myapp.log', format='%(asctime)s %(levelname)s:%(message)s')
    try:
        # считаем слова, логируем результат.
        with open(myfile, 'r') as f:
            file_data = f.read()
            words = file_data.split(" ")
            num_words = len(words)
            logging.debug("this file has %d words", num_words)
            return num_words
    except OSError as e:
        logging.error("error reading the file")
#Функции******************************************************************
#Функция логирования

#функция подключения к бд
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Соеденение с базой произведено успешно")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection
#сравнение с ответа пользователя с ответом из бд
def similarity(s1, s2):
  normalized1 = s1.lower()
  normalized2 = s2.lower()
  matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
  return matcher.ratio()
#поиск имени пользователя
def search_username():
    print("Нужно найти имя пользователя")
    if vkmessage == 1:
        user_get=vk.users.get(user_ids = (user_id))
        user_get=user_get[0]
        username=user_get['first_name']
    if telegrammessage == 1:
        username = first_name
    print("Имя пользователя:" ,username)
    return username
#поиск ответа в бд
def search_message(text): 
  print("Пользователь отправил: ", text)
  conn = create_connection(bdpath)
  c = conn.cursor()
  if text == "Команды" or text == "команды":
      print("Пользователь хочет команды")
      answer = """***Команды чат бота бомж Александр***
Расскажи анекдот - расскажет вам анекдот
Расскажи историю - расскажет вам историю
Время - Скажет точное время
Если просто написать сообщение бот вам ответит!"""
  elif text == "Расскажи анекдот" or text == "расскажи анекдот":
      print("Пользователь хочет анекдот")
      c.execute("SELECT * FROM anecdotes")
      anecdotes = []
      for i in c.fetchall():
        anecdotes.append(i[0])
      answer = anecdotes[(random.randint(0, len(anecdotes)) - 1)]
  elif text == "Расскажи историю" or text == "расскажи историю":
      print("Пользователь хочет историю")
      c.execute("SELECT * FROM stories")
      stories = []
      for i in c.fetchall():
        stories.append(i[0])
      answer = stories[(random.randint(0, len(stories)) - 1)]
  elif text == "Время" or text == "время":
      print("Пользователь хочет узнать время")
      now = datetime.datetime.now()
      answer = now.strftime("%d-%m-%Y %H:%M")
      print("Бот отправил: ", answer)
  else:
      c.execute("SELECT * FROM answers where (message)=(?)",(text, )) #достаем все данные из таблицы ответов бд
      n = 0
      answers = []
      unknown_answers = []
      sim = []
      index = []
      for i in c.fetchall():
        answers.append(i[1]) #добавляем все ответы из бд
      conn.commit()
      print("Количество ответов в базе: ", len(answers))
      if len(answers) != 0:
          print("Бот нашел ответ в базе, выбираю рандомный")
          answer = answers[(random.randint(0, len(answers)) - 1)]
      else:
          print("бот не нашел ответ в базе, начинаю ход конем")
          c.execute("SELECT * FROM answers") #достаем все данные из таблицы ответов бд
          for i in c.fetchall():
              answers.append(i[1]) #добавляем все ответы из бд
              sim.append(similarity(text, i[0])) #сравниваем ответ пользователя с ответами из базы
          ind = sim.index(max(sim))  #индекс самого совпадаяющего сообщения из базы
          print("Найден ответ, похож на: ", sim[ind] * 100, "%") 
          if sim[ind] < 0.85: #если сообщение пользователя не совпадает с сообщением из базы на 85%, добавляем сообщение в таблицу неизвестных сообщений
              print("Данное сообщение не совпадает с базой на 85%, добавляю в неизвестные и отправляю самое схожее")
              c.execute("SELECT * FROM unknown_messages where (messages)=(?)",(text, )) #достаем все данные из таблицы ответов бд
              for i in c.fetchall():
                  unknown_answers.append(i[0]) #добавляем все ответы из бд
              conn.commit()
              if len(unknown_answers) == 0:
                  print("Подобных сообщений не было добавляю в неизвестные")
                  c.execute("INSERT INTO unknown_messages (messages)  VALUES (?)",(text, ))
                  conn.commit()
              else:
                  print("Это сообщение присутствует в базе неизвестных сообщений")
          answer = answers[ind]
      ogrone = 0
      ogrtwo = 0
      ogrthree = 0
      ogrfour = 0
      for i in answer:
          if i == "%":
              index.append(n)
          n = n + 1
      if len(index) == 2:
          ogrone = index[0]
          ogrtwo = index[1] + 1
          if answer[ogrone:ogrtwo] == "%username%" or answer[ogrone:ogrtwo] == "%USERNAME%":
              answer = answer[:ogrone] + search_username() + answer[ogrtwo:]
      elif len(index) == 4:
          ogrone = index[0]
          ogrtwo = index[1] + 1
          ogrthree = index[2]
          ogrfour = index[3] + 1
          if answer[ogrone:ogrtwo] == "%username%" or answer[ogrone:ogrtwo] == "%USERNAME%":
              answer = answer[:ogrone] + search_username() + answer[ogrtwo:ogrthree] + search_username() + answer[ogrfour:]
      print("Бот отправил: ", answer)
      conn.close()
      print("Отключение от базы произведено успешно")
      print("")
      print("")
      print("")
  return answer #отправляем сообщение с большим совпадением
#Функция ответа на команду старт в Telegram
def start(update, context):
    update.message.reply_text('ЭЭЭ, мелочи не найдется?')
#Функция ответа на обычное текстовое сообщение в телеграм
def text(update, context):
    #получаем текст от пользователя
    message = update.message.text
    print("пользователь telegram отправил сообщение")
    #отправляем текст в нашу функцио поиска ответа
    global telegrammessage, first_name
    telegrammessage = 1
    first_name = update.message.chat.first_name
    answer = search_message(message)
    #вовщращаем результат пользователю в боте
    update.message.reply_text(answer)
#функция ответа на текстовое личное сообщение в вк
def write_msg_user(user_id, message):
    try:
        vk_session.method('messages.send', {'user_id': user_id, 'message': message, "random_id": random_id})
    except vk_api.ApiError as err:
        print("Error", err, end="\n"*2)
#функция ответа на текстовое сообщение в беседе вк
def write_msg_chat(user_id, message):
    try:
        vk_session.method('messages.send', {'chat_id': user_id, 'message': message, "random_id": random_id})
    except vk_api.ApiError as err:
        print("Error", err, end="\n"*2)
#Функции**********************************************************************

#Достаем настройки из конфигурационного файла
config = configparser.ConfigParser()
config.read("settings.ini")
tokentelegram = config["TELEGRAM"]["token"]
tokenvk = config["VK"]["token"]
publikid = config["VK"]["publik"]
bdpath = config["BD"]["path"]
#бот вк
#создаем бота и указываем его токен
updater = Updater(tokentelegram, use_context=True)
#создаем регистратор событий, который будет понимать, что сделал пользователь и на какую функцию надо переключиться.
dispatcher = updater.dispatcher
# Авторизуемся как сообщество
vk_session = vk_api.VkApi(token=tokenvk)
longpoll = VkBotLongPoll(vk_session, publikid)
vk = vk_session.get_api()
# Работа с сообщениями
for event in longpoll.listen():
    vkmessage = 0
    telegrammessage = 0
    #запускаем бота telegram
    updater.start_polling()
    #регистрируем команду /start и говорим, что после нее надо использовать функцию def start
    dispatcher.add_handler(CommandHandler("start", start))
    #регистрируем получение текста и говорим, что после нее надо использовать функцию def text
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    # Если пришло новое сообщение
    if event.type == VkBotEventType.MESSAGE_NEW:
        vkmessage = 1
        if event.from_user:
            user_id = event.obj.from_id
            random_id = get_random_id()
            print("пользователь vk: ", "http://vk.com/id" + str(user_id), "отправил сообщение")
            request = event.obj.text # Сообщение от пользователя
            answer = search_message(request) #Поиск ответа
            write_msg_user(user_id, answer) #Отправка ответа
        elif event.from_chat:
            print("Беседа vk: ", event.chat_id, "отправил сообщение")
            request = event.obj.text # Сообщение от пользователя
            random_id = get_random_id()
            answer = search_message(request) #Поиск ответа
            write_msg_chat(event.chat_id, answer) #Отправка ответа
        elif event.type == VkBotEventType.GROUP_JOIN:
            print(event.obj.user_id, end=' ')

            print('Вступил в группу!')
            print()

        elif event.type == VkBotEventType.GROUP_LEAVE:
            print(event.obj.user_id, end=' ')

            print('Покинул группу!')
            print()

