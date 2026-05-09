from django.contrib import admin
from .models import Отдел, Организация, Заявка, Пользователь, ТипыДокументов, ВидыВыплат, Выплаты, ОжидаемаяСуммаВыплат, ОтчетПланировщика

admin.site.register(Отдел)
admin.site.register(Организация)
admin.site.register(Пользователь)
admin.site.register(ТипыДокументов)
admin.site.register(ВидыВыплат)
admin.site.register(Выплаты)
admin.site.register(Заявка)
admin.site.register(ОжидаемаяСуммаВыплат)
admin.site.register(ОтчетПланировщика)