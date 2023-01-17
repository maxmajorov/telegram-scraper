from telethon.sync import TelegramClient
import csv
import os
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from config import API_ID, API_HASH, PHONE
import pandas as pd
# Получение сообщений из чатов
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from convert_csv_to_exel import csv_to_exel
import pyfiglet


figlet = pyfiglet.figlet_format("Telegram parser", font="slant")
print(figlet)

# Для компиляции в exe
# print("Для подключения к telegram API введите данные:")
# API_ID = input("Введите api_id:")
# API_HASH = input("Введите api_hash:")

client = TelegramClient('session_token', API_ID, API_HASH)

#Создаем папку для сохранения результатов
upload_directory = input("Введите имя директории для сохранения результатов:")
os.mkdir(upload_directory)
retval = os.getcwd()
path = f"{retval}\{upload_directory}"
os.chdir(path)
print("Директория успешно создана.")

def get_channel_subscribers():
    """Находим каналы на которые подписаны и выбираем какой будем парсить"""
    chats = []
    last_date = None
    size_chats = 200
    groups = []

    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=size_chats,
        hash = 0
    ))

    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup == True:
                groups.append(chat)
        except:
            continue
        
    print('Выберите номер группы из перечня:')
    i = 0
    for g in groups:
        print(str(i) + ' - ' + g.title)
        i += 1

    g_index = input("Введите нужную цифру: ")
    channel=groups[int(g_index)]

    return channel


def save_subscribers_info_to_csv(channel): 
    """Сохраняем подписчиков выбранного канала в CSV"""

    print('Узнаём пользователей...')
    all_participants = []
    all_participants = client.get_participants(channel)
    
    print('Сохраняем данные в файл...')
    with open(f"members_{channel.title}.csv","w", encoding='UTF-8') as file:
        writer = csv.writer(file, delimiter=",", lineterminator="\n")
        writer.writerow(['username','name', 'phone', 'group'])
        for user in all_participants:
            if user.username:
                username = user.username
            else:
                username = ""
            if user.first_name:
                first_name = user.first_name
            else:
                first_name = ""
            if user.last_name:
                last_name = user.last_name
            else:
                last_name = ""
            name = (first_name + ' ' + last_name).strip()
            if user.phone:
                phone = user.phone
            else:
                phone= "none"

            writer.writerow([username, name, phone, channel.title])   

    print('Парсинг участников группы успешно выполнен!')

def get_chat_msg(channel):
    """Вычитывает все сообщения канала и сохраняет в CSV"""
    print("Подождите...")
    all_messages = []
    offset_id = 0 # номер записи, с которой начинается считывание
    limit = 100 # максимальное число записей, передаваемых за один раз
    total_messages = 0
    total_count_limit = 0 # задать количество сообщений

    while True:
        history = client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        )) 
      
        if not history.messages:
            break
        messages = history.messages
  
        for message in messages:
            # all_messages.append(message.to_dict()) # выдаст всю инфу о сообщении
            all_messages.append(message.message) 
        offset_id = messages[len(messages) - 1].id
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    print("Сохраняем данные в файл...") 
 
    with open(f"chats_{channel.title}.csv", "w", encoding="UTF-8") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(["message"])
        for message in all_messages:
            writer.writerow([message])     
    print("Парсинг сообщений группы успешно выполнен.")

def main():
    channel = get_channel_subscribers()
    save_subscribers_info_to_csv(channel)

    need_convert_to_exel = input("Конвертировать csv в excel? (y/n)")
    if need_convert_to_exel == 'y':
        file_name = f"members_{channel.title}"
        csv_to_exel(file_name)
        print("Success!")
       
    need_parse_msg = input("Спарсить сообщения выбранного канала? (y/n) ")
    if need_parse_msg == 'y':
        get_chat_msg(channel)
        need_convert_to_exel = input("Конвертировать csv в excel? (y/n)")
        if need_convert_to_exel == 'y':
            file_name = f"chats_{channel.title}"
            csv_to_exel(file_name)
            print("Success!")
      
if __name__ == "__main__":
    client.start()
    main()

# input("Press Enter to exit")

