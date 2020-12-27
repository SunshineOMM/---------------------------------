from datetime import datetime
import input_output_system.telegram_bot as tg_bot
import service_data.data as data
import service_data.leaners_calendar as leaners_calendar
import content_management_system.get_matetrial as get_mat
import time_manager.calendar_methodology as calendar

def lern_new_lesson(id_leaner,id_course,lesson_number):
    """
    Функция принимает параметры нового занятия, заносит в календарь даты повторения
    и формирует текст для отправки в бота
    :param id_leaner:
    :param id_course:
    :param lesson_number:
    :return:
    """
    #   Получаем материал запрашиваемого занятия
    lesson = get_mat.get_lesson(id_course, lesson_number)["text"]
    #   Устанавливаем ближайшее повторение для этого материала
    calendar.create_repeat(id_leaner,id_course,lesson_number)
    #   Устанавливаем изучение следующего занятия, при его наличии
    calendar.create_learn_next_lesson(id_leaner,id_course,lesson_number)
    return f"Изучение занятия {int(lesson_number)+1}\n"+lesson

def repeat_lesson(id_leaner,id_course,lesson_number):
    """
    Функция принимает параметры события повторения занятия и формирует текст для отправки в бота
    :param id_course:
    :param lesson_number:
    :return:
    """
    lesson = get_mat.get_lesson(id_course, lesson_number)["text"]
    course_is_end=calendar.create_repeat(id_leaner, id_course, lesson_number)
    if type(course_is_end)==str:
        lesson+=course_is_end
    progress=leaners_calendar.get_count_repetitions(id_leaner, id_course, lesson_number)
    progress=5-progress
    progress=f"Повторение {int(lesson_number)+1} занятия, прогресс: {progress}/5\n"
    return progress+lesson

def start_test_lesson(id_leaner,id_course,lesson_number):
    lesson=get_mat.get_lesson(id_course,lesson_number)
    list_numbers = [i for i in range(1, int(lesson["tests"][0]["count_all_answers"]) + 1)]
    list_callbacks = [f"{lesson_number}%0%{str(i)}_{id_course}" for i in range(1, int(lesson["tests"][0]["count_all_answers"]) + 1)]
    return [lesson["tests"][0]["question"],list_numbers,list_callbacks,"answerfortest"]

def getting_a_response_to_a_test(id_leaner,id_course, number_lesson, number_test,answer):
    if get_mat.get_correct_answer_test_by_lesson(id_course, number_lesson, number_test)==answer:
        leaners_calendar.change_value_count_correct_answer(id_leaner,id_course, number_lesson,True)

    count_test_by_lesson=get_mat.get_count_test_by_lesson(id_course, number_lesson)
    if  count_test_by_lesson-1 == int(number_test):
        #   Если ответ был для последнего теста
        score=round(leaners_calendar.get_count_correct_user_answer(id_leaner,id_course,number_lesson)/count_test_by_lesson*100)
        if score>=75:
            #   Если был набран необходимый процент, ставим пометку и уведомляем об этом
            leaners_calendar.the_lesson_is_passed(id_leaner, id_course, number_lesson)
            return f"Поздравляю, с успешным прохождением тестирования, Ваш результат: {score}%"
        else:
            #   Если не был набран необходимый процент - удаляем все события,
            #   создаём событие изучения урока заново и выводим сообщение об этом
            leaners_calendar.clear_all_event_for_lesson(id_leaner, id_course, number_lesson)
            calendar.create_learn_next_lesson(id_leaner,id_course,str(int(number_lesson)-1))
            return f"К сожалению, Ваш результат: {score}%, что ниже порога успешного прохождения теста - 75%.\n" \
                   f"Не переживайте, это нормально, просто Вам будет приходить этот материал повторно и в следующий раз " \
                   f"Вы обязательно наберёте нужный процент!"
    else:
        #   Если есть ещё тесты по данному занятию
        lesson = get_mat.get_lesson(id_course, number_lesson)
        number_test=int(number_test)+1
        list_numbers = [i for i in range(1, int(lesson["tests"][number_test]["count_all_answers"]) + 1)]
        list_callbacks = [f"{number_lesson}%{str(number_test)}%{str(i)}_{id_course}" for i in range(1, int(lesson["tests"][int(number_test)]["count_all_answers"]) + 1)]
        return [lesson["tests"][number_test]["question"], list_numbers, list_callbacks, "answerfortest"]

def start_new_course_for_unknow_leaner(id_leaner,id_course):
    """
    :param id:
    :param id_course:
    :return:
    """
    if data.find("leaners", id_leaner)== None:
        create_new_leaner(id_leaner)
    data.add_new_course_for_leaner(id_leaner,id_course)
    if not leaners_calendar.find_leaner(id_leaner):
        leaners_calendar.create_new_leaner(id_leaner)
    start_new_course(id_leaner,id_course)

def start_new_course(id_leaner,id_course):
    leaners_calendar.create_new_course(id_leaner,id_course)
    tg_bot.send_message(id_leaner, ["Добро пожаловать на первое занятие!"], button_text="Нажми, как будешь готов",callback_data=f"learn_0_{id_course}")

def create_new_leaner(id):
    data.add_info("leaners",{"id":id,"name":"","courses":[]})

def daily_calendar_crawl():
    """
    Метод ежесуточного опроса всех учеников о наличии запланированных событий сегодня
    :return: При формировании списка событий вызывает метод отправки учащимся сообщений ботом
    """
    print("Начало метода поиска материала для выдачи")
    dict_with_leaner_id_and_event=leaners_calendar.get_list_of_date_events(datetime.now())
    for leaner_id,events in dict_with_leaner_id_and_event.items():
        for event in events:
            key=list(event.keys())[0]
            but=get_data_for_button(key, event[key]['type'], event[key]['lesson'])
            tg_bot.send_message(leaner_id, messages=but[0],button_text=but[1],callback_data=but[2])

def get_data_for_button(course_id,type_lesson,lesson_number):
     if type_lesson=="learn":
         return [[f"Добро пожаловать на {int(lesson_number) + 1} занятие!"],"Нажми, как будешь готов",f"learn_{lesson_number}_{course_id}"]
     elif type_lesson=="repeat":
         return [[f"Добро пожаловать на повторение {int(lesson_number) + 1} занятия!"], "Нажми, как будешь готов",
          f"repeat_{lesson_number}_{course_id}"]
     elif type_lesson=="test":
         return [[f"Добро пожаловать на тестирование по {int(lesson_number) + 1} занятию!"], "Нажми, как будешь готов",
                 f"test_{lesson_number}_{course_id}"]

if __name__ == "__main__":
    pass





















# class leaner:
#     id=""
#     name=""
#     #   Список со словарями с id курса и текущим изучаемым уроком [{"id_course":.., "progress":..,"calendar":calendar.calendar()}, ...]
#     courses=[]
#
#     def __init__(self,id,name="",courses=[]):
#         self.id=id
#         self.name=name
#         self.courses=courses
#
#     def start_new_course(self,id_course):
#         self.courses.append({"id_course":id_course, "progress":0,"calendar":[]})
#         tg_bot.send_message(self.id, ["Добро пожаловать на первое занятие!"], button_text="Нажми, как будешь готов",callback_data=f"learn_0_{id_course}")

# def get_leaner_by_id_from_data(id):
#     note = data.find("leaners", id)
#     if note!=None:
#         return leaner(note["id"],note["courses"])
# def get_note(self):
#     return {"id":self.id, "name":self.name, "event_list":self.event_list,"progress": self.progress}