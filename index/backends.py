from django.contrib.auth.backends import BaseBackend
from .models import Организация

class OrganizationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"DEBUG: Trying to authenticate organization: {username}")  # Для отладки
        try:
            org = Организация.objects.get(Логин=username)
            print(f"DEBUG: Organization found: {org.ПолноеНаименование}")  # Для отладки
            if org.check_password(password):
                print("DEBUG: Password correct")  # Для отладки
                return org
            else:
                print("DEBUG: Password incorrect")  # Для отладки
        except Организация.DoesNotExist:
            print("DEBUG: Organization not found")  # Для отладки
            return None
        return None

    def get_user(self, user_id):
        try:
            return Организация.objects.get(pk=user_id)
        except Организация.DoesNotExist:
            return None