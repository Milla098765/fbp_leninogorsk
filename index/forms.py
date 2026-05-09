from django import forms
from datetime import datetime 
from django.utils import timezone
from .models import Пользователь, Отдел, Организация, ВидыВыплат, Заявка, ОжидаемаяСуммаВыплат, ОтчетВыплат, ОтчетПланировщика, СметаПроект, СметаЗатрат, ДокументЗаявки, СтатьяСметыФБП, СметаФБП, ДокументСметыФБП
class SimpleLoginForm(forms.Form):
    username = forms.CharField(label='Логин', max_length=50)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class OrganizationLoginForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class ОрганизацияФорма(forms.ModelForm):
    Пароль = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Организация
        fields = ['ПолноеНаименование', 'ИНН', 'СчетОрганизации', 'Логин', 'Пароль']

    def save(self, commit=True):
        org = super().save(commit=False)
        raw_password = self.cleaned_data.get('Пароль')
        if raw_password:
            org.set_password(raw_password)
        if commit:
            org.save()
        return org

class ПользовательФорма(forms.ModelForm):
    Пароль = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Пользователь
        fields = ['Имя', 'Фамилия', 'Отчество', 'Роль', 'Логин',
                  'Пароль', 'Телефон', 'Отдел', 'Фото']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Отдел'].queryset = Отдел.objects.all()
        self.fields['Отдел'].empty_label = 'Выберите отдел'
        self.fields['Пароль'].initial = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        pw = self.cleaned_data.get('Пароль')
        if pw:
            user.Пароль = pw  # в будущем — добавить хеширование
        if commit:
            user.save()
        return user

class ОтделФорма(forms.ModelForm):
    class Meta:
        model = Отдел
        fields = ['Название']

class ЗаявкаФорма(forms.ModelForm):
    использовать_другой_вид = forms.BooleanField(
        required=False, 
        label='Указать другой вид выплаты',
        widget=forms.CheckboxInput(attrs={'id': 'use_other_type'})
    )
    
    
    class Meta:
        model = Заявка
        fields = ['вид_выплаты', 'другой_вид_выплаты', 'запрашиваемая_сумма']
        widgets = {
            'запрашиваемая_сумма': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
        }
        labels = {
            'вид_выплаты': 'Вид выплаты',
            'другой_вид_выплаты': 'Другой вид выплаты',
            'запрашиваемая_сумма': 'Запрашиваемая сумма (руб.)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['вид_выплаты'].queryset = ВидыВыплат.objects.all()
        self.fields['вид_выплаты'].empty_label = 'Выберите вид выплаты'
        self.fields['другой_вид_выплаты'].required = False
        # Убираем атрибут multiple, так как он не поддерживается

    def clean(self):
        cleaned_data = super().clean()
        использовать_другой_вид = cleaned_data.get('использовать_другой_вид')
        вид_выплаты = cleaned_data.get('вид_выплаты')
        другой_вид_выплаты = cleaned_data.get('другой_вид_выплаты')
        
        if использовать_другой_вид and not другой_вид_выплаты:
            raise forms.ValidationError('Пожалуйста, укажите вид выплаты')
        elif not использовать_другой_вид and not вид_выплаты:
            raise forms.ValidationError('Пожалуйста, выберите вид выплаты')
        
        return cleaned_data
    
class ОжидаемаяСуммаФорма(forms.ModelForm):
    class Meta:
        model = ОжидаемаяСуммаВыплат
        fields = ['год', 'ожидаемая_сумма_год']  # Оба поля должны быть здесь
        widgets = {
            'год': forms.NumberInput(attrs={
                'min': 2020, 
                'max': 2030,
                'class': 'form-input'
            }),
            'ожидаемая_сумма_год': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'form-input'
            }),
        }
        labels = {
            'год': 'Год',
            'ожидаемая_сумма_год': 'Ожидаемая сумма выплат за год (руб.)',
        }
        
class ОтчетФорма(forms.ModelForm):
    организации = forms.ModelMultipleChoiceField(
        queryset=Организация.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-input', 'style': 'height: 150px;'}),
        required=False,
        label='Организации (оставьте пустым для всех)'
    )
    
    class Meta:
        model = ОтчетВыплат
        fields = ['название', 'дата_начала', 'дата_окончания', 'организации']
        widgets = {
            'название': forms.TextInput(attrs={'class': 'form-input'}),
            'дата_начала': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'дата_окончания': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }
        labels = {
            'название': 'Название отчета',
            'дата_начала': 'Дата начала периода',
            'дата_окончания': 'Дата окончания периода',
        }
        
class ОтклонениеЗаявкиФорма(forms.Form):
    комментарий = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Укажите причину отклонения заявки...',
            'rows': 4,
            'style': 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;'
        }),
        label='Причина отклонения',
        required=True
    )
    
class ОтчетПланировщикаФорма(forms.ModelForm):
    class Meta:
        model = ОтчетПланировщика
        fields = ['название', 'дата_начала', 'дата_окончания']
        widgets = {
            'дата_начала': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'дата_окончания': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'название': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Например: Анализ выплат за январь 2024'
            }),
        }
        labels = {
            'название': 'Название отчета планировщика',
            'дата_начала': 'Начало анализируемого периода',
            'дата_окончания': 'Окончание анализируемого периода',
        }
        
# Добавьте в конец файла forms.py

class СметаПроектФорма(forms.ModelForm):
    class Meta:
        model = СметаПроект
        fields = ['название', 'описание', 'запрашиваемая_сумма']
        widgets = {
            'название': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Ремонт дороги по ул. Ленина'}),
            'описание': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Краткое описание проекта'}),
            'запрашиваемая_сумма': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'название': 'Название проекта',
            'описание': 'Описание',
            'запрашиваемая_сумма': 'Запрашиваемая сумма (руб.)',
        }


class СметаЗатратФорма(forms.ModelForm):
    """Форма для создания сметы затрат администрацией"""
    class Meta:
        model = СметаЗатрат
        fields = ['название', 'год', 'комментарий']  # УДАЛИЛИ 'документ'
        widgets = {
            'название': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Смета на 2025 год'}),
            'год': forms.NumberInput(attrs={'class': 'form-input', 'min': 2024, 'max': 2035}),
            'комментарий': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Дополнительная информация...'}),
        }
        labels = {
            'название': 'Название сметы',
            'год': 'Плановый год',
            'комментарий': 'Комментарий',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['год'].initial = timezone.now().year + 1

class СметаРассмотрениеФорма(forms.Form):
    """Форма для рассмотрения сметы бюджетным отделом"""
    комментарий = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 4,
            'placeholder': 'Введите комментарий...'
        }),
        label='Комментарий',
        required=False
    )
    
    ДЕЙСТВИЯ = [
        ('approve', '✅ Одобрить смету'),
        ('reject', '❌ Отклонить смету'),
        ('rework', '🔄 Отправить на доработку'),
    ]
    
    действие = forms.ChoiceField(
        choices=ДЕЙСТВИЯ,
        widget=forms.RadioSelect,
        label='Действие'
    )


class СоздатьЗаявкиИзСметыФорма(forms.Form):
    """Форма для создания заявок из одобренной сметы"""
    проекты = forms.ModelMultipleChoiceField(
        queryset=None,  # Будет установлено в представлении
        widget=forms.CheckboxSelectMultiple,
        label='Выберите проекты для создания заявок'
    )
    
    def __init__(self, *args, **kwargs):
        смета = kwargs.pop('смета', None)
        super().__init__(*args, **kwargs)
        if смета:
            self.fields['проекты'].queryset = смета.проекты.all()
            
class ГенерацияДокументаФорма(forms.Form):
    """Форма для генерации документа из шаблона"""
    
    # Основные поля для заполнения
    номер_соглашения = forms.CharField(
        label='Номер соглашения о сотрудничестве',
        max_length=50,
        initial='45-С/2025',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    
    дата_соглашения = forms.DateField(
        label='Дата соглашения',
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    
    наименование_учреждения = forms.CharField(
        label='Получатель (учреждение)',
        initial='Муниципальное казённое учреждение «Финансово-бюджетная палата»',
        widget=forms.TextInput(attrs={'class': 'form-input', 'size': 50})
    )
    
    # Выбор проектов из сметы
    проекты = forms.ModelMultipleChoiceField(
        queryset=None,  # Будет установлено в представлении
        widget=forms.CheckboxSelectMultiple,
        label='Выберите проекты для включения в документ',
        required=True
    )
    
    # Дополнительная информация
    дополнительный_текст = forms.CharField(
        label='Дополнительная информация',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3})
    )
    
    def __init__(self, *args, **kwargs):
        смета = kwargs.pop('смета', None)
        super().__init__(*args, **kwargs)
        if смета:
            self.fields['проекты'].queryset = смета.проекты.all()
            
class СметаДанныеФорма(forms.Form):
    """Форма для ввода данных перед созданием документов"""
    
    # Данные получателя
    глава_получатель = forms.CharField(
        label='ФИО Главы района',
        initial='Иванов И.И.',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    должность_получателя = forms.CharField(
        label='Должность получателя',
        initial='Главе Лениногорского муниципального района',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Данные отправителя
    должность_отправителя = forms.CharField(
        label='Должность отправителя',
        initial='Главы администрации города Лениногорск',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    фио_отправителя = forms.CharField(
        label='ФИО отправителя',
        initial='Петров П.П.',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Данные соглашения
    номер_соглашения = forms.CharField(
        label='Номер соглашения о сотрудничестве',
        initial='45-С/2025',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    дата_соглашения = forms.DateField(
        label='Дата соглашения',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    основание = forms.CharField(
        label='Текст основания',
        initial='в соответствии с Соглашением о сотрудничестве',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Получатель средств (ФБП)
    учреждение = forms.CharField(
        label='Получатель средств',
        initial='Муниципальному казённому учреждению «Финансово-бюджетная палата»',
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control', 'size': 50})
    )
    
    # Выбор проектов
    проекты = forms.ModelMultipleChoiceField(
        queryset=None,  # Будет установлено в __init__
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'projects-checkbox'}),
        label='Выберите проекты для включения в письмо',
        required=True
    )
    
    # Дополнительно
    дополнительный_текст = forms.CharField(
        label='Дополнительный текст',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    # Исполнитель
    исполнитель = forms.CharField(
        label='ФИО исполнителя',
        initial='Сидорова А.А.',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    телефон = forms.CharField(
        label='Телефон',
        initial='8 (85595) 5-00-00',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        smeta = kwargs.pop('smeta', None)
        super().__init__(*args, **kwargs)
        if smeta:
            self.fields['проекты'].queryset = smeta.проекты.all()
            # Устанавливаем начальное значение - все проекты выбраны
            self.fields['проекты'].initial = smeta.проекты.all()
        self.fields['дата_соглашения'].initial = datetime.now().date
        
class ДокументЗаявкиФорма(forms.ModelForm):
    """Форма для загрузки документов к заявке"""
    class Meta:
        model = ДокументЗаявки
        fields = ['тип', 'название', 'файл', 'описание']
        widgets = {
            'тип': forms.Select(attrs={'class': 'form-control'}),
            'название': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Трудовой договор Иванова И.И.'}),
            'файл': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.png'}),
            'описание': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Краткое описание документа'}),
        }
        labels = {
            'тип': 'Тип документа',
            'название': 'Название',
            'файл': 'Файл',
            'описание': 'Описание',
        }
        
class СметаБюджетаФорма(forms.ModelForm):
    """Форма для создания сметы бюджета"""
    год = forms.IntegerField(
        min_value=2026,
        initial=timezone.now().year,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = СметаФБП
        fields = ['год']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['год'].widget.attrs['min'] = 2026
    
    def clean_год(self):
        год = self.cleaned_data['год']
        if год < 2026:
            raise forms.ValidationError('Год должен быть не ранее 2026')
        return год


class СтатьяСметыФорма(forms.ModelForm):
    """Форма для добавления статьи в смету"""
    class Meta:
        model = СтатьяСметыФБП
        fields = ['тип', 'название', 'сумма', 'описание']
        widgets = {
            'тип': forms.Select(attrs={'class': 'form-control'}),
            'название': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Зарплата учителей'}),
            'сумма': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'описание': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Подробное описание...'}),
        }
        labels = {
            'тип': 'Тип расходов',
            'название': 'Название статьи',
            'сумма': 'Сумма (руб.)',
            'описание': 'Описание',
        }


class ВыборГодаДляСметыФорма(forms.Form):
    """Форма для выбора года на основе выплат"""
    год = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        годы = kwargs.pop('годы', [])
        super().__init__(*args, **kwargs)
        self.fields['год'].choices = [(г, f'{г} год') for г in годы]


class ВыборСметыАдминистрацииФорма(forms.Form):
    """Форма для выбора сметы от администрации"""
    смета = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        сметы = kwargs.pop('сметы', None)
        super().__init__(*args, **kwargs)
        if сметы:
            self.fields['смета'].queryset = сметы