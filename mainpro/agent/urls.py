from django.urls import path
from . import views

urlpatterns = [
    path('', views.log, name='log'), 
    path('reg', views.reg, name='reg'), 
    path('lout/', views.lout),
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
    path('case/<int:case_id>/add-evidence/', views.add_evidence, name='add_evidence'),
    path('clientdash/', views.client_dashboard, name='client_dashboard'),
]
