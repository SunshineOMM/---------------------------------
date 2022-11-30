import collections
import json
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, files, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import input_output_system.config as conf
import input_output_system.service_data as service_data
import service_data.data as data
import input_output_system.dialogs as dialogsf
import system_for_selecting_and_analyzing_actions.leaner as leaner

class bot(object):

    def __init__(self,dialog_with_customer,dialog_about_create_course,dialog_about_lern_course):
        """Инициализация бота"""
        self.updater = Updater(conf.TOKEN, use_context=True)
        # Создание обработчика для регистрации обработчиков
        self.dp = self.updater.dispatcher
        # ставим обработчик всех текстовых сообщений
        handler = MessageHandler(Filters.text | Filters.command | Filters.document.mime_type("application/msword") |
                                      Filters.document.mime_type("application/vnd.openxmlformats-officedocument"
                                                                 ".wordprocessingml.document") |
                                      Filters.document.mime_type("text/plain"),self.handle_message)
        self.updater.dispatcher.add_handler(handler)

        # Обработчик нажатия на кнопку
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.button))
        #   Словарь содержащий название типа диалога и саму беседу
        self.handlers = {"author_registration":collections.defaultdict(dialog_with_customer),
                                   "create_course":collections.defaultdict(dialog_about_create_course),
                                    "lern_course":collections.defaultdict(dialog_about_lern_course)}

    def start(self):
        """
        Метод запуска бота
        :return:
        """
        # Запуск бота
        self.updater.start_polling()
        # Блокирует выболнение до получения сигнала(события)
        self.updater.idle()

    def button(self,update, context,dummy=""):
        """
        Метод обработки нажатий на любые клавиши
        :param update:
        :param context:
        :param dummy:
        :return:
        """
        chat_id = str(update.callback_query.message.chat_id)
        query = update.callback_query
        query.answer()

        #   data=[event_type("choisecourse","learn","repeat","test"),lesson,course]
        data=query.data.split("_")
        print(data)
        if "choise" == data[0]:
            #   Если при выборе нового курса была нажата какая-нибудь кнопка
            #   Проверка на уже изучение данного курса, если этот курс не был начат ранее, то старт для курса
            leaner.start_new_course_for_unknow_leaner(chat_id, data[1])
            query.edit_message_text("Отличный выбор!")
        elif "learn" == data[0]:
            #   Если была нажата кнопка старта изучения очередного занятия
            query.edit_message_text(leaner.lern_new_lesson(str(chat_id),data[2],data[1]))
        elif "repeat" == data[0]:
            #   Если была нажата кнопка старта изучения очередного занятия
            query.edit_message_text(leaner.repeat_lesson(str(chat_id),data[2],data[1]))
        elif "test" == data[0]:
            #   Если была нажата кнопка старта теста по очередному занятию
            print_list_button_with_text(update.callback_query,
                                        *leaner.start_test_lesson(chat_id,data[2],data[1])
                                        , replace=True)
        elif "answerfortest"==data[0]:
            #   Если была нажата кнопка выбора ответа в  тесте по очередному занятию
            number_lesson,number_test,answer=data[1].split("%")
            test_answer=leaner.getting_a_response_to_a_test(chat_id,data[2], number_lesson, number_test, answer)
            if type(test_answer)==str:
                query.edit_message_text(test_answer)
            elif  type(test_answer)==list:
                print_list_button_with_text(update.callback_query, *test_answer, replace=True)

    def handle_message(self, update, context):
        """
        Метод, срабатывающий при отправке любого* сообщения боту.
        Запускает процесс опознания беседы и ответа пользователя.
        *- тех типов и форматов, что описаны в хэндлерах
        :param update:
        :param context:
        :return:
        """
        #   Проверка на наличие комманд, если есть команда, то автоматически будет запущен обработчик этой комманды
        if not self.checking_for_commands(update, context):
            #  Переход на нужную беседу по текущему id
            self.redirecting_to_a_conversation(update, context)

    def start_command(self,update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Привет! Если нужна помощь напишите /help')
        get_main_menu(update)

    def help_command(self,update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text(service_data.str_help)

    def author_registration_command(self,update, context):
        """Беседа регистрация нового автора в системе"""
        chat_id = str(update.message.chat_id)
        #   Проверка наличия этого пользователя уже в качестве автора
        # if data.find("customers",str(update.message["chat"]["id"])) == None:
        #     answer = self.processing_the_next_dialog_message(chat_id,update.message, context, "author_registration")
        #
        #     if type(answer) == dict and data.enters_the_final_data_about_author(answer,chat_id):
        #         update.message.reply_text(f"Регистрация прошла успешно!")
        #     elif answer==service_data.str_error_for_registration:
        #         self.remove_from_handler(chat_id,"author_registration")
        #         update.message.reply_text(answer)
        #     else:
        #         update.message.reply_text(answer)
        #else:
        update.message.reply_text(f"Поехали!")

    def create_course_command(self,update, context):
        """Беседа создания курса"""
        chat_id = str(update.message.chat_id)
        #   Проверка наличия этого пользователя уже в качестве автора
        if data.find("customers", chat_id) != None:
            answer = self.processing_the_next_dialog_message(chat_id,update.message, context, "create_course")
            if type(answer) == dict:
                if answer.get("file")!=None:
                    # Отправляется пример
                    update.message.reply_text(answer["text"])
                    import os
                    abs_path = os.path.abspath("input_output_system")
                    with open(f"{abs_path}/EXAMPLE.docx", "rb") as f:
                        update.message.reply_document(f)
                else:
                    if data.enters_the_final_data_about_course(answer,chat_id):
                        update.message.reply_text("Ваш курс успешно создан!")
                    else:
                        update.message.reply_text(f"Создание курса прошло не успешно")
            elif answer == service_data.str_error_for_create_course:
                self.remove_from_handler(chat_id, "create_course")
                update.message.reply_text(answer)
            else:
                update.message.reply_text(answer)
        else:
            update.message.reply_text(service_data.str_customer_dint_regitred)

    def lern_course_command(self,update, context=""):
        """Старт изучения курса"""
        chat_id = str(update.message.chat_id)
        #   Проверка на наличие этого обучаемого в системе, если его нет, то создать о нём запись
        # if data.find("leaners", chat_id) == None:
        #     answer = self.processing_the_next_dialog_message(chat_id,update.message, context, "lern_course")
        #     if type(answer) == dict:
        #         print(f'answer: {answer}')
        #         if data.enters_the_final_data_about_leaner(answer,chat_id):
        #             update.message.reply_text(f"Регистрация прошла успешно!")
        #         else:
        #             update.message.reply_text(f"Регистрация не прошла успешно")
        #     if answer == service_data.str_error_for_registration:
        #         self.remove_from_handler(chat_id, "lern_course")
        #         update.message.reply_text(answer)
        #     else:
        #         update.message.reply_text(answer)
        # else:
            #   Предоставление выбора курса
        list_name_id = data.get_name_and_id_for_all_courses(str(update.message.chat_id))
        print_list_button_with_text(update, text="Выберите один из предложенных курсов",
                                    button_list=list_name_id['course_name'],
                                    callback_list=list_name_id["id"], type="choise")

    def checking_for_commands(self,update, context):
        """
        Производит поиск в присланном сообщении комманды. Если команда найдена, то вызывает её обработчик.
        :param message:
        :return: True - команда найдена, иначе False.
        """
        if type(update.message.document)==files.document.Document:
            return False
        if update.message.text[0]=='/':
            message=update.message.text[1:]
        else:
            message = update.message.text
        if message in self.dict_commands.keys():
            self.dict_commands[message](self,update=update, context=context)
            return True
        elif message in main_menu_buttons.keys():
            #   Была нажата кнопка главного меню
            main_menu_buttons[message](self,update=update, context=context)
            return True
        else:
            return False

    def processing_the_next_dialog_message(self,chat_id,message, context,talk_type):
        """
        Метод высокоуровневой работы с беседами. Либо вызывает очередное действие(создаёт беседу),
        либо возвращает результат беседы.
        :param update:
        :param context:
        :param talk_type:
        :return: None, если не удалось создать новую беседу. answer (type(answer) == dict) ответ, если беседа окончена.
        """
        answer = self.get_answer_from_handler(chat_id,message, context,talk_type)
        #   В случае неудачи начала новой беседы (из-за наличия другой беседы) прерываем функцию
        if answer == False:
            return
        elif type(answer) == dict and answer.get("file")==None:
            # если вернулся словарь,то удаляем диалог (т.к. это конец диалога)
            self.remove_from_handler(chat_id, talk_type)
        return answer

    def get_answer_from_handler(self,chat_id,message, context,talk_type):
        """
        Метод, возвращающий очередную реплику
        :param update:
        :param context:
        :param talk_type:
        :return: Возвращает очередную реплику для беседы (если беседа не закончена). Если не известен тип беседы - False
        """
        id = chat_id
        #   Проверка на наличие уже существующей беседы
        find_type = self.find_talk_type_by_id(id)
        if find_type == None:
            # диалог только начинается. defaultdict запустит новый генератор для этого
            # чатика, а мы должны будем извлечь первое сообщение с помощью .next()
            # (.send() срабатывает только после первого yield)
            self.handlers[talk_type][id]
            return next(self.handlers[talk_type][id])
        elif find_type == talk_type:
            # если диалог уже начат, то надо использовать .send(), чтобы
            # передать в генератор ответ пользователя
            return self.handlers[talk_type][id].send(message)
        else:
            return False

    def redirecting_to_a_conversation(self,update, context):
        """
        Метод перенаправления сообщения на беседу, которая уже ведётся
        :param update:
        :param context:
        :return: None
        """
        self.dict_commands[self.find_talk_type_by_id(str(update.message.chat_id))](self,update=update, context=context)

    def find_talk_type_by_id(self, id):
        """
        Возвращает тип беседы с пользователем по его id.
        :param id:
        :return: Тип беседы в случае успеха, иначе None
        """
        for key, val in self.handlers.items():
            for key1,val1 in val.items():
                if id == key1:
                    return key

    def remove_from_handler(self,chat_id,talk_type):
        """
        Метод удаления отработанной беседы с определённым пользователем.
        :param update:
        :param context:
        :param talk_type:
        :return: True в случае успеха, иначе- False
        """
        try:
            del self.handlers[talk_type][chat_id]
            return True
        except:
            return False

    #   Словарь содержащий в себе название комманды и функцию, отвечающую за отработку этой комманды
    dict_commands = {"start": start_command, "help": help_command, "create_course": create_course_command,
                     "author_registration": author_registration_command, "lern_course": lern_course_command}
main_menu_buttons={"Начать изучение курса":bot.dict_commands["lern_course"], "Создать курс":bot.dict_commands["create_course"]}

def print_list_button_with_text(update, text, button_list,callback_list,type="",replace=False):
    keyboard = [[]]
    for i in range(len(button_list)):
        keyboard[0].append(InlineKeyboardButton(f"{button_list[i]}", callback_data=f"{type}_{callback_list[i]}"))
    reply_markup = InlineKeyboardMarkup(keyboard)
    if replace:
        update.edit_message_text(text, reply_markup=reply_markup)
    else:
        update.message.reply_text(text, reply_markup=reply_markup)

def send_message(chat_id,messages,button_text="",callback_data=""):
    """
    Отправляет различные СООБЩЕНИЯ по указанному chat_id
    :param chat_id:
    :param messages: Список сообщений
    :param button_text: Опционально, добавлении кнопки и её текста
    :param callback_data: Опционально, добавлении возращаемых данных при нажатии кнопки
    :return: None
    """
    for message in messages:
        url = "https://api.telegram.org/bot"
        url += conf.TOKEN
        url = url + "/sendmessage"
        if button_text=="" and callback_data=="":
            r = requests.post(url, data={
                "chat_id": chat_id,
                "text": message
            })
        else:
            json_string = """
                    {
                        "chat_id":"CHAT_ID",
                        "text":"MESSAGE",
                        "reply_markup":{
                           "inline_keyboard": [[
                               {
                                    "text": "BUTTON_TEXT",
                                    "callback_data": "CALLBACK_DATA"
                               }
                                ]]
                            }
                    } """
            json_string = json_string.replace("CHAT_ID", str(chat_id))
            json_string = json_string.replace("MESSAGE", message)
            json_string = json_string.replace("BUTTON_TEXT", button_text)
            json_string = json_string.replace("CALLBACK_DATA", callback_data)
            parsed_string = json.loads(json_string)
            r = requests.get(url , json=parsed_string)
        if r.status_code != 200:
            print(r.text)
            raise Exception("post_text error")

def get_main_menu(update):
    buttons = [[KeyboardButton(i) for i in main_menu_buttons.keys()]]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=buttons,one_time_keyboard=True)
    update.message.reply_text("Выберите,что вы хотите сделать и нажмите соответствующую кнопку!",reply_markup=keyboard)

def clear_main_menu(update):
    update.message.reply_text("Хорошо!")

if __name__ == "__main__":
    bot = bot(dialogsf.dialog_with_customer,dialogsf.dialog_about_create_course,dialogsf.dialog_about_lern_course,dialogsf.dialog_test_by_lesson())
    bot.start()