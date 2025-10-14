import gspread
from google.oauth2.service_account import Credentials
from database import init_db, clear_schedule, add_schedule_entry
import schedule as sch
import time
from functools import partial

init_db()

def get_schedule():
    creds = Credentials.from_service_account_file(
        "telegram-schedule-bot-471905-0f504bc2d969.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1BMR4Zk3BU2Tyo7L-CYJeMfVuCxjmmT94kfz4Jp6BFAc/edit?pli=1&gid=739453176#gid=739453176").worksheet("1 курс")

    def get_lection_or_seminar(cell):
        cell = cell[0]
        if "лекция" in cell:
            return "Лекция"
        elif "семинар" in cell or "практическое занятие" in cell:
            return "Семинар"
        else:
            return "Семинар"


    def get_lesson(cell):
        cell_lessons = cell[0]
        lessons = ["Программирование C/C++", "Технологии программирования", "Дискретная математика",
                   "Линейная алгебра и геометрия", "Основы российской государственности", "Математический анализ",
                   "Безопасность жинедеятельности", 'НПС "Цифровая грамотность"', "История России",
                   "Программирование на C++"]
        for l in lessons:
            if l in cell_lessons: return l
        return None

    def get_teacher(cell):
        cell_teachers = cell[0]
        teachers = ["Климов А.", "Улитин И.Б.", "Касьянов Н.Ю.",
                    "Малышев Д.С.", "Беспалов П.А.", "Константинова Т.Н.",
                    "Чистякова С.А.", "Савина О.Н.", "Чистяков В.В.", "Городнова А.А.",
                    "Кочеров С.Н.", "Пеплин Ф.С.", "Талецкий Д.С.", "Полонецкая Н.А.",
                    "Марьевичев Н.", "Шапошников В.Е.", "Логвинова К.В.", "Лупанова Е.А.",
                    "Косульников Д.Д."]
        for t in teachers:
            if t in cell_teachers: return t
        return None

    #вспомогательная функция TODO: дописать чтобы делала с xx.xx по xx.xx
    from datetime import datetime, timedelta

    def get_dates(start_str, year=2025):
        end_str = "24.10.2025"
        start_date = datetime.strptime(start_str + "." + f"{year}", "%d.%m.%Y")
        end_date = datetime.strptime(end_str, "%d.%m.%Y")

        dates = []
        current = start_date
        while current <= end_date:
            # выводим только день и месяц
            dates.append(current.strftime("%d.%m"))
            current += timedelta(weeks=1)
        return dates


    def get_weekday_dates(weekday_name: str):
        # Соответствие русских названий дней недели номерам (понедельник=0, воскресенье=6)
        weekdays = {
            "понедельник": 0,
            "вторник": 1,
            "среда": 2,
            "четверг": 3,
            "пятница": 4,
            "суббота": 5,
            "воскресенье": 6
        }

        # Преобразуем входные строки в объекты datetime
        start = datetime.strptime("2025-09-01", "%Y-%m-%d")
        end = datetime.strptime("2025-10-24", "%Y-%m-%d")

        target_weekday = weekdays[weekday_name]

        # Находим первую дату нужного дня недели
        days_until_target = (target_weekday - start.weekday() + 7) % 7
        first_date = start + timedelta(days=days_until_target)

        dates = []
        current_date = first_date
        while current_date <= end:
            dates.append(current_date.strftime("%d.%m"))
            current_date += timedelta(weeks=1)

        return dates

    #определяю дату
    def get_days(cell):
        day_of_week = cell[-1]
        days_of_discipline = cell[0]
        day = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
        month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        days = []
        dates = []
        for d in day:
            for m in month:
                dates.append(d+"."+m+"")
        for date in dates:
            if "с " + date in days_of_discipline:
                return get_dates(date)
        for date in dates:
            if date in days_of_discipline and (not(f"{date} - отмена занятий" in days_of_discipline)): #проверка нет ли отмены занятия
                days.append(date)
        if len(days) == 0:
            days = get_weekday_dates(day_of_week)
        return days

    #проход по всей таблице
    #lecture_columns = ["E", "I", "M", "Q", "U", "Y", "AC"]
    #auditory_columns = ["F", "J", "N", "R", "V", "Z", "AD"]
    #building_columns = ["G", "K", "O", "S", "W", "AA", "AE"]
    #for column in range(0, len(lecture_columns)):
    #    for line in range(12, 49, 9):
    #        ranges = [f"{lecture_columns[column]+str(line)}:{lecture_columns[column]+str(line+7)}", f"{auditory_columns[column]+str(line)}:{auditory_columns[column]+str(line+7)}", f"{building_columns[column]+str(line)}:{building_columns[column]+str(line+7)}", f"B{line}:B{line+7}", f"C{line}:C{line+7}"]
    #        data = (sheet.batch_get(ranges))
    #        for i in range(len(data[0])):
    #            print(data[0][i])

    schedule_for_week = []
    for line in range(12,49, 9):
        if line != 39:
            #тестовый проход по дню
            ranges = [f"AC{line}:AC{line+7}", f"AD{line}:AD{line+7}", f"AE{line}:AE{line+7}", f"B{line}:B{line+7}", f"C{line}:C{line+7}"]
            data = (sheet.batch_get(ranges))
            #кладу данные в новые списки
            disciplines = data[0]
            auditories = data[1]
            buildings = data[2]
            day_of_week = data[3][0][0]
            time = data[4]

            print(disciplines)
            print(auditories)
            print(buildings)
            print(time)
            print(day_of_week)

            #обрезаю время пар под количество пар в день
            len_of_day = len(disciplines)
            time_n = []
            for i in range(len_of_day):
                time_n.append(time[i])
            time = time_n
            print(time)
                                                                                                                                        #   0           1          2       3        4         5
            #что я хочу? я хочу список в котором для одной пары написаны даты, препод, время, название, здание, кабинет. условно pair = ["название", "препод", "время", [даты], "здание", "кабинет"]
            #что надо? взять пару из списка на день, проверить есть ли в ней верхняя и нижняя недели, если есть, то разбить через сплит на 2 пары, если верхняя и нижние пары, то могут отличаться корпуса, кабинеты, их тоже пробить через сплит.
            #надо не забыть про орг и историю, как-то сплитануть, т.к. раньше было орг сейчас история.
            #дальше что? этой паре/парам поставить в соответствие время проведения, всем парам в список засунуть день недели.
            schedule_for_day = []
            for i in range(len_of_day):
                pair = []
                if  len(disciplines[i])>0 and ("------------------------------" in disciplines[i][0] or "---------------------" in disciplines[i][0]):
        #может не быть пары на верхней или нижней неделе, надо не забыть проверить длину строки
                    if "------------------------------" in disciplines[i][0]:
                        upper_week_discipline, lower_week_discipline = disciplines[i][0].replace("\n", "").split("------------------------------")
                    elif "---------------------" in disciplines[i][0]:
                        upper_week_discipline, lower_week_discipline = disciplines[i][0].replace("\n", "").split("---------------------")
                    #print(upper_week_discipline)
                    #print(lower_week_discipline)
                    if "----" in auditories[i][0]:
                        upper_week_auditorie, lower_week_auditorie = auditories[i][0].replace("\n", "").split("----")
                    elif "---" in auditories[i][0]: #первый индекс везде поменять на i в цикле
                        upper_week_auditorie, lower_week_auditorie = auditories[i][0].replace("\n", "").split("---")
                    #print(upper_week_auditorie)
                    #print(lower_week_auditorie)
                    else:
                        upper_week_auditorie = auditories[i][0].replace("\n", "")
                        lower_week_auditorie = auditories[i][0].replace("\n", "")
            #            print(upper_week_auditorie)
            #            print(lower_week_auditorie)
                    if len(buildings[2])>0 and "----" in buildings[i][0]:
                        upper_week_building, lower_week_building = buildings[i][0].replace("\n", "").split("----")
            #            print(upper_week_building)
            #            print(lower_week_building)
                    else: #len(building[2])>0 and (not("----" in building[i][0])):
                        upper_week_building = buildings[i][0].replace("\n", "")
                        lower_week_building = buildings[i][0].replace("\n", "")
            #            print(upper_week_building)
            #            print(lower_week_building)
            #        else:
            #            upper_week_building = []
            #            lower_week_building = []
                    upper_week_pair = [upper_week_discipline, upper_week_auditorie, upper_week_building, time[i][0], day_of_week]
                    lower_week_pair = [lower_week_discipline, lower_week_auditorie, lower_week_building, time[i][0], day_of_week]
            #       print("верхняя неделя",upper_week_pair)
            #       print("нижняя неделя", lower_week_pair)
                    pair = [upper_week_pair, lower_week_pair]
                    if len(upper_week_pair[0])==0:
                        pair = lower_week_pair
                    if len(lower_week_pair[0])==0:
                        pair = upper_week_pair
                elif len(disciplines[i])>0:
                    discipline = disciplines[i][0].replace("\n", "")
                    auditorie = auditories[i][0].replace("\n", "")
                    building = buildings[i][0].replace("\n", "")
                    if "Основы российской государственности" in discipline and "История России" in discipline:
                        a, discipline = discipline.split("М_ОРГ_Г_958391_168")
                    pair = [discipline, auditorie, building, time[i][0], day_of_week]
                    #print("обычная неделя", pair)
                print(pair)
                if len(pair)==2:
                    schedule_for_day.append(pair[0])
                    schedule_for_day.append(pair[1])
                elif len(pair)==0:
                    var = None
                else:
                    schedule_for_day.append(pair)
            print(schedule_for_day)
            schedule_for_day_recycled = []
            for lesson in schedule_for_day:
                lesson = [get_lesson(lesson), get_teacher(lesson), lesson[3], lesson[1], lesson[2], get_days(lesson), get_lection_or_seminar(lesson)]
                schedule_for_day_recycled.append(lesson)
            print("финальное расписание")
            for lesson in schedule_for_day_recycled:
                print(lesson)

            print(schedule_for_day_recycled)
            schedule_for_week.append(schedule_for_day_recycled)

    clear_schedule()  # очищаем старые данные

    for schedule_for_day_recycled in schedule_for_week:
        for lesson in schedule_for_day_recycled:
            subject = lesson[0]
            teacher = lesson[1]
            time = lesson[2]
            classroom = lesson[3]
            building = lesson[4]
            dates = lesson[5]
            type = lesson[6]

            for d in dates:
                add_schedule_entry(subject, teacher, time, classroom, building, d, type)

sch.every(12).hours.do(partial(get_schedule))
while True:
    sch.run_pending()
    time.sleep(10)