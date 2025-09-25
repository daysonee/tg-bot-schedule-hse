import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Определяем доступы
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("telegram-schedule-bot-471905-458c6fcfd4ce.json", scope)

# Авторизация
client = gspread.authorize(creds)

# Открываею таблицу
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1BMR4Zk3BU2Tyo7L-CYJeMfVuCxjmmT94kfz4Jp6BFAc/edit?gid=739453176#gid=739453176").worksheet("1 курс")


def get_lesson(cell):
    lessons = ["Программирование C/C++", "Технологии программирования", "Дискретная математика",
               "Линейная алгебра и геометрия", "Основы российской государственности", "Математический анализ",
               "Безопасность жинедеятельности", 'НПС "Цифровая грамотность"', "История России",
               "Программирование на C++"]
    for l in lessons:
        if l in cell: return l
    return None

def get_teacher(cell):
    teachers = ["Климов А.", "Улитин И.Б.", "Касьянов Н.Ю.",
                "Малышев Д.С.", "Беспалов П.А.", "Константинова Т.Н.",
                "Чистякова С.А.", "Савина О.Н.", "Чистяков В.В.", "Городнова А.А.",
                "Кочеров С.Н.", "Пеплин Ф.С.", "Талецкий Д.С.", "Полонецкая Н.А.",
                "Марьевичев Н.", "Шапошников В.Е.", "Логвинова К.В.", "Лупанова Е.А.",
                "Косульников Д.Д."]
    for t in teachers:
        if t in cell: return t
    return None

#вспомогательная функция TODO: дописать чтобы делала с xx.xx по xx.xx
from datetime import datetime, timedelta

def get_dates(start_str, year=2025):
    end_str = "24.10.2025"
    start_date = datetime.strptime(start_str + f".{year}", "%d.%m.%Y")
    end_date = datetime.strptime(end_str, "%d.%m.%Y")

    dates = []
    current = start_date
    while current <= end_date:
        # выводим только день и месяц
        dates.append(current.strftime("%d.%m"))
        current += timedelta(weeks=1)
    return dates
#определяю дату TODO: добавить не просто cell а индекс, добавить еще одно условие, если нет дней и с xx.xx, то брать день недели и прибавлять 7(скорее всего написать или дописать вспомогательную функцию)
def get_days(cell):
    day = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    days = []
    dates = []
    for d in day:
        for m in month:
            dates.append(d+"."+m+".")
    for date in dates:
        if "с " + date in cell:
            return get_dates(date)
    for date in dates:
        if date in cell and (not(f"{date} - отмена занятий" in cell)): #проверка нет ли отмены занятия
            days.append(date)
    if len(days) > 0:
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

#тестовый проход по дню
ranges = ["E12:E19", "F12:F19", "G12:G19", "B12:B19", "C12:C19"]
data = (sheet.batch_get(ranges))
#кладу данные в новые списки
disciplines = data[0]
auditories = data[1]
building = data[2]
day_of_week = data[3][0][0]
time = data[4]

print(disciplines)
print(auditories)
print(building)
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

if "------------------------------" in disciplines[0][0]:
    upper_week_discipline, lower_week_discipline = disciplines[0][0].replace("\n", "").split("------------------------------")
    print(upper_week_discipline)
    print(lower_week_discipline)
    if "----" in auditories[0][0]:
        upper_week_auditories, lower_week_auditories = auditories[0][0].replace("\n", "").split("----")
        print(upper_week_auditories)
        print(lower_week_auditories)
    else:
        upper_week_auditories = auditories[0][0].replace("\n", "")
        lower_week_auditories = auditories[0][0].replace("\n", "")
        print(upper_week_auditories)
        print(lower_week_auditories)
    if "----" in building[0][0]:
        upper_week_building, lower_week_building = building[0][0].replace("\n", "").split("----")
        print(upper_week_building)
        print(lower_week_building)
    else:
        upper_week_building = building[0][0].replace("\n", "")
        lower_week_building = building[0][0].replace("\n", "")
        print(upper_week_building)
        print(lower_week_building)
    upper_week_pair = [upper_week_discipline, upper_week_auditories, upper_week_building, time[0][0]]
    lower_week_pair = [lower_week_discipline, lower_week_auditories, lower_week_building, time[0][0]]
    print(upper_week_pair)
    print(lower_week_pair)