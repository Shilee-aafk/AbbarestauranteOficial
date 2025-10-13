from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('receptionist-dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('cook-dashboard/', views.cook_dashboard, name='cook_dashboard'),
    path('waiter-dashboard/', views.waiter_dashboard, name='waiter_dashboard'),

    # Old form-based views (can be removed if fully migrated to API)
    path('save_order/', views.save_order, name='save_order'),
     path('add_table/', views.add_table, name='add_table'),
    path('edit_table/<int:table_id>/', views.edit_table, name='edit_table'),
    path('delete_table/<int:table_id>/', views.delete_table, name='delete_table'),
    path('update_order_status_json/<int:order_id>/', views.update_order_status_json, name='update_order_status_json'),
    path('add_reservation/', views.add_reservation, name='add_reservation'),
    path('add_order/', views.add_order, name='add_order'),
    path('edit_order/<int:id>/', views.edit_order, name='edit_order'),
    path('delete_order/<int:id>/', views.delete_order, name='delete_order'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('ws/productos/', views.crear_producto, name='crear_producto'),

    # --- API URLs for Admin Dashboard ---
    path('api/orders/', views.api_orders, name='api_orders'),
    path('api/orders/<int:pk>/', views.api_order_detail, name='api_order_detail'),
    path('api/kitchen-orders/', views.api_kitchen_orders, name='api_kitchen_orders'),
    path('api/orders/<int:pk>/status/', views.api_order_status, name='api_order_status'),
    path('api/tables/', views.api_tables, name='api_tables'),
    path('api/tables/<int:pk>/', views.api_table_detail, name='api_table_detail'),
    path('api/menu-items/', views.api_menu_items, name='api_menu_items'),
    path('api/menu-items/<int:pk>/', views.api_menu_item_detail, name='api_menu_item_detail'),
    path('api/waiter/orders/<int:pk>/', views.api_waiter_order_detail, name='api_waiter_order_detail'),
]
