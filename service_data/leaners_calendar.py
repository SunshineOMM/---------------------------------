from dateutil.parser import parse
import content_management_system.get_matetrial as get_mat
import service_data.data as service_data
import threading
# import os
# data_path=os.path.abspath('leaners_calendar.json ')
#data_path="D:/projects/tgbot_Interactive-learning-program/service_data/leaners_calendar.json"
import pathlib
data_path = pathlib.Path('service_data/leaners_calendar.json')
LOCK = threading.RLock()

def add_event(leaner_id,course_id,event_id,event):
    """
    Добавление нового события
    :param leaner_id:
    :param course_id:
    :param event_id:
    :param event:
    :return: При не нахождении нужного id False. В случае успеха - True.
    """
    with LOCK:
        #   Получения данных из json файла
        data=get_mat.get_data_from_json(data_path)
        if checking_for_availability(leaner_id,course_id):
            data["leaners"][leaner_id][course_id].update({event_id:event})
            get_mat.enter_data(data_path,data)
            return True
        else:
            return False







        # # Попадаем сюда, если ещё нет записей о данным пользователе
        # data["leaners"].append({"leaner_id":leaner_id,"calendar":[dict_note]})
        # get_mat.enter_data(data_path,data)
        # return True

def checking_for_availability(leaner_id,course_id):
    data = get_mat.get_data_from_json(data_path)
    leaner = data["leaners"].get(leaner_id)
    if leaner == None:
        return False
    course = leaner.get(course_id)
    if course == None:
        return False
    return True

def add_events(leaner_id,course_id,events):
    """
    Производит добавление событий в базу данных по id ученика.
    :param leaner_id:
    :param events: {event_id:event}
    :return: При не нахождении нужного id или при наличии идентичной записи возвращается False.
    В случае успеха - True.
    """
    with LOCK:
        for event_id,event in events.items():
            if add_event(leaner_id,course_id,event_id,event)==False:
                return False
        return True

def add_leaner(leaner_id):
    """
    Добавляет нового ученика в базу данных, хранящую в себе очередные события
    :param leaner_id:
    :return:
    """
    with LOCK:
        #   Получения данных из json файла
        data = get_mat.get_data_from_json(data_path)
        data["leaners"].update({leaner_id:{}})
        get_mat.enter_data(data_path,data)

def del_event_by_id(event_id):
    """
    Удаляет событие из leaners_calendar.json по его id
    :param event_id:
    :return: None
    """
    with LOCK:
        data = get_mat.get_data_from_json(data_path)
        location = find_event_location(event_id)
        if location != None:
            del data["leaners"][location[0]][location[1]][event_id]
            get_mat.enter_data(data_path, data)
            return True
        return False

def del_event_by_location(leaner_id,course_id,event_id):
    with LOCK:
        try:
            data = get_mat.get_data_from_json(data_path)
            del data["leaners"][leaner_id][course_id][event_id]
            get_mat.enter_data(data_path, data)
            return True
        except:
            return False

def get_list_of_date_events(date):
    """
    Смотрит в список всех событий и возвращает те события, которые запланированы на указанную дату.
     Перед отправкой удаляет отправленные события из списка.
    :param date: дата, по которой идёт отбор событий
    :return: Возвращает словарь в формате
    """
    with LOCK:
        data = get_mat.get_data_from_json(data_path)
        dict_all_events_for_all_leaners= {}
        list_with_location_event_by_del=[]
        for id_leaner,courses in data["leaners"].items():
            list_all_events_for_one_leaner = []
            for id_course,course in courses.items():
                for id_event, event in course.items():
                    if id_event=="course_progress":
                        continue
                    date_and_time = parse(event["date"])
                    if date_and_time.day == date.day and date_and_time.hour == date.hour and date_and_time.minute == date.minute:
                        list_all_events_for_one_leaner.append({id_course:event})
                        list_with_location_event_by_del.append((id_leaner,id_course,id_event))
            dict_all_events_for_all_leaners.update({id_leaner: list_all_events_for_one_leaner})

        for event_location in list_with_location_event_by_del:
            del_event_by_location(*event_location)

        return dict_all_events_for_all_leaners

def find_event(event_id):
    """
    Поиск события по его id
    :param event_id:
    :return: Запись события в случае успеха, иначе None
    """
    with LOCK:
        data = get_mat.get_data_from_json(data_path)
        location=find_event_location(event_id)
        if location!=None:
            return data["leaners"][location[0]][location[1]][event_id]

def find_event_location(event_id):
    """
    Поиск местоположения события по его id
    :param event_id:
    :return: Запись события в случае успеха, иначе None
    """
    with LOCK:
        data = get_mat.get_data_from_json(data_path)
        for id_leaner,courses in data["leaners"].items():
            for id_course,course in courses.items():
                for id_event, event in course.items():
                    if id_event==event_id:
                        return (id_leaner,id_course)

def no_events_for_the_lesson(leaner_id,id_course,lesson_number):
    """
    Метод, проверяющий наличие событий по уроку
    :param leaner_ind:
    :param id_course:
    :param lesson_number:
    :return: False, если события ещё есть,иначе - True
    """
    with LOCK:
        if checking_for_availability(leaner_id,id_course):
            data = get_mat.get_data_from_json(data_path)
            for id_event,event in data["leaners"][leaner_id][id_course].items():
                if id_event=="course_progress":
                    continue
                if event["lesson"]==lesson_number:
                    return False
        return True

def get_unique_event_id(string):
    with LOCK:
        while True:
            string += '1'
            _id = str(id(string))
            if find_event(_id) == None:
                return _id

def is_lesson_learned(leaner_id,id_course,lesson_number):
    """
    Функция, по заданным данным, даёт ответ имеет ли конкрентое занятие статус пройденного
    :param leaner_id:
    :param id_course:
    :param lesson_number:
    :return: True в случае успеха, иначе False, в случае ошибки None
    """
    with LOCK:
        if checking_for_availability(leaner_id,id_course) == None:
            return None
        data = get_mat.get_data_from_json(data_path)
        return data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["test"]=="1"

def are_the_repetitions_finished(leaner_id,id_course,lesson_number):
    """
    Функция, дающая ответ есть ли ещё повторения по указанному занятию
    :param leaner_id:
    :param id_course:
    :param lesson_number:
    :return: True в случае успеха, иначе False, в случае ошибки None
    """
    with LOCK:
        if checking_for_availability(leaner_id, id_course) == None:
            return None
        data = get_mat.get_data_from_json(data_path)
        return data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["repeat"]=="0"

def get_count_repetitions(leaner_id,id_course,lesson_number):
    with LOCK:
        if checking_for_availability(leaner_id,id_course):
            data = get_mat.get_data_from_json(data_path)
            return int(data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["repeat"])

def decrement_of_repetitions(leaner_id,id_course,lesson_number):
    with LOCK:
        if checking_for_availability(leaner_id,id_course):
            data = get_mat.get_data_from_json(data_path)
            cur_val=data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["repeat"]
            cur_val=int(cur_val)-1
            data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["repeat"]=str(cur_val)
            get_mat.enter_data(data_path, data)
        else:
            return False

def create_new_leaner(leaner_id):
    with LOCK:
            data = get_mat.get_data_from_json(data_path)
            data["leaners"].update({leaner_id:{}})
            get_mat.enter_data(data_path, data)

def create_new_course(leaner_id,id_course):
    with LOCK:
        data = get_mat.get_data_from_json(data_path)
        tmp_list=[]
        for i in range(int(service_data.get_count_lesson_in_course(id_course))):
            tmp_list.append({"repeat": "2","test": "0","count_correct_user_answer":"0"})
        data["leaners"][leaner_id].update({id_course:{"course_progress": tmp_list}})
        get_mat.enter_data(data_path, data)

def find_leaner(leaner_id):
    with LOCK:
        data = get_mat.get_data_from_json(data_path)
        for id_leaner,leaner_data in data["leaners"].items():
            if leaner_id==id_leaner:
                return True
        return False

def change_value_count_correct_answer(leaner_id,id_course,lesson_number,bool_value):
    with LOCK:
        try:
            data = get_mat.get_data_from_json(data_path)
            count_correct_user_answer=int(data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["count_correct_user_answer"])
            if bool_value:
                count_correct_user_answer+=1
            else:
                count_correct_user_answer-=1
            data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["count_correct_user_answer"]=str(count_correct_user_answer)
            get_mat.enter_data(data_path, data)
            return True
        except:
            return False

def get_count_correct_user_answer(leaner_id,id_course,lesson_number):
    with LOCK:
        try:
            data = get_mat.get_data_from_json(data_path)
            return int(data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["count_correct_user_answer"])
        except:
            return False

def clear_all_event_for_lesson(leaner_id,id_course,lesson_number):
    with LOCK:
        try:
            list_with_location_event_for_del=[]
            data = get_mat.get_data_from_json(data_path)
            for id_event,event in data["leaners"][leaner_id][id_course].items():
                if id_event=="course_progress":
                    continue
                elif event["lesson"]==lesson_number:
                    list_with_location_event_for_del.append((leaner_id,id_course,id_event))
            for i in list_with_location_event_for_del:
                del_event_by_location(*i)
            return True
        except:
            return False

def reset_values_of_the_lesson(leaner_id,id_course,lesson_number):
    with LOCK:
        try:
            data = get_mat.get_data_from_json(data_path)
            data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]=\
                {"repeat": "6","test": "0","count_correct_user_answer":"0"}
            get_mat.enter_data(data_path, data)
            return True
        except:
            return False

def the_lesson_is_passed(leaner_id,id_course,lesson_number):
    with LOCK:
        try:
            data = get_mat.get_data_from_json(data_path)
            data["leaners"][leaner_id][id_course]["course_progress"][int(lesson_number)]["test"]="1"
            get_mat.enter_data(data_path, data)
            return True
        except:
            return False

if __name__ == "__main__":
    pass
    # for i in range(3):
    #     print(is_lesson_learned("342564034","8f7f1fd5-2573-47e4-9146-154dbc197c86",str(i)))

    # print(add_event("342564034", "8f7f1fd5-2573-47e4-9146-154dbc197c86", "testtesttesttest",
    #           {"date": "str(tmp_date)", "type": "learn", "lesson": "str(int(number_lesson)+1)"}))

    #add_leaner("best")

    #print(find_event_location("2222222"))

    #print(find_event("2222222"))

    # print(del_event_by_id("2222222"))
    #
    #print(get_list_of_date_events(parse("2020-12-24 23:07:39.445487")))

    #print(del_event_by_location("342564034", "8f7f1fd5-2573-47e4-9146-154dbc197c86", "testtesttesttest"))

    #print(no_events_for_the_lesson("342564034","8f7f1fd5-2573-47e4-9146-154dbc197c86","8"))

    # print(is_lesson_learned("342564034","8f7f1fd5-2573-47e4-9146-154dbc197c86","1"))
    #
    # print(are_the_repetitions_finished("342564034","8f7f1fd5-2573-47e4-9146-154dbc197c86","1"))

    #create_new_leaner("999999999")

    #create_new_course("999999999", "8f7f1fd5-2573-47e4-9146-154dbc197c86")

    #print(find_leaner("342564034"))

    # change_value_count_correct_answer("342564034", "8bfec8d0-9b65-4596-b97c-844f1823cbfc",
    #                                   "0", True)

    #print(get_count_correct_user_answer("342564034", "8bfec8d0-9b65-4596-b97c-844f1823cbfc","0"))

    #print(clear_all_event_for_lesson("342564034", "8bfec8d0-9b65-4596-b97c-844f1823cbfc","1"))

    #the_lesson_is_passed("342564034", "8bfec8d0-9b65-4596-b97c-844f1823cbfc","2")