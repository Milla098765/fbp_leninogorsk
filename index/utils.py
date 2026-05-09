# index/utils.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime
import os
from django.conf import settings
from math import cos, sin, radians

# Регистрируем русские шрифты Times New Roman
try:
    pdfmetrics.registerFont(TTFont('Times-Roman', 'C:/Windows/Fonts/times.ttf'))
    pdfmetrics.registerFont(TTFont('Times-Bold', 'C:/Windows/Fonts/timesbd.ttf'))
    PDF_FONT_NAME = 'Times-Roman'
    PDF_FONT_BOLD = 'Times-Bold'
    print("✅ Times New Roman загружен")
except:
    # Если Times нет, пробуем Arial
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
        PDF_FONT_NAME = 'Arial'
        PDF_FONT_BOLD = 'Arial-Bold'
        print("⚠️ Times New Roman не найден, используем Arial")
    except:
        PDF_FONT_NAME = 'Helvetica'
        PDF_FONT_BOLD = 'Helvetica-Bold'
        print("⚠️ Используем стандартный шрифт Helvetica")

# Для совместимости со старым кодом
FONT_NAME = PDF_FONT_NAME
FONT_BOLD = PDF_FONT_BOLD
FONT_PATH = "C:/Windows/Fonts/times.ttf"

def generate_smeta_pdf(smeta):
    """Генерация официальной сметы расходов"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Заголовок
    c.setFont(PDF_FONT_BOLD, 18)
    c.drawCentredString(width/2, height-50, "СМЕТА РАСХОДОВ")
    c.setFont(PDF_FONT_BOLD, 14)
    c.drawCentredString(width/2, height-70, f"на {smeta.год} год")
    
    c.line(50, height-85, 550, height-85)
    
    # Информация об организации
    y = height - 110
    c.setFont(PDF_FONT_BOLD, 11)
    c.drawString(50, y, "Заказчик:")
    c.setFont(PDF_FONT_NAME, 11)
    c.drawString(120, y, "Администрация города Лениногорск")
    y -= 20
    
    c.setFont(PDF_FONT_BOLD, 11)
    c.drawString(50, y, "ИНН/КПП:")
    c.setFont(PDF_FONT_NAME, 11)
    c.drawString(120, y, f"{smeta.организация.ИНН or '1649000000'} / 164901001")
    y -= 20
    
    c.setFont(PDF_FONT_BOLD, 11)
    c.drawString(50, y, "Юридический адрес:")
    c.setFont(PDF_FONT_NAME, 10)
    c.drawString(180, y, "423250, Республика Татарстан,")
    y -= 15
    c.drawString(180, y, "г. Лениногорск, ул. Ленина, 1")
    y -= 25
    
    # Заголовки таблицы
    c.setFont(PDF_FONT_BOLD, 11)
    c.drawString(50, y, "№")
    c.drawString(80, y, "Наименование работ (услуг)")
    c.drawRightString(400, y, "Сумма (руб.)")
    c.drawString(450, y, "Примечание")
    
    y -= 10
    c.line(50, y, 550, y)
    y -= 20
    
    c.setFont(PDF_FONT_NAME, 11)
    total = 0
    
    # Рассчитываем общую сумму
    for project in smeta.проекты.all():
        total += project.запрашиваемая_сумма
    
    # Выводим проекты
    for i, project in enumerate(smeta.проекты.all(), 1):
        c.drawString(50, y, str(i))
        
        # Название проекта
        name = project.название
        if len(name) > 30:
            name = name[:27] + "..."
        c.drawString(80, y, name)
        
        # Сумма
        c.drawRightString(400, y, f"{project.запрашиваемая_сумма:,.2f}")
        
        # Примечание
        note = project.описание[:15] + "..." if project.описание and len(project.описание) > 15 else (project.описание or "-")
        c.drawString(450, y, note)
        
        y -= 20
        
        if y < 120:
            c.showPage()
            y = height - 80
            c.setFont(PDF_FONT_BOLD, 11)
            c.drawString(50, y, "№")
            c.drawString(80, y, "Наименование работ (услуг)")
            c.drawRightString(400, y, "Сумма (руб.)")
            c.drawString(450, y, "Примечание")
            y -= 10
            c.line(50, y, 550, y)
            y -= 20
            c.setFont(PDF_FONT_NAME, 11)
    
    # Итог
    y -= 10
    c.line(50, y, 550, y)
    y -= 20
    c.setFont(PDF_FONT_BOLD, 12)
    c.drawString(50, y, "ИТОГО:")
    c.drawRightString(550 - 50, y, f"{total:,.2f} руб.")
    
    # Комментарий
    if smeta.комментарий:
        y -= 30
        c.setFont(PDF_FONT_BOLD, 11)
        c.drawString(50, y, "Основание:")
        c.setFont(PDF_FONT_NAME, 11)
        # Разбиваем комментарий на строки
        comment_lines = [smeta.комментарий[i:i+60] for i in range(0, len(smeta.комментарий), 60)]
        for line in comment_lines:
            y -= 15
            c.drawString(130, y, line)
    
    # Подписи
    y = 140
    c.setFont(PDF_FONT_NAME, 11)
    c.drawString(50, y, "Глава администрации города Лениногорск")
    c.drawString(300, y, "_____________ /Петров П.П./")
    y -= 25
    
    c.drawString(50, y, "Главный бухгалтер")
    c.drawString(300, y, "_____________ /Сидорова С.С./")
    y -= 25
    
    c.drawString(50, y, "Начальник финансового отдела")
    c.drawString(300, y, "_____________ /Иванова И.И./")
    
    # Печать Администрации
    draw_stamp_image(c, 450, 80)
    
    # Дата
    today = datetime.now().strftime("%d.%m.%Y")
    c.drawRightString(550, height-50, f"«___» __________ {smeta.год} г.")
    
    c.save()
    buffer.seek(0)
    return buffer


def generate_zayavka_pdf(smeta, data, selected_projects=None):
    """Генерация официального письма-заявки с печатью Администрации"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    c.setFont(PDF_FONT_NAME, 12)
    y = height - 60
    
    # Шапка документа
    c.setFont(PDF_FONT_NAME, 11)
    c.drawRightString(width - 50, y, f"{data['глава_получатель']}")
    y -= 15
    c.drawRightString(width - 50, y, f"{data['должность_получателя']}")
    y -= 25
    
    # Отправитель
    c.setFont(PDF_FONT_NAME, 11)
    c.drawString(50, y, f"от {data['должность_отправителя']}")
    y -= 15
    c.drawString(50, y, f"{data['фио_отправителя']}")
    y -= 30
    
    # Обращение
    c.setFont(PDF_FONT_NAME, 12)
    c.drawString(50, y, f"Уважаемый {data['глава_получатель']}!")
    y -= 30
    
    # Текст письма
    c.drawString(50, y, f"В соответствии с {data['основание']} № {data['номер_соглашения']}")
    y -= 18
    c.drawString(50, y, f"от {data['дата_соглашения'].strftime('%d.%m.%Y')} Администрация города Лениногорск")
    y -= 18
    c.drawString(50, y, f"просит рассмотреть возможность выделения бюджетных средств")
    y -= 18
    c.drawString(50, y, f"{data['учреждение']} на реализацию")
    y -= 18
    c.drawString(50, y, f"мероприятий по развитию города Лениногорск в {smeta.год} году согласно")
    y -= 18
    c.drawString(50, y, f"следующим направлениям:")
    y -= 25
    
    # Проекты
    projects = selected_projects if selected_projects else smeta.проекты.all()
    total = 0
    
    for i, project in enumerate(projects, 1):
        project_text = f"{i}. {project.название}"
        c.drawString(70, y, project_text)
        y -= 18
        
        if project.описание:
            desc_lines = [project.описание[j:j+70] for j in range(0, len(project.описание), 70)]
            for desc_line in desc_lines:
                c.drawString(90, y, desc_line)
                y -= 15
        
        c.drawString(90, y, f"Сумма: {project.запрашиваемая_сумма:,.2f} рублей")
        y -= 20
        total += project.запрашиваемая_сумма
        
        if y < 120:
            c.showPage()
            y = height - 60
            c.setFont(PDF_FONT_NAME, 12)
    
    # Итог
    y -= 10
    c.setFont(PDF_FONT_BOLD, 13)
    c.drawString(50, y, f"Общая сумма: {total:,.2f} рублей")
    y -= 25
    
    # Приложения
    c.setFont(PDF_FONT_BOLD, 11)
    c.drawString(50, y, "Приложения:")
    y -= 18
    c.setFont(PDF_FONT_NAME, 11)
    c.drawString(70, y, "1. Смета расходов с гербовой печатью Администрации;")
    y -= 15
    c.drawString(70, y, f"2. Копия соглашения № {data['номер_соглашения']};")
    y -= 15
    c.drawString(70, y, "3. Пояснительная записка.")
    y -= 25
    
    # Подпись
    c.drawString(50, y, f"{data['должность_отправителя']}")
    y -= 20
    c.drawString(50, y, "_________________________________")
    y -= 15
    c.drawString(50, y, f"({data['фио_отправителя']})")
    y -= 25
    
    # Печать Администрации
    draw_stamp_image(c, 450, 120)
    
    # Исполнитель
    y = 80
    c.setFont(PDF_FONT_NAME, 10)
    c.drawString(50, y, f"Исполнитель: {data['исполнитель']}")
    y -= 15
    c.drawString(50, y, f"Тел.: {data['телефон']}")
    
    c.save()
    buffer.seek(0)
    return buffer


def draw_stamp_image(c, x, y, width=80, height=80):
    """Вставка изображения печати в PDF"""
    try:
        # Путь к изображению - используем BASE_DIR (рабочий путь)
        stamp_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'stamp.png')
        
        print(f"🔍 Ищем штамп: {stamp_path}")
        print(f"📁 Файл существует: {os.path.exists(stamp_path)}")
        
        # Если файл существует, вставляем его
        if os.path.exists(stamp_path):
            stamp = ImageReader(stamp_path)
            c.drawImage(stamp, x - width/2, y - height/2, width=width, height=height, mask='auto')
            print("✅ Штамп успешно вставлен!")
        else:
            # Если файл не найден, рисуем заглушку
            print(f"❌ Файл не найден: {stamp_path}")
            c.setStrokeColor(colors.red)
            c.setFillColor(colors.transparent)
            c.circle(x, y, 30, stroke=1, fill=0)
            c.setFont(PDF_FONT_BOLD, 10)
            c.setFillColor(colors.red)
            c.drawCentredString(x, y-5, "ПЕЧАТЬ")
            
    except Exception as e:
        print(f"❌ Ошибка при вставке штампа: {e}")
        # Заглушка в случае ошибки
        c.setStrokeColor(colors.red)
        c.circle(x, y, 30, stroke=1, fill=0)
        c.setFont(PDF_FONT_BOLD, 10)
        c.drawCentredString(x, y-5, "ПЕЧАТЬ")
        

def generate_budget_smeta_pdf(смета):
    """Генерация PDF сметы бюджета"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Заголовок
    c.setFont(PDF_FONT_BOLD, 18)
    c.drawCentredString(width/2, height-50, f"СМЕТА БЮДЖЕТА НА {смета.год} ГОД")
    
    # Информация
    y = height - 80
    c.setFont(PDF_FONT_NAME, 11)
    c.drawString(50, y, f"Дата создания: {смета.дата_создания.strftime('%d.%m.%Y')}")
    y -= 20
    c.drawString(50, y, f"Статус: {смета.get_статус_display()}")
    y -= 30
    
    # Таблица
    c.setFont(PDF_FONT_BOLD, 11)
    c.drawString(50, y, "№")
    c.drawString(80, y, "Статья расходов")
    c.drawString(300, y, "Сумма (руб.)")
    c.drawString(450, y, "Примечание")
    y -= 10
    c.line(50, y, 550, y)
    y -= 20
    
    c.setFont(PDF_FONT_NAME, 11)
    total = 0
    
    for i, статья in enumerate(смета.статьи.all(), 1):
        c.drawString(50, y, str(i))
        c.drawString(80, y, статья.название[:30])
        c.drawRightString(400, y, f"{статья.сумма:,.2f}")
        c.drawString(450, y, "-")
        
        y -= 20
        total += статья.сумма
        
        if статья.описание:
            c.setFont(PDF_FONT_NAME, 8)
            c.drawString(100, y, статья.описание[:50])
            c.setFont(PDF_FONT_NAME, 11)
            y -= 15
        
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont(PDF_FONT_BOLD, 11)
            c.drawString(50, y, "№")
            c.drawString(80, y, "Статья расходов")
            c.drawString(300, y, "Сумма (руб.)")
            c.drawString(450, y, "Примечание")
            y -= 10
            c.line(50, y, 550, y)
            y -= 20
            c.setFont(PDF_FONT_NAME, 11)
    
    # Итог
    y -= 10
    c.line(50, y, 550, y)
    y -= 20
    c.setFont(PDF_FONT_BOLD, 13)
    c.drawString(50, y, "ИТОГО:")
    c.drawRightString(550 - 50, y, f"{total:,.2f} руб.")
    
    # Подпись
    y = 100
    c.setFont(PDF_FONT_NAME, 11)
    c.drawString(50, y, "Специалист бюджетного отдела")
    c.drawString(300, y, "__________________ /_______________/")
    
    c.save()
    buffer.seek(0)
    return buffer


def generate_budget_pismo_pdf(смета, user):
    """Генерация PDF письма-заявки"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    y = height - 50
    
    c.setFont(PDF_FONT_BOLD, 14)
    c.drawString(50, y, "Руководителю Финансово-бюджетной палаты")
    y -= 20
    c.drawString(50, y, "Лениногорского муниципального района")
    y -= 25
    
    c.setFont(PDF_FONT_NAME, 12)
    c.drawString(50, y, f"от {user.Фамилия} {user.Имя} {user.Отчество or ''}")
    y -= 25
    c.drawString(50, y, f"(специалиста бюджетного отдела)")
    y -= 35
    
    c.setFont(PDF_FONT_BOLD, 14)
    c.drawString(50, y, f"Уважаемый руководитель!")
    y -= 35
    
    c.setFont(PDF_FONT_NAME, 12)
    c.drawString(50, y, f"Представляю на утверждение проект сметы расходов на {смета.год} год.")
    y -= 25
    c.drawString(50, y, "Смета составлена на основе анализа выплат предыдущих периодов")
    y -= 25
    c.drawString(50, y, "и с учетом планируемых мероприятий.")
    y -= 35
    
    c.setFont(PDF_FONT_BOLD, 12)
    c.drawString(50, y, "Основные статьи расходов:")
    y -= 25
    
    c.setFont(PDF_FONT_NAME, 11)
    for статья in смета.статьи.all():
        c.drawString(70, y, f"• {статья.название}: {статья.сумма:,.2f} руб.")
        y -= 18
        y -= 5
        
        if y < 120:
            c.showPage()
            y = height - 50
            c.setFont(PDF_FONT_NAME, 11)
    
    y -= 20
    c.setFont(PDF_FONT_BOLD, 12)
    c.drawString(50, y, f"Общая сумма: {смета.общая_сумма:,.2f} руб.")
    y -= 35
    
    c.setFont(PDF_FONT_NAME, 11)
    c.drawString(50, y, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
    y -= 30
    
    c.drawString(50, y, f"{user.Фамилия} {user.Имя}")
    y -= 20
    c.drawString(50, y, "__________________ /_______________/")
    
    c.save()
    buffer.seek(0)
    return buffer


def generate_fbp_smeta_pdf(смета, user=None):
    """Генерация официальной сметы ФБП (Times New Roman)"""
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Верхний колонтитул
        c.setFont(PDF_FONT_BOLD, 14)
        c.drawCentredString(width/2, height-40, "МУНИЦИПАЛЬНОЕ КАЗЕННОЕ УЧРЕЖДЕНИЕ")
        c.setFont(PDF_FONT_BOLD, 14)
        c.drawCentredString(width/2, height-58, "«ФИНАНСОВО-БЮДЖЕТНАЯ ПАЛАТА»")
        c.setFont(PDF_FONT_NAME, 12)
        c.drawCentredString(width/2, height-73, "муниципального образования «Лениногорский муниципальный район»")
        c.drawCentredString(width/2, height-88, "Республики Татарстан")
        
        # Горизонтальная линия
        c.setStrokeColor(colors.black)
        c.line(50, height-100, 550, height-100)
        
        # Заголовок документа
        c.setFont(PDF_FONT_BOLD, 16)
        c.drawCentredString(width/2, height-135, f"СМЕТА РАСХОДОВ ФБП НА {смета.год} ГОД")
        
        # Реквизиты документа
        y = height - 170
        c.setFont(PDF_FONT_NAME, 11)
        c.drawString(50, y, "Дата составления: __________________")
        c.drawRightString(550, y, f"Форма по ОКУД 0501234")
        y -= 20
        c.drawString(50, y, "Номер документа: _____________")
        c.drawRightString(550, y, f"Дата {datetime.now().strftime('%d.%m.%Y')}")
        y -= 30
        
        # Основание
        c.setFont(PDF_FONT_BOLD, 12)
        c.drawString(50, y, "1. ОСНОВАНИЕ ДЛЯ СОСТАВЛЕНИЯ СМЕТЫ")
        y -= 20
        c.setFont(PDF_FONT_NAME, 11)
        if hasattr(смета, 'создана_на_основе_выплат_за_год') and смета.создана_на_основе_выплат_за_год:
            c.drawString(70, y, f"На основании анализа фактических выплат за {смета.создана_на_основе_выплат_за_год} год")
        else:
            c.drawString(70, y, "На основании плановых показателей и прогноза потребностей")
        y -= 25
        
        # Таблица
        c.setFont(PDF_FONT_BOLD, 12)
        c.drawString(50, y, "2. СТАТЬИ РАСХОДОВ")
        y -= 25
        
        # Заголовки таблицы
        c.setFont(PDF_FONT_BOLD, 11)
        c.drawString(50, y, "№")
        c.drawString(80, y, "Код статьи")
        c.drawString(130, y, "Наименование статьи")
        c.drawRightString(500, y, "Сумма (руб.)")
        y -= 10
        c.line(50, y, 550, y)
        y -= 20
        
        c.setFont(PDF_FONT_NAME, 11)
        total = 0
        статьи = смета.статьи.all()
        
        if not статьи:
            c.drawString(80, y, "Статьи расходов отсутствуют")
            y -= 20
        else:
            for i, статья in enumerate(статьи, 1):
                # Номер
                c.drawString(50, y, str(i))
                
                # Код
                code = f"Ст-{i:03d}"
                c.drawString(80, y, code)
                
                # Название
                name = статья.название
                if len(name) > 45:
                    name = name[:42] + "..."
                c.drawString(130, y, name)
                
                # Сумма
                c.drawRightString(500, y, f"{статья.сумма:,.2f}")
                total += статья.сумма
                y -= 18
                
                # Описание
                if статья.описание and статья.описание != "Экономическое обоснование отсутствует":
                    c.setFont(PDF_FONT_NAME, 9)
                    desc = статья.описание[:55] + "..." if len(статья.описание) > 55 else статья.описание
                    c.drawString(130, y, desc)
                    y -= 15
                    c.setFont(PDF_FONT_NAME, 11)
                
                if y < 100:
                    c.showPage()
                    y = height - 50
                    c.setFont(PDF_FONT_BOLD, 11)
                    c.drawString(50, y, "№")
                    c.drawString(80, y, "Код статьи")
                    c.drawString(130, y, "Наименование статьи")
                    c.drawRightString(500, y, "Сумма (руб.)")
                    y -= 10
                    c.line(50, y, 550, y)
                    y -= 20
                    c.setFont(PDF_FONT_NAME, 11)
        
        # Итоговая сумма
        y -= 20
        c.line(50, y, 550, y)
        y -= 20
        c.setFont(PDF_FONT_BOLD, 13)
        c.drawString(50, y, "ИТОГО ПО СМЕТЕ:")
        c.drawRightString(500, y, f"{total:,.2f}")
        y -= 18
        c.setFont(PDF_FONT_NAME, 11)
        c.drawString(470, y, "рублей")
        
        # Сумма прописью
        y -= 30
        c.setFont(PDF_FONT_BOLD, 11)
        c.drawString(50, y, "Сумма прописью:")
        c.setFont(PDF_FONT_NAME, 11)
        
        # Простое преобразование суммы в пропись (для целых тысяч)
        rub = int(total)
        rub_str = f"{rub:,}".replace(",", " ")
        c.drawString(145, y, f"{rub_str} рублей 00 копеек")
        
        # Подписи
        y = 140
        c.line(50, y, 550, y)
        y -= 25
        
        c.setFont(PDF_FONT_NAME, 11)
        c.drawString(50, y, "Руководитель ФБП")
        c.drawString(250, y, "_________________________")
        if user:
            c.drawString(470, y, f"{user.Фамилия} {user.Имя[0] if user.Имя else ''}.")
        else:
            c.drawString(470, y, "(Фамилия И.О.)")
        y -= 25
        
        c.drawString(50, y, "Главный бухгалтер")
        c.drawString(250, y, "_________________________")
        c.drawString(470, y, "(Фамилия И.О.)")
        y -= 25
        
        c.drawString(50, y, "Начальник отдела планирования")
        c.drawString(250, y, "_________________________")
        c.drawString(470, y, "(Фамилия И.О.)")
        
        # Место печати
        draw_stamp_image(c, 500, 60)
        c.setFont(PDF_FONT_NAME, 10)
        c.drawString(460, 35, "М.П.")
        
        # Нижний колонтитул
        c.setFont(PDF_FONT_NAME, 9)
        c.drawString(50, 25, f"Документ сформирован автоматически {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        c.save()
        buffer.seek(0)
        print(f"✅ PDF сметы ФБП успешно создан, размер: {len(buffer.getvalue())} байт")
        return buffer
        
    except Exception as e:
        print(f"❌ Ошибка в generate_fbp_smeta_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.drawString(100, 500, f"Ошибка создания PDF: {str(e)}")
        c.save()
        buffer.seek(0)
        return buffer


def generate_fbp_pismo_pdf(смета, user):
    """Генерация официального письма-заявки от ФБП (Times New Roman)"""
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Исходящие данные (справа вверху)
        y = height - 50
        c.setFont(PDF_FONT_NAME, 11)
        c.drawRightString(550, y, "Руководителю Министерства финансов")
        y -= 18
        c.drawRightString(550, y, "Республики Татарстан")
        y -= 15
        c.drawRightString(550, y, "Иванову И.И.")
        y -= 25
        
        # Входящие данные (слева)
        c.drawString(50, y, f"Исх. № ________ от {datetime.now().strftime('%d.%m.%Y')}")
        y -= 25
        
        c.setFont(PDF_FONT_NAME, 11)
        c.drawString(50, y, f"На № _________ от _______________")
        y -= 35
        
        # Заголовок
        c.setFont(PDF_FONT_BOLD, 14)
        c.drawCentredString(width/2, y, "ПИСЬМО-ЗАЯВКА")
        y -= 22
        c.setFont(PDF_FONT_NAME, 11)
        c.drawCentredString(width/2, y, f"на выделение бюджетных ассигнований на {смета.год} год")
        y -= 35
        
        # Обращение
        c.setFont(PDF_FONT_NAME, 12)
        c.drawString(50, y, "Уважаемый Иван Иванович!")
        y -= 30
        
        # Текст письма
        c.setFont(PDF_FONT_NAME, 12)
        line1 = "Финансово-бюджетная палата Лениногорского муниципального района"
        c.drawString(50, y, line1)
        y -= 20
        c.drawString(50, y, "направляет на рассмотрение и утверждение проект сметы расходов")
        y -= 20
        c.drawString(50, y, f"на {смета.год} год с общей суммой финансирования в размере")
        y -= 20
        c.setFont(PDF_FONT_BOLD, 12)
        c.drawString(50, y, f"{смета.общая_сумма:,.2f} ({(смета.общая_сумма/1000):.0f} тысяч) рублей.")
        y -= 30
        
        # Основания - нумерованный список
        c.setFont(PDF_FONT_NAME, 12)
        c.drawString(50, y, "Смета составлена на основании:")
        y -= 22
        
        c.drawString(65, y, "1) анализа фактических выплат муниципальным организациям")
        y -= 18
        c.drawString(80, y, "за предыдущие периоды;")
        y -= 18
        c.drawString(65, y, "2) прогноза потребности в бюджетных средствах на текущий год;")
        y -= 18
        c.drawString(65, y, "3) заявок, поступивших от структурных подразделений")
        y -= 18
        c.drawString(80, y, "и организаций города.")
        y -= 25
        
        # Статьи расходов
        c.setFont(PDF_FONT_BOLD, 12)
        c.drawString(50, y, "Статьи расходов, включенные в смету:")
        y -= 25
        
        c.setFont(PDF_FONT_NAME, 11)
        for i, статья in enumerate(смета.статьи.all(), 1):
            name = статья.название
            if len(name) > 50:
                name = name[:47] + "..."
            c.drawString(65, y, f"{i}. {name} - {статья.сумма:,.2f} рублей")
            y -= 18
            
            if y < 120:
                c.showPage()
                y = height - 50
        
        # Общая сумма
        y -= 12
        c.setFont(PDF_FONT_BOLD, 12)
        c.drawString(50, y, f"Общая сумма по смете: {смета.общая_сумма:,.2f} рублей")
        y -= 25
        
        
        # Заключительная часть
        c.setFont(PDF_FONT_NAME, 12)
        c.drawString(50, y, "Просим рассмотреть представленный проект сметы и утвердить")
        y -= 18
        c.drawString(50, y, "указанные объемы финансирования в установленном порядке.")
        y -= 30
        
        # Подпись
        c.drawString(50, y, "С уважением,")
        y -= 25
        
        c.setFont(PDF_FONT_BOLD, 12)
        c.drawString(50, y, "Специалист по бюджету ФБП Лениногорского района")
        y -= 20
        c.setFont(PDF_FONT_NAME, 12)
        c.drawString(50, y, f"{user.Фамилия} {user.Имя} {user.Отчество or ''}")
        y -= 15
        c.drawString(50, y, "_________________________")
        y -= 10
        c.drawString(50, y, "(подпись)")
        
        # Печать
        draw_stamp_image(c, 500, y-20)
        c.setFont(PDF_FONT_NAME, 10)
        c.drawString(480, y-40, "М.П.")
        
        # Исполнитель
        y = 70
        c.setFont(PDF_FONT_NAME, 9)
        c.drawString(50, y, f"Исполнитель: {user.Фамилия} {user.Имя}")
        y -= 12
        c.drawString(50, y, f"Телефон: 8 (85595) 5-00-00")
        y -= 12
        c.drawString(50, y, f"E-mail: fbp-leninogorsk@tatar.ru")
        
        # Нижний колонтитул
        c.setFont(PDF_FONT_NAME, 9)
        c.drawString(50, 25, f"Документ сформирован автоматически {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        c.save()
        buffer.seek(0)
        print(f"✅ PDF письма ФБП успешно создан, размер: {len(buffer.getvalue())} байт")
        return buffer
        
    except Exception as e:
        print(f"❌ Ошибка в generate_fbp_pismo_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.drawString(100, 500, f"Ошибка создания PDF: {str(e)}")
        c.save()
        buffer.seek(0)
        return buffer