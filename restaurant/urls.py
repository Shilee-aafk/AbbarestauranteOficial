from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('receptionist-dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('cook-dashboard/', views.cook_dashboard, name='cook_dashboard'),
    path('waiter-dashboard/', views.waiter_dashboard, name='waiter_dashboard'),
    path('save_order/', views.save_order, name='save_order'),
    path('add_menu_item/', views.add_menu_item, name='add_menu_item'),
    path('edit_menu_item/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('delete_menu_item/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('add_table/', views.add_table, name='add_table'),
    path('edit_table/<int:table_id>/', views.edit_table, name='edit_table'),
    path('delete_table/<int:table_id>/', views.delete_table, name='delete_table'),
    path('update_order_status_json/<int:order_id>/', views.update_order_status_json, name='update_order_status_json'),
    path('add_reservation/', views.add_reservation, name='add_reservation'),
    path('add_order/', views.add_order, name='add_order'),
    path('edit_order/<int:id>/', views.edit_order, name='edit_order'),
    path('delete_order/<int:id>/', views.delete_order, name='delete_order'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
