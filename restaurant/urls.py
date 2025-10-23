from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('signup/', views.signup_view, name='signup'),

    path('', views.home, name='home'),
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('receptionist-dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('cook-dashboard/', views.cook_dashboard, name='cook_dashboard'),
    path('waiter-dashboard/', views.waiter_dashboard, name='waiter_dashboard'),

    path('save_order/', views.save_order, name='save_order'),
    path('add_reservation/', views.add_reservation, name='add_reservation'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('api/users/', views.api_users, name='api_users'),
    path('api/users/<int:pk>/', views.api_users, name='api_user_detail'),
    # --- API URLs for Admin Dashboard ---
    path('api/orders/', views.api_orders, name='api_orders'),
    path('api/orders/<int:pk>/', views.api_order_detail, name='api_order_detail'),
    path('api/kitchen-orders/', views.api_kitchen_orders, name='api_kitchen_orders'),
    path('api/orders/<int:pk>/status/', views.api_order_status, name='api_order_status'),
    path('api/menu-items/', views.api_menu_items, name='api_menu_items'),
    path('api/menu-items/<int:pk>/', views.api_menu_item_detail, name='api_menu_item_detail'),
    path('api/waiter/orders/<int:pk>/', views.api_waiter_order_detail, name='api_waiter_order_detail'),
    path('api/orders-report/', views.api_orders_report, name='api_orders_report'),
    # La ruta general para listar/crear va PRIMERO, la específica para un recurso DESPUÉS.
    path('api/pins/', views.api_registration_pins, name='api_registration_pins'),
    path('api/pins/<int:pk>/', views.api_registration_pins, name='api_registration_pin_detail'),

    path('export/orders-excel/', views.export_orders_excel, name='export_orders_excel'),
    path('api/dashboard-charts/', views.api_dashboard_charts, name='api_dashboard_charts'),
]
