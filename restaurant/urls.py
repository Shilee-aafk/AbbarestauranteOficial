from django.urls import path
from . import views
from restaurant import views as restaurant_views

app_name = 'restaurant'

urlpatterns = [
    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('', views.home, name='home'),
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('receptionist-dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('cook-dashboard/', views.cook_dashboard, name='cook_dashboard'),
    path('waiter-dashboard/', views.waiter_dashboard, name='waiter_dashboard'),
    path('menu/', restaurant_views.public_menu_view, name='public_menu'),
    path('logout/', views.logout_view, name='logout'),
    path('save_order/', views.save_order, name='save_order'),
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
    path('api/menu-items/<int:pk>/upload-image/', views.api_menu_item_upload_image, name='api_menu_item_upload_image'),
    path('api/menu-items/<int:pk>/delete-image/', views.api_menu_item_delete_image, name='api_menu_item_delete_image'),
    path('api/waiter/orders/<int:pk>/', views.api_waiter_order_detail, name='api_waiter_order_detail'),
    path('api/orders-report/', views.api_orders_report, name='api_orders_report'),
    path('api/orders/<int:pk>/payment/', views.api_process_payment, name='api_process_payment'),
    path('api/payment-methods-report/', views.api_payment_methods_report, name='api_payment_methods_report'),
    # La ruta general para listar/crear va PRIMERO, la específica para un recurso DESPUÉS.
    path('api/pins/', views.api_registration_pins, name='api_registration_pins'),
    path('api/pins/<int:pk>/', views.api_registration_pins, name='api_registration_pin_detail'),
    
    # Categorías API
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/categories/check/', views.api_categories_check, name='api_categories_check'),

    path('export/orders-excel/', views.export_orders_excel, name='export_orders_excel'),
    path('api/dashboard-charts/', views.api_dashboard_charts, name='api_dashboard_charts'),
    path('api/admin-dashboard-stats/', views.api_admin_dashboard_stats, name='api_admin_dashboard_stats'),
    
    # RoomBill APIs
    path('api/roombills/unpaid-orders/', views.api_get_unpaid_orders_by_room, name='api_get_unpaid_orders_by_room'),
    path('api/roombills/create/', views.api_create_roombill, name='api_create_roombill'),
    path('api/roombills/', views.api_get_roombills, name='api_get_roombills'),
    path('api/roombills/<int:bill_id>/', views.api_roombill_detail, name='api_roombill_detail'),
    
    path('export/roombills-excel/', views.export_roombills_excel, name='export_roombills_excel'),
]
