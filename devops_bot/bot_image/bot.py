import logging
import re, os, paramiko
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv
import psycopg2
import subprocess

def list_command(update: Update, context):
    update.message.reply_text('Введите команду для получения мериков с kali: \n'
                              '/get_release - О релизе. \n'
                              '/get_uname - Об архитектуры процессора, имени хоста системы и версии ядра.\n'
                              '/get_uptime - О времени работы.\n'
                              '/get_df - Сбор информации о состоянии файловой системы.\n'
                              '/get_free - Сбор информации о состоянии оперативной памяти.\n'
                              '/get_mpstat - Сбор информации о производительности системы.\n'
                              '/get_w - Сбор информации о работающих в данной системе пользователях.\n'
                              '/get_auths - Последние 10 входов в систему.\n'
                              '/get_critical - Последние 5 критических события.\n'
                              '/get_ps - Сбор информации о запущенных процессах.\n'
                              '/get_ss - Сбор информации об используемых портах.\n'
                              '/get_apt_list - Сбор информации об установленных пакетах (5 первых).\n'
                              '/get_apt_list "название пакета" - Сбор информации о конкретном пакете.\n'
                              '/get_services - Сбор информации о запущенных сервисах.\n')
    
load_dotenv("/home/starikovmr/bot/.env")

#.env info
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_db = os.getenv('DB_DATABASE')


TOKEN = os.getenv("TOKEN")

#logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')
    update.message.reply_text(f'Вот список доступных команд:\n'
                                '1)Найти номера:/find_phone_numbers\n'
                                '2)Найти email:/find_email\n'
                                '3)Проверить пароль:/check_password\n'
                                '4)Вывести команды для мониторинга Linux:/list\n'
                                '5)Вывести логи репликации:/get_repl_logs\n')


def list_command(update: Update, context):
    update.message.reply_text('Введите команду для получения мериков с kali: \n'
                              '/get_release - О релизе. \n'
                              '/get_uname - Об архитектуры процессора, имени хоста системы и версии ядра.\n'
                              '/get_uptime - О времени работы.\n'
                              '/get_df - Сбор информации о состоянии файловой системы.\n'
                              '/get_free - Сбор информации о состоянии оперативной памяти.\n'
                              '/get_mpstat - Сбор информации о производительности системы.\n'
                              '/get_w - Сбор информации о работающих в данной системе пользователях.\n'
                              '/get_auths - Последние 10 входов в систему.\n'
                              '/get_critical - Последние 5 критических события.\n'
                              '/get_ps - Сбор информации о запущенных процессах.\n'
                              '/get_ss - Сбор информации об используемых портах.\n'
                              '/get_apt_list - Сбор информации об установленных пакетах (5 первых).\n'
                              '/get_apt_list "название пакета" - Сбор информации о конкретном пакете.\n'
                              '/get_services - Сбор информации о запущенных сервисах.\n')

def find_phone_numbers_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_numbers'


def find_phone_numbers (update: Update, context):
    user_input = update.message.text 

    phone_num_regex = re.compile(r"\+?7[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|\+?7[ -]?\d{10}|8[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|8[ -]?\d{10}")

    phone_number_list = phone_num_regex.findall(user_input) 

    if not phone_number_list: 
        update.message.reply_text('В тексте нет телефонных номеров.')
        return ConversationHandler.END 
    
    logging.info("Список телефонных номеров" + str(phone_number_list))
    phone_numbers = '' 
    for i in range(len(phone_number_list)):
        phone_number = phone_number_list[i]
        phone_numbers += f'{i+1}. {phone_number}\n'
        
    update.message.reply_text(phone_numbers) 
    update.message.reply_text('Хотите записать данные в таблицу? Y/N')
    context.user_data['phonenumlist'] = phone_number_list
    return 'save_to_base'


def help_command(update: Update, context):
    update.message.reply_text('Help!')


def find_emails_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')

    return 'find_emails'


def find_emails (update: Update, context):
    user_input = update.message.text

    email_regex = re.compile(r'[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+') 

    email_list = email_regex.findall(user_input) 

    if not email_list:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END 
    
    logging.info("Список email-адресов" + str(email_list))

    emails = ''
    for i in range(len(email_list)):
        emails += f'{i+1}. {email_list[i]}\n'
        
    update.message.reply_text(emails) 
    update.message.reply_text('Хотите записать данные в таблицу? Y/N')
    context.user_data['emaillist'] = email_list
    return 'save_to_base'


def check_pass_command(update: Update, context):
    update.message.reply_text('Введите пароль: ')
    return 'check_password'


def check_password (update: Update, context):
    user_input = update.message.text 

    pass_regex = re.compile(r'(?=.*[0-9])(?=.*[!@#$%^&*()])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*()]{8,}') 

    pass_check = pass_regex.findall(user_input) 
    logging.info("Введенный пароль:" + str(pass_check))
    if not pass_check:
        update.message.reply_text('Пароль простой')
        return ConversationHandler.END 
        
    update.message.reply_text('Пароль сложный') 
    return ConversationHandler.END 

#for ssh
def execute_command(command, host_, username_, password_, port_):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logging.info(str(host))
        client.connect(hostname=host_, username=username_, password=password_, port=port_)
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        logging.info(data)
        return data
    except:
        return ""
    
#for postgres
def execute_postgres_command(command):
    connection = None
    try:
        connection = psycopg2.connect(user=db_username,
                                    password=db_password,
                                    host=db_host,
                                    port=db_port, 
                                    database=db_db)

        cursor = connection.cursor()
        cursor.execute(command)
        if not "SELECT" in command: connection.commit()
        data = cursor.fetchall()
        logging.info("Команда успешно выполнена")
        return data
    except (Exception, psycopg2.Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")



def get_release_command(update: Update, context):
    data = execute_command('lsb_release -a', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")


def get_uname_command(update: Update, context):
    data = execute_command('uname -a', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")    

def get_uptime_command(update: Update, context):
    data = execute_command('uptime', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_df_command(update: Update, context):
    data = execute_command('df -h', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_free_command(update: Update, context):
    data = execute_command('free -h', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_mpstat_command(update: Update, context):
    data = execute_command('mpstat -P ALL', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_w_command(update: Update, context):
    data = execute_command('w', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_auth_command(update: Update, context):
    data = execute_command('last -n 10', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_critical_command(update: Update, context):
    data = execute_command('journalctl -p crit -n 5', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_ps_command(update: Update, context):
    data = execute_command('ps aux | head -n 20', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_ss_command(update: Update, context):
    data = execute_command('ss | head -n 20', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def get_services_command(update: Update, context):
    data = execute_command('systemctl list-units --type=service --state=active | head -n 20', host, username, password, port)
    if(data != ""): update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")

def apt_list_command(update: Update, context):
    update.message.reply_text('Enter apt_list or packet name')
    return 'apt_list'


def apt_list(update: Update, context):
    user_input = update.message.text 
    data = ""
    if(user_input == "apt_list"):
        data = execute_command('apt list --installed | head -n 20', host, username, password, port) 
    else:
        user_input = re.split('[ |&;]', user_input)[0]
        data = execute_command(f'apt show {user_input}', host, username, password, port)
    
    if(data == ""): 
        update.message.reply_text("Ошибка выполнения команды")
        return ConversationHandler.END 
    
    update.message.reply_text(data)
    logging.info(user_input)
    logging.info(data)
    return ConversationHandler.END 


def get_repl_logs_command(update: Update, context):
    data = ""
    data = execute_command('head -40 /var/log/postgresql/postgresql-14-main.log | grep "repl"', host, username, password, port)
    logging.info("OK")
    if(data != ""):
        update.message.reply_text(data)
    else: update.message.reply_text("Ошибка выполнения команды")



def get_emails_command(update: Update, context):
    data = execute_postgres_command("SELECT * FROM Emails;")
    if(data != ""): 
        emails = ''
        for element in data:
            emails += f'{element[0]}. {element[1]}\n'
        update.message.reply_text(emails)
    else: update.message.reply_text("Ошибка выполнения команды")


def get_phone_numbers_command(update: Update, context):
    data = execute_postgres_command("SELECT * FROM PhoneNumbers;")
    if(data != ""):
        numbers = ''
        for element in data:
            numbers += f'{element[0]}. {element[1]}\n'
        update.message.reply_text(numbers)
    else: 
        update.message.reply_text("Ошибка выполнения команды")

def save_to_base(update: Update, context, data: str, data_type: str):
    user_input = update.message.text 
    if(user_input == "N"):
        update.message.reply_text('OK')
        return ConversationHandler.END 
    result = ""
    if data_type.lower() == 'phone_numbers':
        for element in data:
            number = element
            result = execute_postgres_command(f"INSERT INTO PhoneNumbers (phone_number) VALUES ('{number}');")
    elif data_type.lower() == 'emails':
        for element in data:
            result = execute_postgres_command(f"INSERT INTO Emails (email) VALUES ('{element}');")
    else: update.message.reply_text("Ошибка выполнения команды")
    if(result == ""): update.message.reply_text("Ошибка выполнения команды")
    else: 
        update.message.reply_text(f'Информация {data_type} успешно записана в базу данных.')
        if data_type.lower() == 'phone_numbers':
            update.message.reply_text(f'Просмотреть список телефонных номеров: /get_phone_numbers')
        elif data_type.lower() == 'emails':
            update.message.reply_text(f'Просмотреть список электронных почт: /get_emails')
    return ConversationHandler.END


def main():

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFPN = ConversationHandler(
        entry_points=[CommandHandler('find_phone_numbers', find_phone_numbers_command)],
        states={
            'find_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, find_phone_numbers)],
            'save_to_base': [MessageHandler(Filters.text & ~Filters.command, lambda update, context: save_to_base(update, context, context.user_data['phonenumlist'], 'phone_numbers'))]
        },
        fallbacks=[]
    )

    convHandlerFE = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_emails_command)],
        states={
            'find_emails': [MessageHandler(Filters.text & ~Filters.command, find_emails)],
            'save_to_base': [MessageHandler(Filters.text & ~Filters.command, lambda update, context: save_to_base(update, context, context.user_data['emaillist'], 'emails'))]
        },
        fallbacks=[]
    )

    convHandlerСP = ConversationHandler(
        entry_points=[CommandHandler('check_password', check_pass_command)],
        states={
            'check_password': [MessageHandler(Filters.text & ~Filters.command, check_password)],
        },
        fallbacks=[]
    )

    convHandlerAL = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', apt_list_command)],
        states={
            'apt_list': [MessageHandler(Filters.text & ~Filters.command, apt_list)],
        },
        fallbacks=[]
    )
  
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(convHandlerFPN)
    dp.add_handler(convHandlerFE)
    dp.add_handler(convHandlerСP)
    dp.add_handler(convHandlerAL)
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("get_release", get_release_command))
    dp.add_handler(CommandHandler("get_uname", get_uname_command))
    dp.add_handler(CommandHandler("get_df", get_df_command))
    dp.add_handler(CommandHandler("get_uptime", get_uptime_command))
    dp.add_handler(CommandHandler("get_free", get_free_command))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat_command))
    dp.add_handler(CommandHandler("get_w", get_w_command))
    dp.add_handler(CommandHandler("get_auths", get_auth_command))
    dp.add_handler(CommandHandler("get_critical", get_critical_command))
    dp.add_handler(CommandHandler("get_ps", get_ps_command))
    dp.add_handler(CommandHandler("get_ss", get_ss_command))
    dp.add_handler(CommandHandler("get_services", get_services_command))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs_command))
    dp.add_handler(CommandHandler("get_emails", get_emails_command))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers_command))
    dp.add_handler(CommandHandler("list", list_command))
    
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
