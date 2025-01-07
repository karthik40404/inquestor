from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'), 
    path('login/', views.log, name='log'),  
    path('logout/', views.lout, name='lout'),  
    path('contact/', views.contact_page, name='contact'),
    path('smessage',views.message),  
    path('reg', views.reg, name='reg'), 
    path('admdash', views.admdash),
    path('add-agent/', views.add_agent, name='add_agent'),
    path('add-case-category/', views.add_case_category, name='add_case_category'),
    path('add-case/', views.add_case, name='add_case'),
    path('cases/', views.list_cases, name='list_cases'),
    path('case/<int:case_id>/', views.case_details, name='case_details'),
    path('add-client/', views.add_client, name='add_client'),
    path('clients/', views.list_clients, name='list_clients'),
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/update-status/<int:case_id>/', views.update_case_status, name='update_case_status'),
    path('change-password/', views.change_password, name='change_password'),
    path('case/<int:case_id>/add-evidence/', views.add_evidence, name='add_evidence'),
    path('case-category/<int:category_id>/', views.cases_by_category, name='cases_by_category'),
    path('submit_case/<int:category_id>/', views.submit_case, name='submit_case'),
    path('user', views.user_home, name='user_home'),
    path('chat/<int:case_id>/', views.chat_view, name='chat_view'),
    path('send_message/<int:case_id>/', views.send_message, name='send_message'),
    path('agent/<int:agent_id>/', views.agent_profile, name='agent_profile'),
]
