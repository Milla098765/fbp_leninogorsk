from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.urls import reverse  # Добавить этот импорт
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

class Отдел(models.Model):
    Название = models.CharField(max_length=100)

    def __str__(self):
        return self.Название

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    Отдел = models.ForeignKey(Отдел, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username if hasattr(self, 'user') else 'Профиль'

class Организация(models.Model):
    ПолноеНаименование = models.CharField(max_length=200)

    инн_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='ИНН должен содержать ровно 10 цифр.'
    )
    счет_validator = RegexValidator(
        regex=r'^\d{20}$',
        message='Счет организации должен содержать ровно 20 цифр.'
    )

    ИНН = models.CharField(max_length=10, validators=[инн_validator], unique=True, null=True, blank=True)
    СчетОрганизации = models.CharField(max_length=20, validators=[счет_validator], null=True, blank=True)
    Логин = models.CharField(max_length=50, unique=True)
    Пароль = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.ПолноеНаименование

    def set_password(self, raw_password):
        """Установка хэшированного пароля"""
        self.Пароль = make_password(raw_password)

    def check_password(self, raw_password):
        """Проверка пароля"""
        if self.Пароль:
            return check_password(raw_password, self.Пароль)
        return False

    # ДОБАВЛЯЕМ ВСЕ НЕОБХОДИМЫЕ МЕТОДЫ ДЛЯ СОВМЕСТИМОСТИ
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_staff(self):
        return False

    @property
    def is_superuser(self):
        return False

    def get_username(self):
        return self.Логин

    def has_perm(self, perm, obj=None):
        return False

    def has_module_perms(self, app_label):
        return False

    def save(self, *args, **kwargs):
        """Автоматически хешируем пароль при сохранении, если он был изменен"""
        if self.Пароль and not self.Пароль.startswith('pbkdf2_sha256$'):
            self.set_password(self.Пароль)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

class Пользователь(models.Model):
    Имя = models.CharField(max_length=50)
    Фамилия = models.CharField(max_length=50)
    Отчество = models.CharField(max_length=50, blank=True, null=True)
    Роль = models.CharField(
        max_length=50, 
        choices=[('user', 'Пользователь'), ('superuser', 'Суперюзер')],
        default='user'
    )
    Логин = models.CharField(max_length=50, unique=True)
    Пароль = models.CharField(max_length=100)
    Телефон = models.CharField(max_length=20, blank=True, null=True)
    Отдел = models.ForeignKey('Отдел', on_delete=models.SET_NULL, null=True)
    Фото = models.ImageField(upload_to='user_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.Фамилия} {self.Имя}"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
class ТипыДокументов(models.Model):
    Название = models.CharField(max_length=100)

    def __str__(self):
        return self.Название

    class Meta:
        verbose_name = 'Тип документа'
        verbose_name_plural = 'Типы документов'

class ВидыВыплат(models.Model):
    Название = models.CharField(max_length=100)

    def __str__(self):
        return self.Название

    class Meta:
        verbose_name = 'Вид выплаты'
        verbose_name_plural = 'Виды выплат'

class Заявка(models.Model):
    СТАТУС_ВЫБОР = [
        ('new', 'Новая'),
        ('approved', 'Принята'),
        ('rejected', 'Отклонена'),
    ]
    
    организация = models.ForeignKey(Организация, on_delete=models.CASCADE, verbose_name='Организация')
    дата_подачи = models.DateTimeField(auto_now_add=True, verbose_name='Дата подачи')
    полное_наименование = models.CharField(max_length=200, verbose_name='Полное наименование организации')
    инн = models.CharField(max_length=10, verbose_name='ИНН')
    счет_организации = models.CharField(max_length=20, verbose_name='Счет организации')
    
    # Получатель (фиксированные данные)
    получатель = models.CharField(max_length=300, default='Муниципальное казённое учреждение «Финансово-бюджетная палата» муниципального образования «Лениногорский муниципальный район» Республики Татарстан')
    счет_получателя = models.CharField(max_length=20, default='03100643000000011100')
    
    вид_выплаты = models.ForeignKey(ВидыВыплат, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Вид выплаты')
    другой_вид_выплаты = models.CharField(max_length=200, blank=True, null=True, verbose_name='Другой вид выплаты')
    запрашиваемая_сумма = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Запрашиваемая сумма')
    статус = models.CharField(max_length=10, choices=СТАТУС_ВЫБОР, default='new', verbose_name='Статус')
    дата_рассмотрения = models.DateTimeField(null=True, blank=True, verbose_name='Дата рассмотрения')
    
    # НОВЫЕ ПОЛЯ ДЛЯ КОММЕНТАРИЯ ОТКЛОНЕНИЯ
    комментарий_отклонения = models.TextField(blank=True, null=True, verbose_name='Причина отклонения')
    дата_отклонения = models.DateTimeField(blank=True, null=True, verbose_name='Дата отклонения')
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-дата_подачи']

    def __str__(self):
        return f"Заявка от {self.организация.ПолноеНаименование} на {self.запрашиваемая_сумма} руб."

class ДокументЗаявки(models.Model):
    """Модель для хранения документов, прикреплённых к заявке"""
    ТИПЫ_ДОКУМЕНТОВ = [
        ('dogovor', 'Трудовой договор'),
        ('prikaz', 'Приказ'),
        ('tabel', 'Табель учёта времени'),
        ('akt', 'Акт выполненных работ'),
        ('schet', 'Счёт'),
        ('raschet', 'Расчётный лист'),
        ('vedomost', 'Платёжная ведомость'),
        ('other', 'Прочее'),
    ]
    
    заявка = models.ForeignKey(
        Заявка, 
        on_delete=models.CASCADE, 
        related_name='документы'
    )
    тип = models.CharField(max_length=20, choices=ТИПЫ_ДОКУМЕНТОВ, verbose_name='Тип документа')
    название = models.CharField(max_length=200, verbose_name='Название')
    файл = models.FileField(upload_to='zayavki_docs/%Y/%m/', verbose_name='Файл')
    описание = models.TextField(blank=True, verbose_name='Описание')
    дата_загрузки = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Документ заявки'
        verbose_name_plural = 'Документы заявки'
        ordering = ['-дата_загрузки']
    
    def __str__(self):
        return f"{self.get_тип_display()}: {self.название}"

class Выплаты(models.Model):
    СТАТУС_ВЫБОР = [
        ('ожидает', 'Ожидает выплаты'),
        ('выплачено', 'Выплачено'),
        ('отменено', 'Отменено'),
    ]
    
    код_выплаты = models.CharField(max_length=50, unique=True, verbose_name='Код выплаты', blank=True)
    полное_наименование = models.CharField(max_length=200, verbose_name='Полное наименование организации')
    инн = models.CharField(max_length=10, verbose_name='ИНН')
    счет_получателя = models.CharField(max_length=20, verbose_name='Счет получателя')
    статус = models.CharField(max_length=50, choices=СТАТУС_ВЫБОР, default='ожидает', verbose_name='Статус')
    вид = models.ForeignKey(ВидыВыплат, on_delete=models.SET_NULL, null=True, verbose_name='Вид выплаты')
    сумма = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма')
    
    # ИЗМЕНИТЕ ЭТО ПОЛЕ - добавьте related_name
    заявка = models.ForeignKey(
        Заявка, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Связанная заявка',
        related_name='связанные_выплаты'  # ДОБАВЬТЕ ЭТО
    )
    
    дата_создания = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    дата_выполнения = models.DateField(null=True, blank=True, verbose_name='Дата выполнения')
    назначение_платежа = models.TextField(blank=True, verbose_name='Назначение платежа')
    заблокировано = models.BooleanField(default=False, verbose_name='Заблокировано для изменений')
    
    # Новое поле для хранения сгенерированного документа
    документ_создан = models.BooleanField(default=False, verbose_name='Документ создан')

    def __str__(self):
        return f"Выплата {self.код_выплаты} - {self.сумма} руб."

    def save(self, *args, **kwargs):
        # Автоматически генерируем код выплаты если он не задан
        if not self.код_выплаты:
            last_payment = Выплаты.objects.order_by('-id').first()
            last_id = last_payment.id if last_payment else 0
            self.код_выплаты = f"PAY{last_id + 1:06d}"
        
        # Автоматически ставим дату выполнения при статусе "выплачено"
        if self.статус == 'выплачено' and not self.дата_выполнения:
            self.дата_выполнения = timezone.now().date()
            self.заблокировано = True  # Блокируем после выполнения
            self.документ_создан = True  # Помечаем что документ можно создавать
            
        # Если статус меняется с "выплачено" на другой - разблокируем
        if self.статус != 'выплачено':
            self.заблокировано = False
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Выплата'
        verbose_name_plural = 'Выплаты'
        
class ОжидаемаяСуммаВыплат(models.Model):
    год = models.IntegerField(verbose_name='Год', unique=True)
    ожидаемая_сумма_год = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Ожидаемая сумма за год',
        default=0
    )
    дата_создания = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Ожидаемая сумма выплат'
        verbose_name_plural = 'Ожидаемые суммы выплат'
        ordering = ['-год']  # Добавить сортировку по году
    
    def __str__(self):
        return f"Ожидаемая сумма за {self.год} год: {self.ожидаемая_сумма_год} руб."
    
    def is_leap_year(self):
        """Проверка високосного года"""
        year = self.год
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    def get_expected_for_period(self, start_date, end_date):
        """Рассчитать ожидаемую сумму для периода"""
        days_in_period = (end_date - start_date).days + 1
        days_in_year = 366 if self.is_leap_year() else 365
        
        daily_rate = self.ожидаемая_сумма_год / days_in_year
        return daily_rate * days_in_period
    
    def get_expected_for_month(self, month, year=None):
        """Рассчитать ожидаемую сумму для месяца"""
        if year and year != self.год:
            return 0
        
        days_in_month = {
            1: 31, 2: 29 if self.is_leap_year() else 28, 3: 31, 4: 30,
            5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        
        days = days_in_month.get(month, 30)
        days_in_year = 366 if self.is_leap_year() else 365
        
        daily_rate = self.ожидаемая_сумма_год / days_in_year
        return daily_rate * days
    
class ОтчетВыплат(models.Model):
    название = models.CharField(max_length=200, verbose_name='Название отчета')
    дата_создания = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    дата_начала = models.DateField(verbose_name='Дата начала периода')
    дата_окончания = models.DateField(verbose_name='Дата окончания периода')
    фильтр_статус = models.CharField(max_length=20, default='выплачено', verbose_name='Фильтр по статусу')
    организации = models.ManyToManyField('Организация', blank=True, verbose_name='Организации')
    общая_сумма = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Общая сумма выплат')
    количество_выплат = models.IntegerField(verbose_name='Количество выплат')
    
    class Meta:
        verbose_name = 'Отчет выплат'
        verbose_name_plural = 'Отчеты выплат'
        ordering = ['-дата_создания']
    
    def __str__(self):
        org_count = self.организации.count()
        org_text = f" ({org_count} орг.)" if org_count > 0 else " (все организации)"
        return f"Отчет {self.название}{org_text}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('отчет_детали', kwargs={'pk': self.pk})
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
        
class ОтчетПланировщика(models.Model):
    название = models.CharField(max_length=200, verbose_name='Название отчета')
    дата_создания = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    дата_начала = models.DateField(verbose_name='Дата начала периода')
    дата_окончания = models.DateField(verbose_name='Дата окончания периода')
    
    # ОСНОВНЫЕ ПОКАЗАТЕЛИ - то что вы просили!
    ожидаемая_сумма_периода = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Ожидаемая сумма за период', default=0)
    фактическая_сумма_периода = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Фактическая сумма за период', default=0)
    отклонение_суммы = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Отклонение по сумме', default=0)
    
    # Анализ выполнения
    процент_выполнения_плана = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Процент выполнения плана', default=0)
    количество_выплат = models.IntegerField(verbose_name='Количество выплат', default=0)
    
    # Данные для графика в Word
    данные_графика = models.JSONField(verbose_name='Данные для графика', default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Отчет планировщика'
        verbose_name_plural = 'Отчеты планировщика'
        ordering = ['-дата_создания']
    
    def __str__(self):
        return f"Отчет планировщика: {self.название}"
    
    def save(self, *args, **kwargs):
        # Автоматический расчет отклонения и процента выполнения
        self.отклонение_суммы = self.фактическая_сумма_периода - self.ожидаемая_сумма_периода
        if self.ожидаемая_сумма_периода > 0:
            self.процент_выполнения_плана = (self.фактическая_сумма_периода / self.ожидаемая_сумма_периода) * 100
        super().save(*args, **kwargs)
        
# Добавьте эти модели в ваш models.py

class СметаПроект(models.Model):
    """
    Модель для проектов в смете администрации
    """
    название = models.CharField(max_length=200, verbose_name='Название проекта')
    описание = models.TextField(verbose_name='Описание проекта', blank=True)
    запрашиваемая_сумма = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Запрашиваемая сумма')
    
    class Meta:
        verbose_name = 'Проект сметы'
        verbose_name_plural = 'Проекты сметы'
    
    def __str__(self):
        return self.название


class СметаЗатрат(models.Model):
    """
    Модель для смет затрат от администрации
    """
    СТАТУС_ВЫБОР = [
        ('черновик', 'Черновик'),
        ('отправлена', 'Отправлена в бюджетный отдел'),
        ('одобрена', 'Одобрена'),
        ('отклонена', 'Отклонена'),
    ]
    
    организация = models.ForeignKey(Организация, on_delete=models.CASCADE, verbose_name='Организация')
    название = models.CharField(max_length=200, verbose_name='Название сметы')
    год = models.IntegerField(verbose_name='Плановый год')
    дата_создания = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    дата_отправки = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')
    статус = models.CharField(max_length=20, choices=СТАТУС_ВЫБОР, default='черновик', verbose_name='Статус')
    комментарий = models.TextField(blank=True, verbose_name='Комментарий')
    дата_рассмотрения = models.DateTimeField(null=True, blank=True, verbose_name='Дата рассмотрения')
    
    # Связь с проектами
    проекты = models.ManyToManyField(СметаПроект, verbose_name='Проекты', blank=True)
    
    # Общая сумма
    общая_сумма = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Общая сумма сметы', default=0)
    
    class Meta:
        verbose_name = 'Смета затрат'
        verbose_name_plural = 'Сметы затрат'
        ordering = ['-дата_создания']
    
    def __str__(self):
        return f"{self.название} ({self.организация.ПолноеНаименование})"
    
    def save(self, *args, **kwargs):
        if self.pk:
            self.общая_сумма = self.проекты.aggregate(total=models.Sum('запрашиваемая_сумма'))['total'] or 0
        super().save(*args, **kwargs)
    
    def отправить(self):
        self.статус = 'отправлена'
        self.дата_отправки = timezone.now()
        self.save()
    
    def одобрить(self, пользователь, комментарий=''):
        """Одобрение сметы бюджетным отделом"""
        self.статус = 'одобрена'
        self.дата_рассмотрения = timezone.now()
        if комментарий:
            self.комментарий = комментарий
        self.save()
    
    def отклонить(self, пользователь, комментарий):
        """Отклонение сметы с комментарием"""
        self.статус = 'отклонена'
        self.дата_рассмотрения = timezone.now()
        if комментарий:
            self.комментарий = комментарий
        self.save()
    
    def требовать_доработки(self, пользователь, комментарий):
        """Отправить на доработку"""
        self.статус = 'требует_доработки'
        self.дата_рассмотрения = timezone.now()
        if комментарий:
            self.комментарий = комментарий
        self.save()


class СгенерированныйДокумент(models.Model):
    """Модель для хранения сгенерированных документов"""
    смета = models.ForeignKey(СметаЗатрат, on_delete=models.CASCADE, related_name='сгенерированные_документы')
    название = models.CharField(max_length=200, verbose_name='Название документа')
    содержание = models.TextField(verbose_name='Содержание')
    дата_создания = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Сгенерированный документ'
        verbose_name_plural = 'Сгенерированные документы'
        
class ДокументСметы(models.Model):
    """Модель для хранения сгенерированных документов сметы в БД"""
    ТИПЫ_ДОКУМЕНТОВ = [
        ('smeta', 'Смета с печатью'),
        ('zayavka', 'Письмо-заявка'),
    ]
    
    смета = models.ForeignKey(
        СметаЗатрат, 
        on_delete=models.CASCADE, 
        related_name='документы'
    )
    тип = models.CharField(max_length=20, choices=ТИПЫ_ДОКУМЕНТОВ, verbose_name='Тип документа')
    название = models.CharField(max_length=200, verbose_name='Название')
    pdf_data = models.BinaryField(verbose_name='PDF данные')  # Храним PDF прямо в БД
    дата_создания = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Документ сметы'
        verbose_name_plural = 'Документы сметы'
        ordering = ['-дата_создания']
    
    def __str__(self):
        return f"{self.get_тип_display()}: {self.название}"
    
class СметаФБП(models.Model):
    """Смета, которую составляет ФБП на основе выплаченных заявок"""
    СТАТУС_ВЫБОР = [
        ('черновик', 'Черновик'),
        ('утверждена', 'Утверждена'),
        ('отправлена', 'Отправлена'),
    ]
    
    год = models.IntegerField(verbose_name='Плановый год')
    дата_создания = models.DateTimeField(auto_now_add=True)
    дата_обновления = models.DateTimeField(auto_now=True)
    статус = models.CharField(max_length=20, choices=СТАТУС_ВЫБОР, default='черновик')
    создатель = models.ForeignKey(Пользователь, on_delete=models.SET_NULL, null=True)
    
    # На основе каких данных создана
    создана_на_основе_выплат_за_год = models.IntegerField(null=True, blank=True, verbose_name='Год выплат')
    
    общая_сумма = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Смета ФБП'
        verbose_name_plural = 'Сметы ФБП'
    
    def __str__(self):
        return f"Смета ФБП на {self.год} год"
    
    def рассчитать_общую_сумму(self):
        total = self.статьи.aggregate(total=models.Sum('сумма'))['total'] or 0
        self.общая_сумма = total
        self.save()
        return total


class СтатьяСметыФБП(models.Model):
    """Статья расходов в смете ФБП"""
    ТИПЫ_СТАТЕЙ = [
        ('zp', 'Заработная плата'),
        ('kommunalka', 'Коммунальные услуги'),
        ('remont', 'Ремонтные работы'),
        ('oborudovanie', 'Приобретение оборудования'),
        ('soft', 'Программное обеспечение'),
        ('transport', 'Транспортные расходы'),
        ('svyaz', 'Связь и интернет'),
        ('kanc', 'Канцелярские товары'),
        ('other', 'Прочее'),
    ]
    
    смета = models.ForeignKey(СметаФБП, on_delete=models.CASCADE, related_name='статьи')
    название = models.CharField(max_length=200)
    тип = models.CharField(max_length=20, choices=ТИПЫ_СТАТЕЙ, default='other')
    сумма = models.DecimalField(max_digits=15, decimal_places=2)
    описание = models.TextField(blank=True)
    
    # Для статей, созданных на основе выплат
    основано_на_выплатах = models.BooleanField(default=False)
    количество_выплат = models.IntegerField(default=0)
    исходная_организация = models.CharField(max_length=200, blank=True, verbose_name='Организация')
    
    class Meta:
        verbose_name = 'Статья сметы ФБП'
        verbose_name_plural = 'Статьи смет ФБП'
    
    def __str__(self):
        return f"{self.название} - {self.сумма} руб."


class ДокументСметыФБП(models.Model):
    """Документы для сметы ФБП"""
    ТИПЫ_ДОКУМЕНТОВ = [
        ('smeta', 'Смета расходов'),
        ('pismo', 'Письмо-заявка'),
    ]
    
    смета = models.ForeignKey(СметаФБП, on_delete=models.CASCADE, related_name='документы')
    тип = models.CharField(max_length=20, choices=ТИПЫ_ДОКУМЕНТОВ)
    название = models.CharField(max_length=200)
    pdf_data = models.BinaryField()  # ЭТО ПОЛЕ ДОЛЖНО БЫТЬ
    дата_создания = models.DateTimeField(auto_now_add=True)
    
class ОтчетПоЗаявкам(models.Model):
    """Отчет по заявкам организаций"""
    название = models.CharField(max_length=255, verbose_name="Название отчета")
    дата_создания = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    создатель = models.ForeignKey('Пользователь', on_delete=models.CASCADE, null=True, blank=True, related_name='отчеты_заявки')
    
    # Параметры фильтрации
    дата_начала = models.DateField(null=True, blank=True, verbose_name="Дата начала")
    дата_окончания = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    фильтр_статус = models.CharField(max_length=50, blank=True, null=True, verbose_name="Фильтр по статусу")
    фильтр_вид_выплаты = models.IntegerField(blank=True, null=True, verbose_name="Фильтр по виду выплаты")
    
    # Статистика
    количество_заявок = models.IntegerField(default=0, verbose_name="Количество заявок")
    общая_сумма = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Общая сумма")
    количество_новых = models.IntegerField(default=0, verbose_name="Новых")
    количество_принятых = models.IntegerField(default=0, verbose_name="Принятых")
    количество_отклоненных = models.IntegerField(default=0, verbose_name="Отклоненных")
    
    # Данные отчета в JSON
    данные = models.JSONField(default=dict, blank=True, verbose_name="Данные отчета")
    
    # Файл отчета
    файл = models.FileField(upload_to='reports/applications/', blank=True, null=True, verbose_name="Файл отчета")
    
    class Meta:
        verbose_name = "Отчет по заявкам"
        verbose_name_plural = "Отчеты по заявкам"
        ordering = ['-дата_создания']
    
    def __str__(self):
        return self.название