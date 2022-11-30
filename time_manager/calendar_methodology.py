from datetime import datetime, timedelta
import service_data.leaners_calendar as leaners_calendar
import service_data.data as data
import content_management_system.get_matetrial as get_mat

# tech_of_repet= [{"minutes":5,"hours":0,"days":0},{"minutes":25,"hours":8,"days":0},{"minutes":0,"hours":0,"days":1},
#                 {"minutes":0,"hours":0,"days":16},{"minutes":0,"hours":0,"days":75}]

#   Тестировочная версия повторений
tech_of_repet=[{"minutes":1,"hours":0,"days":0},{"minutes":1,"hours":0,"days":0}]

# LERN_PERIOD={"minutes":0,"hours":0,"days":3}

#   Тестировочная версия интервала изучения нового занятия
LERN_PERIOD={"minutes":1,"hours":0,"days":0}

def create_repeat(id_leaner,id_course,number_lesson):
    if not leaners_calendar.are_the_repetitions_finished(id_leaner,id_course,number_lesson):
        leaners_calendar.decrement_of_repetitions(id_leaner,id_course,number_lesson)
        count_repetitions=leaners_calendar.get_count_repetitions(id_leaner,id_course,number_lesson)
        if count_repetitions==0:
            if int(data.get_count_lesson_in_course(id_course))-1==int(number_lesson):
                return f"\n\n\nНа этом всё) Поздравляю с успешным прохождением курса: {data.find('courses',id_course)['course_name']}!!!"
            else:
                return False
        elif count_repetitions==1 and not get_mat.is_empty_test(id_course,number_lesson):
            create_test_by_lesson(id_leaner, id_course, number_lesson)
        td = timedelta(days=tech_of_repet[count_repetitions-1]["days"], hours=tech_of_repet[count_repetitions-1]["hours"],
                       minutes=tech_of_repet[count_repetitions-1]["minutes"])
        tmp_date = datetime.now()+td
        return leaners_calendar.add_event(id_leaner, id_course,
                                          leaners_calendar.get_unique_event_id(
                                              id_leaner + id_course + number_lesson + str(tmp_date)),
                                          {"date": str(tmp_date), "type": "repeat", "lesson": number_lesson})
    else:
        return False

def create_test_by_lesson(id_leaner,id_course,number_lesson):
    td = timedelta(days=0, hours=0, minutes=1)
    tmp_date = datetime.now() + td
    return leaners_calendar.add_event(id_leaner, id_course,
                                      leaners_calendar.get_unique_event_id(id_leaner + id_course + number_lesson + str(tmp_date)),
                                      {"date": str(tmp_date), "type": "test", "lesson": number_lesson})

def create_learn_next_lesson(id_leaner,id_course,number_lesson):
    """
    Добавление события изучения следующего занятия
    :param id_leaner:
    :param id_course:
    :param number_lesson: тема, по которой произошло срабатывание сигнала
    :param date_signal: дата возникновения сигнала
    :return: Возвращает True в случае успеха, иначе - False
    :param id_leaner:
    :param id_course:
    :param number_lesson:
    :param date_signal:
    :return:
    """
    if int(number_lesson) < int(data.get_count_lesson_in_course(id_course)) - 1:
        td = timedelta(days=LERN_PERIOD["days"], hours=LERN_PERIOD["hours"], minutes=LERN_PERIOD["minutes"])
        tmp_date = datetime.now() + td
        return leaners_calendar.add_event(id_leaner,id_course,
                                          leaners_calendar.get_unique_event_id(id_leaner+id_course+number_lesson+str(tmp_date)),
                                          {"date": str(tmp_date), "type": "learn", "lesson": str(int(number_lesson)+1)})
    else:
        return False

if __name__ == "__main__":
    for i in range(7):
        print(create_test_by_lesson("342564034", "8bfec8d0-9b65-4596-b97c-844f1823cbfc","2"))















# def create_repeat_plan(id_leaner,id_course,number_lesson,date_signal=datetime.now()):
#     """
#     Построение списка событий с их описанием, формат: [{"event_id":..,"course_id":.., "date":..,"type":..,"lesson":..},...]
#     :param id_leaner:
#     :param id_course:
#     :param number_lesson: тема, по которой произошло срабатывание сигнала
#     :param date_signal: дата возникновения сигнала
#     :return: Возвращает True в случае успеха, иначе - False
#     """
#     repeat_event_calendar=[]
#     for node in tech_of_repet:
#         td=timedelta(days=node["days"],hours=node["hours"],minutes=node["minutes"])
#         tmp_date=date_signal+td
#         repeat_event_calendar.append(
#             {"event_id": leaners_calendar.get_unique_event_id(id_leaner+id_course+number_lesson+str(tmp_date)), "course_id": id_course,
#              "date": str(tmp_date), "type": "repeat", "lesson": number_lesson})
#
#     return leaners_calendar.add_events(id_leaner,repeat_event_calendar)