import service_data.data as data
import json
def get_lesson(id_course,number_lesson):
    """
    Возвращает нужное занятие по указанному курсу
    :param id_course:
    :param number_lesson:
    :return: Необходимое занятие, иначе - None
    """
    number_lesson=int(number_lesson)
    course_node=data.find("courses",id_course)
    with open(course_node["json_source_path"],encoding="utf-8") as f:
        course = json.load(f)
    lessons=course["lessons"]
    #print(f"get_lesson:{number_lesson} < {len(lessons)}")
    if number_lesson<len(lessons):
        return course["lessons"][number_lesson]

def enter_data(data_path,data):
    """
    Метод ввода данных в json файл
    :param data_path:
    :return: None
    """
    with open(data_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)

def is_empty_test(id_course,number_lesson):
    """
    Метод проверки наличия теста в занятии
    :param id_course:
    :return: True при отсутствии, иначе - False
    """
    number_lesson=int(number_lesson)
    course_node = data.find("courses", id_course)
    with open(course_node["json_source_path"], encoding="utf-8") as f:
        course = json.load(f)
    tests=course["lessons"][number_lesson].get("tests")
    if tests==None or len(tests)==0:
        return True
    else:
        return False

def get_data_from_json(data_path):
    """
    Возврат содержимого json файла
    :param data_path:
    :return: Содержимое в виде json словаря
    """
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
        return data

def get_correct_answer_test_by_lesson(id_course,number_lesson,number_test):
    lesson=get_lesson(id_course, number_lesson)
    return lesson["tests"][int(number_test)]["correct_answer"]

def get_count_test_by_lesson(id_course,number_lesson):
    lesson=get_lesson(id_course, number_lesson)
    tests=lesson.get("tests")
    if tests==None:
        return 0
    else:
        str(len(tests))
    return len(lesson["tests"])

if __name__ == "__main__":
    for i in range(3):
        print(get_count_test_by_lesson("8bfec8d0-9b65-4596-b97c-844f1823cbfc", i))
