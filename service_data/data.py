import json
import uuid
from datetime import datetime
data_path="D:\Rep\Kursach\service_data\data.json"

def find(category,id):
    """
    Производит поиск указанного элемента из указанной категории.
    :param category: "customers" или "leaners" или "courses"
    :param id: уникальный идентификатор элемента
    :return:В случае успеха возвращает элемент целиком, иначе None
    """
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    for i in data[category]:
        if i["id"]==id:
            return i
    return None

def add_info(category,dict_note):
    """
    Производит добавление информиции в базу данных.
    :param category: "customers" или "leaners" или "courses"
    :param dict_note: представление данных класса для базы данных
    :return: При не нахождении нужного id возвращается None.
    Если id найден, но записи идентичны- False. Если запись была изменена, то True.
    Случай пустого контейнера - не определённое поведение.
    """
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    #   Пробегаемся по всем элементам data[category] в поисках совпадения с dict_note["id"]
    for i in range(len(data[category])):
        #   Если нашли
        if dict_note["id"] == data[category][i]["id"]:
            #   Если старая и новая записи отличаются
            if dict_note != data[category][i]["id"]:
                data[category][i] = dict_note
                with open(data_path, 'w', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False,indent=4, sort_keys=True)
                    return True
            else:
                return False

    #   Если попали сюда, значит нужно добавлять новую запись
    data[category].append(dict_note)
    with open(data_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False,indent=4, sort_keys=True)
    return True

def get_count_lesson_in_course(id_course):
    return find("courses",id_course)["lesson_count"]

def get_uniq_id(category):
    while True:
        id = str(uuid.uuid4())
        id=id.replace("_","")
        if find(category,id)==None:
            return id

def get_name_and_id_for_all_courses(leaner_id):
    """
    Возвращает список идентификаторов курсов, доступных для ученика
    :return:
    """
    list_name=[]
    list_id=[]
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    for i in data["courses"]:
        if i["visibility"]== "local" and i["id_customer"]!=leaner_id:
            #   Если курс помечен как локальный и ученик не является его автором, то мы не отображаем этот курс
            continue
        list_name.append(i["course_name"])
        list_id.append(i["id"])
    return {"course_name":list_name,"id":list_id}

def enters_the_final_data_about_course(course_data,chat_id):
    """
    Заносит финальные данные о создаваемом курсе в хранилище
    :param вdata:
    :param chat_id:
    :return:
    """
    course_data.update({"id": get_uniq_id(category="courses"), "rating": "0", "creation_date": str(datetime.now().date()),
                   "id_customer": chat_id})
    add_new_course_for_customers(chat_id,course_data["id"])
    return add_info(category="courses", dict_note=course_data)

def enters_the_final_data_about_author(author_data,chat_id):
    """
    Заносит финальные данные о создаваемом авторе в хранилище
    :param data:
    :param chat_id:
    :return:
    """
    author_data.update({"id": chat_id, "rating": 0, "course_id_list": []})
    return add_info(category="customers", dict_note=author_data)

def enters_the_final_data_about_leaner(leaner_data,chat_id):
    """
    Заносит финальные данные о создаваемом авторе в хранилище
    :param вdata:
    :param chat_id:
    :return:
    """
    leaner_data.update({"id": chat_id, "courses": []})
    return add_info(category="leaners", dict_note=leaner_data)

def add_new_course_for_leaner(chat_id,course_id):
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    for leaner_ind in range(len(data["leaners"])):
        if data["leaners"][leaner_ind]["id"]==chat_id:
            data["leaners"][leaner_ind]["courses"].append(course_id)
            with open(data_path, 'w', encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)
            return True
    return False

def add_new_course_for_customers(chat_id,course_id):
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    for leaner_ind in range(len(data["leaners"])):
        if data["leaners"][leaner_ind]["id"]==chat_id:
            data["leaners"][leaner_ind]["course_id_list"].append(course_id)
            with open(data_path, 'w', encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)
            return True
    return False

def del_info(category, note):
    pass