from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.log, name='log'), 
    path('lout/', views.logout),
    path('admdash', views.admdash),
    path('admin/add-agent/', views.add_agent, name='add_agent'),
    path('admin/add-case-category/', views.add_case_category, name='add_case_category'),
    path('admin/add-case/', views.add_case, name='add_case'),
    path('admin/cases/', views.list_cases, name='list_cases'),
    path('admin/case/<int:case_id>/', views.case_details, name='case_details'),
    path('admin/add-client/', views.add_client, name='add_client'),
    path('admin/clients/', views.list_clients, name='list_clients'),
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/update-status/<int:case_id>/', views.update_case_status, name='update_case_status'),
    path('case/<int:case_id>/add-evidence/', views.add_evidence, name='add_evidence'),
    path('clientdash/', views.client_dashboard, name='client_dashboard'),
]
