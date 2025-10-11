from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Reservation, Order, OrderItem, MenuItem, Table

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
            return redirect('admin_dashboard')
        elif request.user.groups.filter(name='Recepcionista').exists():
            return redirect('receptionist_dashboard')
        elif request.user.groups.filter(name='Cocinero').exists():
            return redirect('cook_dashboard')
        elif request.user.groups.filter(name='Garzón').exists():
            return redirect('waiter_dashboard')
        else:
            # No role assigned, render home
            return render(request, 'restaurant/home.html', {})
    else:
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def admin_dashboard(request):
    import json
    from django.utils import timezone
    reservations = Reservation.objects.all()
    orders = Order.objects.all()
    menu_items = MenuItem.objects.all()
    tables = Table.objects.all()
    total_orders_today = Order.objects.filter(created_at__date=timezone.now().date()).count()
    preparing_count = Order.objects.filter(status='preparing').count()
    ready_count = Order.objects.filter(status='ready').count()
    completed_count = Order.objects.filter(status='served').count()
    recent_orders = Order.objects.order_by('-created_at')[:10]
    for order in recent_orders:
        order.total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all())
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    # JSON data for JavaScript
    orders_json = json.dumps([{
        'id': o.id,
        'table': o.table.number,
        'status': o.status,
        'user': o.user.username,
        'created_at': o.created_at.isoformat(),
        'total': float(sum(item.menu_item.price * item.quantity for item in o.orderitem_set.all()))
    } for o in orders])
    tables_json = json.dumps([{
        'id': t.id,
        'number': t.number
    } for t in tables])
    menu_items_json = json.dumps([{
        'id': m.id,
        'name': m.name,
        'price': float(m.price),
        'category': m.category,
        'available': m.available
    } for m in menu_items])
    return render(request, 'restaurant/admin_dashboard.html', {
        'reservations': reservations,
        'orders': orders,
        'menu_items': menu_items,
        'tables': tables,
        'total_orders_today': total_orders_today,
        'preparing_count': preparing_count,
        'ready_count': ready_count,
        'completed_count': completed_count,
        'recent_orders': recent_orders,
        'user_role': user_role,
        'kitchen_orders': Order.objects.filter(status__in=['pending', 'preparing']),
        'orders_json': orders_json,
        'tables_json': tables_json,
        'menu_items_json': menu_items_json,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Recepcionista').exists())
def receptionist_dashboard(request):
    from django.utils import timezone
    reservations = Reservation.objects.all()
    tables = Table.objects.all()
    total_orders_today = Order.objects.filter(created_at__date=timezone.now().date()).count()
    preparing_count = Order.objects.filter(status='preparing').count()
    ready_count = Order.objects.filter(status='ready').count()
    completed_count = Order.objects.filter(status='served').count()
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    return render(request, 'restaurant/receptionist_dashboard.html', {
        'reservations': reservations,
        'tables': tables,
        'total_orders_today': total_orders_today,
        'preparing_count': preparing_count,
        'ready_count': ready_count,
        'completed_count': completed_count,
        'user_role': user_role,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Cocinero').exists())
def cook_dashboard(request):
    from django.utils import timezone
    orders = Order.objects.filter(status__in=['pending', 'preparing'])
    preparing_count = Order.objects.filter(status='preparing').count()
    ready_count = Order.objects.filter(status='ready').count()
    for order in orders:
        order.total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all())
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    return render(request, 'restaurant/cook_dashboard.html', {
        'orders': orders,
        'preparing_count': preparing_count,
        'ready_count': ready_count,
        'user_role': user_role,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Garzón').exists())
def waiter_dashboard(request):
    import json
    from django.utils import timezone
    from django.db.models import Q
    # Tables and menu items should be managed through the admin panel
    tables = Table.objects.all()
    menu_items = MenuItem.objects.filter(available=True)
    categories = menu_items.values_list('category', flat=True).distinct()
    orders = Order.objects.filter(~Q(status='served'))  # Active orders
    for table in tables:
        table.is_available = not orders.filter(table=table).exists()
        table.current_order = orders.filter(table=table).first() if not table.is_available else None
    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    menu_items_json = json.dumps([{'id': item.id, 'name': item.name, 'price': float(item.price)} for item in menu_items])
    return render(request, 'restaurant/waiter_dashboard.html', {
        'tables': tables,
        'menu_items': menu_items,
        'categories': categories,
        'menu_items_json': menu_items_json,
        'user_role': user_role,
    })

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Garzón').exists())
def save_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_id = data.get('table_id')
        items = data.get('items', [])

        table = Table.objects.get(id=table_id)
        order = Order.objects.create(table=table, user=request.user, status='pending')

        for item in items:
            menu_item = MenuItem.objects.get(id=item['id'])
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item['quantity'],
                note=item.get('note', '')
            )

        return JsonResponse({'success': True, 'order_id': order.id})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def add_menu_item(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            name = data.get('name')
            price = data.get('price')
            category = data.get('category')
            available = data.get('available')
            item = MenuItem.objects.create(name=name, price=price, category=category, available=available)
            return JsonResponse({'success': True, 'item': {'id': item.id, 'name': item.name, 'price': float(item.price), 'category': item.category, 'available': item.available}})
        else:
            name = request.POST.get('name')
            price = request.POST.get('price')
            category = request.POST.get('category')
            available = request.POST.get('available') == 'on'
            MenuItem.objects.create(name=name, price=price, category=category, available=available)
            return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def edit_menu_item(request, item_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        item = MenuItem.objects.get(id=item_id)
        item.name = data.get('name')
        item.price = data.get('price')
        item.category = data.get('category')
        item.available = data.get('available')
        item.save()
        return JsonResponse({'success': True, 'item': {'id': item.id, 'name': item.name, 'price': float(item.price), 'category': item.category, 'available': item.available}})
    return JsonResponse({'success': False})

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def delete_menu_item(request, item_id):
    if request.method == 'POST':
        MenuItem.objects.get(id=item_id).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def add_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table = Table.objects.get(number=data['table'])
        order = Order.objects.create(table=table, user=request.user, status=data['status'])
        return JsonResponse({'success': True, 'order': {'id': order.id, 'table': order.table.number, 'status': order.status}})

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def edit_order(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = Order.objects.get(id=id)
        table = Table.objects.get(number=data['table'])
        order.table = table
        order.status = data['status']
        order.save()
        return JsonResponse({'success': True, 'order': {'id': order.id, 'table': order.table.number, 'status': order.status}})

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def delete_order(request, id):
    if request.method == 'POST':
        Order.objects.get(id=id).delete()
        return JsonResponse({'success': True})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def add_table(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            number = data.get('number')
            capacity = data.get('capacity', 4)
            table = Table.objects.create(number=number)
            return JsonResponse({'success': True, 'table': {'id': table.id, 'number': table.number, 'capacity': capacity}})
        else:
            number = request.POST.get('number')
            Table.objects.create(number=number)
            return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def edit_table(request, table_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        table = Table.objects.get(id=table_id)
        table.number = data.get('number')
        table.save()
        return JsonResponse({'success': True, 'table': {'id': table.id, 'number': table.number, 'capacity': data.get('capacity', 4)}})
    return JsonResponse({'success': False})

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def delete_table(request, table_id):
    if request.method == 'POST':
        Table.objects.get(id=table_id).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def update_order_status_json(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status')
        order = Order.objects.get(id=order_id)
        order.status = status
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Recepcionista').exists())
def add_reservation(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        guests = request.POST.get('guests')
        table_id = request.POST.get('table')
        Reservation.objects.create(name=name, email=email, phone=phone, date=date, time=time, guests=guests, table_id=table_id)
        return redirect('receptionist_dashboard')
    return redirect('receptionist_dashboard')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Cocinero').exists())
def update_order_status(request, order_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        order = Order.objects.get(id=order_id)
        order.status = status
        order.save()
        return redirect('cook_dashboard')
    return redirect('cook_dashboard')
