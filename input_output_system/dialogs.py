import os
import pathlib
import content_management_system.input_doc_class as input_doc_class
import input_output_system.service_data as service_data

def dialog_with_customer():
    try:
        #   Введите имя
        answer = yield "Здравствуйте! Как зовут вас?"
        # убираем ведущие знаки пунктуации, оставляем только
        # первую компоненту имени, пишем её с заглавной буквы
        name = answer.text.rstrip(".!, :;").split()[0].capitalize()
        #   Введите дополнительную информацию(должность, профессиональная сфера, интересы, о себе)
        description = yield f"Приятно познакомиться {name}! Ведите дополнительную информацию (должность, профессиональная сфера, интересы, о себе)"
        description=description.text
        #   Инструктаж по взаимодействию
        yield {"name":name,"description":description}
        return
    except:
        yield service_data.str_error_for_registration

def dialog_about_create_course():
    try:
        #   Ввод дополнительной информации(кому предназначается, особенности, какие компетенции закрывает)
        description = yield "Введите дополнительную информацию о курсе(кому предназначается, особенности, какие компетенции закрывает)"
        description = description.text
        level_of_complexity=yield "Укажите предполагаемую сложность курса от 0 до 10"
        level_of_complexity=level_of_complexity.text
        #   Проверка на ввод целого числа в заданном диапазоне
        if int(level_of_complexity)<0 or int(level_of_complexity)>10:
            raise
        # lesson_count = yield "Укажите количество разделов( 1 раздел = 1 занятие)"
        visibility=yield "Укажите видимость создаваемого курса 'мне'- отображаться будет только у Вас," \
                         " 'всем'- доступен будет всем пользователям "
        visibility=visibility.text
        if visibility=='всем':
            visibility="global"
        elif visibility=='мне':
            visibility="local"
        else:
            raise

        file = yield {"text":"Пожалуйста, оформите в соответствии с образцом и прикрепите файл с материалом (расширение docx).","file":""}
        data_dict=handler_doc(file)

        yield {"course_name": data_dict["course_name"], "description": description,"json_source_path":data_dict["json_source_path"],"level_of_complexity":level_of_complexity,"lesson_count":data_dict["count_lesson"],"visibility":visibility}
        return
    except:
        yield service_data.str_error_for_create_course

def handler_doc(update):
    """
    Вызывается при отсылке файла курса. Подготовливает правильный путь сохранения и скачивет туда этот файл.
    Далее создаёт класс обработки данных и запускает процесс классификации присланных данных.
    :param update:
    :return: Возвращает словарь, содержащий путь  в каталоге на классифицированные данные, имя курса, количество занятий в случае успеха, иначе None
    """
    #   Формирование названия папки
    abs_path=os.path.abspath("content_management_system")
    direction_name=f"{abs_path}\input_documents\{update.chat.id}"
    #   Проверка наличия папки автора, и если такой нет, то её создание
    if not os.path.exists(direction_name):
        os.mkdir(direction_name)
    #   Подготовительные работы
    doc=update.document
    file_extension=pathlib.Path(doc.file_name).suffix
    file_name=str(update.date)[:10]
    #   Скачивание документа
    doc.get_file().download(custom_path=f"{direction_name}\{file_name}{file_extension}")
    #    Создение класса для работы с документами
    absolute_path=os.path.abspath(f"{direction_name}\{file_name}{file_extension}")
    input_doc=input_doc_class.input_doc(absolute_path,file_extension)
    print("Распознано получение файла!")
    #   Классификация полученного текста
    json_source_path=input_doc.add_JSON_to_folder()
    return {"json_source_path":json_source_path,"course_name":input_doc.course_name,"count_lesson":input_doc.count_lesson}

def dialog_about_lern_course():
    try:
        #   Введите имя
        answer = yield "Здравствуйте! Как зовут вас?"
        # убираем ведущие знаки пунктуации, оставляем только
        # первую компоненту имени, пишем её с заглавной буквы
        name = answer.text.rstrip(".!, :;").split()[0].capitalize()
        #   Введите дополнительную информацию(должность, профессиональная сфера, интересы, о себе)
        description = yield f"Приятно познакомиться {name}! Ведите необязательную информацию о себе (это нужно для того, чтобы лучше понимать аудиторию этого курса)"
        description=description.text
        yield {"name": name, "description": description}
        return

    except:
        yield service_data.str_error_for_registration

