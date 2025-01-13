from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'), 
    path('login/', views.log, name='log'),  
    path('logout/', views.lout, name='lout'),  
    path('contact/', views.contact_page, name='contact'),
    path('service/', views.service),
    path('smessage',views.message),  
    path('reg', views.reg, name='reg'), 
    path('admdash', views.admdash),
    path('add-agent/', views.add_agent, name='add_agent'),
    path('delete-agent/<int:agent_id>/', views.delete_agent, name='delete_agent'),
    path('add-case-category/', views.add_case_category, name='add_case_category'),
    path('cases/', views.list_cases, name='list_cases'),
    path('clients/', views.list_clients, name='list_clients'),
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/update-status/<int:case_id>/', views.update_case_status, name='update_case_status'),
    path('change-password/', views.change_password, name='change_password'),
    path('case-category/<int:category_id>/', views.cases_by_category, name='cases_by_category'),
    path('submit_case/<int:category_id>/', views.submit_case, name='submit_case'),
    path('user', views.user_home, name='user_home'),
    path('agent/<int:agent_id>/case/', views.agent_profile, name='agent_profile'),  
    path('case-details/<int:case_id>/', views.agent_case_details, name='agent_case_details'),
]
