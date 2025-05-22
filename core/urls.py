from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordChangeDoneView
from .views import CustomPasswordChangeView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.owner_login, name='login'),
    path('register/', views.owner_register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-room/', views.add_room, name='add_room'),
    path('edit-room/<int:room_id>/', views.edit_room, name='edit_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('tenant-register/', views.tenant_register, name='add_tenant'),
    path('tenant/<int:tenant_id>/', views.tenant_detail, name='tenant_detail'),
    path('tenant/<int:tenant_id>/edit/', views.tenant_edit, name='tenant_edit'),
    path('tenant/<int:tenant_id>/delete/', views.delete_tenant, name='delete_tenant'),
    path('tenant/<int:tenant_id>/payment/', views.add_payment, name='add_payment'),
    path('tenant/<int:tenant_id>/payment-history/', views.payment_history, name='payment_history'),
    path('tenant/<int:tenant_id>/pdf/', views.tenant_pdf_view, name='tenant_pdf'),
    path('owner/edit-profile/', views.edit_profile, name='edit_profile'),
    path('tenant/<int:tenant_id>/edit-image/', views.edit_tenant_image, name='edit_tenant_image'),
    path('rooms/', views.room_list, name='room_list'),
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('change-password/done/', PasswordChangeDoneView.as_view(template_name='core/password_change_done.html'), name='password_change_done'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
