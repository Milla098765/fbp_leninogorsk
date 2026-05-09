from django.urls import path
from . import views

urlpatterns = [
    # Главная страница выбора
    path('', views.welcome_page, name='welcome'),
    
    # Пути для сотрудников и администраторов
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('budget/', views.budget_page, name='budget_page'),

    # Пути для кастомных пользователей
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/application/<int:pk>/', views.user_application_detail, name='user_application_detail'),
    path('user/add/', views.user_create, name='user_add'),
    path('user/<int:pk>/edit/', views.user_update, name='user_edit'),
    path('user/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('user/application/<int:pk>/approve/', views.user_application_approve, name='user_application_approve'),
    path('user/application/<int:pk>/reject/', views.user_application_reject, name='user_application_reject'),

    # Пути для отделов
    path('отделы/', views.отделы_list, name='отделы_list'),
    path('отделы/add/', views.отдел_create, name='отдел_create'),
    path('отделы/<int:pk>/edit/', views.отдел_update, name='отдел_update'),
    path('отделы/<int:pk>/delete/', views.отдел_delete, name='отдел_delete'),

    # Пути для организаций
    path('организации/', views.организации_list, name='организации_list'),
    path('организации/add/', views.организация_create, name='организация_create'),
    path('организации/<int:pk>/edit/', views.организация_update, name='организация_update'),
    path('организации/<int:pk>/delete/', views.организация_delete, name='организация_delete'),

    # Пути для входа организаций
    path('organization/login/', views.organization_login_view, name='organization_login'),
    path('organization/dashboard/', views.organization_dashboard, name='organization_dashboard'),
    path('organization/logout/', views.organization_logout, name='organization_logout'),
    path('organization/application/create/', views.application_create, name='application_create'),
    path('organization/applications/', views.organization_applications, name='organization_applications'),

    # Пути для бюджетного отдела
    path('budget/applications/', views.budget_applications, name='budget_applications'),
    path('budget/application/<int:pk>/', views.application_detail, name='application_detail'),
    path('budget/application/<int:pk>/approve/', views.budget_application_approve, name='budget_application_approve'),
    path('budget/application/<int:pk>/reject/', views.budget_application_reject, name='budget_application_reject'),

    # Пути для выплат
    path('выплаты/', views.выплаты_list, name='выплаты_list'),
    path('выплаты/<int:pk>/update-status/', views.выплата_update_status, name='выплата_update_status'),
    
    # Пути для документов выплат
    path('выплаты/<int:pk>/download-document/', views.download_payment_document, name='download_payment_document'),
    path('organization/application/<int:pk>/download-document/', views.download_organization_payment_document, name='download_organization_payment_document'),
    
    # Пути для ожидаемых сумм
    path('ожидаемые-суммы/', views.ожидаемые_суммы_list, name='ожидаемые_суммы_list'),
    path('ожидаемые-суммы/add/', views.ожидаемая_сумма_create, name='ожидаемая_сумма_create'),
    path('ожидаемые-суммы/<int:pk>/edit/', views.ожидаемая_сумма_update, name='ожидаемая_сумма_update'),
    path('ожидаемые-суммы/<int:pk>/delete/', views.ожидаемая_сумма_delete, name='ожидаемая_сумма_delete'),
    
    # Пути для отчетов (обычные отчеты для бюджетного отдела)
    path('отчеты/', views.отчеты_list, name='отчеты_list'),
    path('отчеты/create/', views.отчет_create_from_payments, name='отчет_create_from_payments'),
    path('отчеты/<int:pk>/', views.отчет_детали, name='отчет_детали'),
    path('отчеты/<int:pk>/download/', views.отчет_download, name='отчет_download'),
    path('отчеты/<int:pk>/chart/', views.отчет_chart, name='отчет_chart'),

    # ==================== ПУТИ ДЛЯ СПЕЦИАЛИСТА ПО ПЛАНИРОВАНИЮ ====================
    path('planning/dashboard/', views.planning_dashboard, name='planning_dashboard'),
    path('planning/payments/', views.planning_payments, name='planning_payments'),
    
    # ОТЧЕТЫ ПЛАНИРОВЩИКА
    path('planning/reports/', views.planning_reports_list, name='planning_reports_list'),
    path('planning/reports/create/', views.planning_create_report, name='planning_create_report'),
    path('planning/reports/<int:pk>/', views.planning_report_detail, name='planning_report_detail'),
    path('planning/reports/<int:pk>/download/', views.download_planning_report, name='download_planning_report'),

    # ==================== СМЕТЫ ЗАТРАТ ОТ АДМИНИСТРАЦИИ ====================
    # Для администрации (организация)
    path('organization/smeti/', views.organization_smeti_list, name='organization_smeti_list'),
    path('organization/smeta/create/', views.organization_smeta_create, name='organization_smeta_create'),
    path('organization/smeta/<int:pk>/', views.organization_smeta_detail, name='organization_smeta_detail'),
    path('organization/smeta/<int:pk>/send/', views.organization_smeta_send, name='organization_smeta_send'),
    path('organization/smeta/<int:pk>/delete/', views.organization_smeta_delete, name='organization_smeta_delete'),
    
    path('budget/smeta/<int:pk>/', views.budget_smeta_detail, name='budget_smeta_detail'),
    path('budget/smeta/<int:pk>/review/', views.budget_smeta_review, name='budget_smeta_review'),
    path('budget/smeta/<int:pk>/create-applications/', views.budget_create_applications_from_smeta, name='budget_create_applications_from_smeta'),
    
    # Общий просмотр для администрации и бюджетного отдела
    path('smeti/<int:pk>/download/', views.smeta_download_document, name='smeta_download_document'),
    
    path('organization/smeta/<int:pk>/create-document/', views.смета_создать_документ, name='smeta_create_document'),
    path('organization/smeta/<int:pk>/edit-projects/', views.organization_smeta_edit_projects, name='organization_smeta_edit_projects'),
    
    # Для бюджетного отдела - отдельная страница для смет
    path('budget/smeti/', views.budget_smeti_list, name='budget_smeti_list'),
    path('smeta/<int:pk>/download-pdf/', views.download_smeta_pdf, name='download_smeta_pdf'),
    path('smeta/<int:pk>/create-zayavka/', views.create_zayavka_pdf, name='create_zayavka'),
    
    # Пути для детального просмотра заявки организацией
    path('organization/application/<int:pk>/', views.organization_application_detail, name='organization_application_detail'),

    # ==================== ПУТИ ДЛЯ ДОКУМЕНТОВ ЗАЯВОК (ИСПРАВЛЕНО) ====================
    path('application/<int:pk>/upload-document/', views.заявка_загрузить_документ, name='upload_application_document'),
    path('application-document/<int:pk>/delete/', views.заявка_удалить_документ, name='delete_application_document'),
    path('application-document/<int:pk>/download/', views.скачать_документ_заявки, name='download_application_document'),  # ← ИЗМЕНЕНО!
    
    # Пути для деталей заявки
    path('application/<int:pk>/', views.organization_application_detail, name='organization_application_detail'),
    
    # ==================== СМЕТЫ ФБП ====================
    path('budget/fbp-smeti/', views.бюджет_сметы_fbp_list, name='budget_smeti_fbp'),
    path('budget/fbp-smeta/from-payments/', views.бюджет_смета_на_основе_выплат, name='budget_smeta_fbp_from_payments'),
    path('budget/fbp-smeta/<int:pk>/', views.бюджет_смета_fbp_детали, name='budget_smeta_fbp_detail'),
    path('budget/fbp-smeta/<int:pk>/create-docs/', views.бюджет_смета_fbp_создать_документы, name='budget_smeta_fbp_create_docs'),
    path('budget/fbp-smeta/from-admin/', views.бюджет_смета_fbp_из_администрации, name='budget_smeta_fbp_from_admin'),
    path('budget/fbp-smeta/<int:pk>/add-admin/', views.бюджет_смета_fbp_добавить_администрацию, name='budget_smeta_fbp_add_admin'),
    path('budget/fbp-smeta/<int:pk>/delete/', views.budget_smeta_fbp_delete, name='budget_smeta_fbp_delete'),
    path('budget/fbp-statya/<int:pk>/delete/', views.бюджет_смета_fbp_удалить_статью, name='budget_smeta_fbp_delete_statya'),
    path('budget/fbp-document/<int:pk>/download/', views.download_fbp_document, name='download_fbp_document'),
    
    # ==================== ДОКУМЕНТЫ СМЕТЫ АДМИНИСТРАЦИИ ====================
    path('document/<int:pk>/download/', views.скачать_документ, name='download_document'),
    # Отчеты по заявкам
    path('create-application-report/', views.create_application_report, name='create_application_report'),
    path('application-reports/', views.application_reports_list, name='application_reports_list'),
    path('application-report/download/<int:pk>/', views.download_application_report, name='download_application_report'),
    path('application-report/delete/<int:pk>/', views.delete_application_report, name='delete_application_report'),
]