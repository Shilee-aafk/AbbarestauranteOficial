from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db import IntegrityError
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
        'description': m.description,
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

    # Get served orders for the payment section
    served_orders = Order.objects.filter(status='served').select_related('table').order_by('-created_at')
    for order in served_orders:
        order.total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all())

    return render(request, 'restaurant/receptionist_dashboard.html', {
        'reservations': reservations,
        'tables': tables,
        'total_orders_today': total_orders_today,
        'preparing_count': preparing_count,
        'ready_count': ready_count,
        'completed_count': completed_count,
        'user_role': user_role,
        'served_orders': served_orders,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Cocinero').exists())
def cook_dashboard(request):
    from django.utils import timezone
    orders = Order.objects.filter(status__in=['pending', 'preparing']).select_related('table', 'user').prefetch_related('orderitem_set__menu_item').order_by('created_at')
    preparing_count = Order.objects.filter(status='preparing').count()
    ready_count = Order.objects.filter(status='ready').count()
    for order in orders:
        order.total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all()) if order.pk else 0
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

    # Get active orders for the monitor section
    active_orders = Order.objects.filter(status__in=['pending', 'preparing', 'ready']).select_related('table').prefetch_related('orderitem_set__menu_item').order_by('created_at')
    for order in active_orders:
        order.total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all())

    # Get orders that define the state of a table
    relevant_orders = Order.objects.filter(status__in=['pending', 'preparing', 'ready', 'served']).order_by('created_at')

    # Get served orders for the payment section
    served_orders = Order.objects.filter(status='served').order_by('-created_at')
    for order in served_orders:
        order.total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all())

    for table in tables:
        table.is_available = not relevant_orders.filter(table=table).exists()
        table.current_order = relevant_orders.filter(table=table).first() if not table.is_available else None

    user_role = request.user.groups.first().name if request.user.groups.exists() else None
    menu_items_json = json.dumps([{'id': item.id, 'name': item.name, 'price': float(item.price)} for item in menu_items])
    return render(request, 'restaurant/waiter_dashboard.html', {
        'tables': tables,
        'active_orders': active_orders,
        'served_orders': served_orders,
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

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Garzón').exists())
def api_waiter_order_detail(request, pk):
    """
    API endpoint for waiters to get and update a specific order.
    GET: Returns the items of an order.
    PUT: Updates the items of an order.
    """
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    if request.method == 'GET':
        items = order.orderitem_set.all()
        items_data = [{ 
            'id': item.menu_item.id,
            'name': item.menu_item.name,
            'price': float(item.menu_item.price),
            'quantity': item.quantity,
            'note': item.note,
        } for item in items]

        total = sum(item['price'] * item['quantity'] for item in items_data)

        data = {
            'status': order.status,
            'items': items_data,
            'total': total,
            'table_number': order.table.number,
        }
        return JsonResponse(data)

    if request.method == 'PUT':
        data = json.loads(request.body)
        items_data = data.get('items', [])

        # Delete old items and create new ones (simpler than diffing)
        order.orderitem_set.all().delete()

        for item_data in items_data:
            menu_item = MenuItem.objects.get(id=item_data['id'])
            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=item_data['quantity'], note=item_data.get('note', ''))
        
        # The signal will automatically trigger the real-time update
        order.save() # Trigger the post_save signal
        return JsonResponse({'success': True, 'order_id': order.id})

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


def crear_producto(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        category = data.get('category', 'General')
        available = data.get('available', True)

        producto = MenuItem.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            available=available
        )
        return JsonResponse({'message': 'Producto creado', 'id': producto.id})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# --- API Views for Admin Dashboard ---

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_orders(request):
    """
    GET: Returns a list of all orders.
    POST: Creates a new order.
    """
    if request.method == 'GET':
        orders = Order.objects.select_related('table').all().order_by('-created_at')
        data = [{
            'id': o.id,
            'table_number': o.table.number if o.table else 'N/A',
            'table_id': o.table.id if o.table else None,
            'status': o.get_status_display(),
        } for o in orders]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_id = data.get('table')
            status = data.get('status')

            if not table_id:
                return JsonResponse({'error': 'Table ID is required'}, status=400)

            table = Table.objects.get(id=table_id)
            order = Order.objects.create(table=table, user=request.user, status=status)
            
            return JsonResponse({
                'id': order.id,
                'table_id': order.table.id,
                'table_number': order.table.number,
                'status': order.get_status_display()
            }, status=201)
        except Table.DoesNotExist:
            return JsonResponse({'error': 'Table not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['Administrador', 'Recepcionista']).exists())
def api_order_detail(request, pk):
    """
    GET: Returns a single order.
    PUT: Updates an order.
    DELETE: Deletes an order.
    """
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    if request.method == 'GET':
<<<<<<< HEAD
        # Serializa los items del pedido
        order_items = order.orderitem_set.all()
        items_data = []
        for item in order_items:
            items_data.append({
                'id': item.id,
                'menu_item_id': item.menu_item.id,
                'menu_item_name': item.menu_item.name,
                'quantity': item.quantity,
                'price': float(item.menu_item.price), # Precio actual del item
                'note': item.note,
            })

        # Calcula el total basado en los precios actuales
        total = sum(item['price'] * item['quantity'] for item in items_data)

        # Prepara la respuesta JSON completa
        data = {
            'id': order.id,
            'table_id': order.table.id,
            'table_number': order.table.number,
            'user_id': order.user.id,
            'user_username': order.user.username,
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at,
            'total': total,
            'items': items_data,  # Aquí incluimos la lista de items
        }
        return JsonResponse(data)
=======
        items = order.orderitem_set.all()
        total = sum(item.menu_item.price * item.quantity for item in items)
        return JsonResponse({
            'id': order.id,
            'table_id': order.table.id,
            'table_number': order.table.number,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'user': order.user.username,
            'items': [{
                'id': item.id,
                'menu_item': item.menu_item.name,
                'price': float(item.menu_item.price),
                'quantity': item.quantity,
                'note': item.note,
                'subtotal': float(item.menu_item.price * item.quantity)
            } for item in items],
            'total': float(total)
        })
>>>>>>> a8e8363e154178963ea9ba642cc278d8c7122b17
    
    if request.method == 'PUT':
        data = json.loads(request.body)
        if 'table' in data:
            order.table = get_object_or_404(Table, pk=data['table'])
        if 'status' in data:
            order.status = data['status']
        order.save()
        return JsonResponse({'success': True, 'id': order.id})

    if request.method == 'DELETE':
        order.delete()
        return JsonResponse({'success': True}, status=204)

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_kitchen_orders(request):
    if request.method == 'GET':
        orders = Order.objects.filter(status__in=['pending', 'preparing']).select_related('table')
        data = [{
            'id': o.id,
            'table_number': o.table.number if o.table else 'N/A',
            'status': o.get_status_display(),
        } for o in orders]
        return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['Administrador', 'Garzón', 'Cocinero', 'Recepcionista']).exists())
def api_order_status(request, pk):
    if request.method == 'PUT':
        data = json.loads(request.body)
        order = Order.objects.get(pk=pk)
        order.status = data['status']
        order.save()
        return JsonResponse({'success': True, 'status': order.status})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_tables(request):
    """
    GET: Returns a list of all tables.
    POST: Creates a new table.
    """
    if request.method == 'GET':
        tables = Table.objects.all().order_by('number')
        data = [{
            'id': t.id,
            'number': t.number,
            'capacity': t.capacity,
        } for t in tables]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table = Table.objects.create(
                number=data['number'],
                capacity=data['capacity']
            )
            return JsonResponse({
                'id': table.id,
                'number': table.number,
                'capacity': table.capacity
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_table_detail(request, pk):
    try:
        table = Table.objects.get(pk=pk)
    except Table.DoesNotExist:
        return JsonResponse({'error': 'Table not found'}, status=404)

    if request.method == 'PUT':
        data = json.loads(request.body)
        table.number = data.get('number', table.number)
        table.capacity = data.get('capacity', table.capacity)
        table.save()
        return JsonResponse({'id': table.id, 'number': table.number, 'capacity': table.capacity})

    if request.method == 'DELETE':
        table.delete()
        return JsonResponse({'success': True}, status=204)

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_menu_items(request):
    """
    GET: Returns a list of all menu items.
    POST: Creates a new menu item.
    """
    if request.method == 'GET':
        menu_items = MenuItem.objects.all().order_by('category', 'name')
        data = [{
            'id': m.id, 'name': m.name, 'description': m.description,
            'price': float(m.price), 'category': m.category, 'available': m.available
        } for m in menu_items]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item = MenuItem.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                price=data['price'],
                category=data['category'],
                available=data.get('available', True)
            )
            return JsonResponse({
                'id': item.id, 'name': item.name, 'description': item.description,
                'price': float(item.price), 'category': item.category, 'available': item.available
            }, status=201)
        except (ValidationError, IntegrityError, ValueError, KeyError) as e:
            return JsonResponse({'error': f'Invalid data: {str(e)}'}, status=400)


@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_menu_item_detail(request, pk):
    """
    GET: Returns a single menu item.
    PUT: Updates a menu item.
    DELETE: Deletes a menu item.
    """
    try:
        item = MenuItem.objects.get(pk=pk)
    except MenuItem.DoesNotExist:
        return JsonResponse({'error': 'Menu item not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': item.id, 'name': item.name, 'description': item.description, 
            'price': float(item.price), 'category': item.category, 'available': item.available
        })
    
    if request.method == 'PUT':
        data = json.loads(request.body)
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        item.price = data.get('price', item.price)
        item.category = data.get('category', item.category)
        item.available = data.get('available', item.available)
        item.save()
        return JsonResponse({
            'id': item.id, 'name': item.name, 'description': item.description, 
            'price': float(item.price), 'category': item.category, 'available': item.available
        })

    if request.method == 'DELETE':
        item.delete()
        return JsonResponse({'success': True}, status=204)

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['Administrador', 'Recepcionista']).exists())
def api_orders_report(request):
    """
    API endpoint to get a filtered list of orders for reporting purposes.
    """
    if request.method == 'GET':
        from django.db.models import Q
        orders = Order.objects.select_related('table').prefetch_related('orderitem_set__menu_item').all()

        # Filtering
        search_query = request.GET.get('search', '')
        if search_query:
            if search_query.isdigit():
                orders = orders.filter(Q(id=int(search_query)) | Q(table__number__icontains=search_query))
            else:
                orders = orders.filter(Q(table__number__icontains=search_query))

        status_query = request.GET.get('status', '')
        if status_query:
            orders = orders.filter(status=status_query)

        date_from_query = request.GET.get('date_from', '')
        if date_from_query:
            orders = orders.filter(created_at__date__gte=date_from_query)

        date_to_query = request.GET.get('date_to', '')
        if date_to_query:
            orders = orders.filter(created_at__date__lte=date_to_query)

        orders = orders.order_by('-created_at')

        # Prepare data for JSON response
        data = []
        for order in orders:
            total = 0
            for item in order.orderitem_set.all():
                if item.menu_item: # Asegurarse de que menu_item existe antes de acceder a sus propiedades
                    total += item.menu_item.price * item.quantity

            data.append({
                'id': order.id,
                'table_number': order.table.number if order.table else 'N/A',
                'status': order.status,
                'status_display': order.get_status_display(),
                'status_class': order.status_class,
                'created_at': order.created_at,
                'total': total,
            })

        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['Administrador', 'Recepcionista']).exists())
def export_orders_csv(request):
    """
    Exports a filtered list of orders to a CSV file.
    """
    import csv
    from django.http import HttpResponse
    from django.utils import timezone

    orders = Order.objects.select_related('table').prefetch_related('orderitem_set__menu_item').all()

    # Filtering (same logic as api_orders_report)
    search_query = request.GET.get('search', '')
    if search_query:
        # Mantengo la lógica original que el usuario indicó que funcionaba para CSV
        # Aunque para IDs enteros, Q(id=int(search_query)) sería más preciso.
        orders = orders.filter(Q(id__icontains=search_query) | Q(table__number__icontains=search_query))

    status_query = request.GET.get('status', '')
    if status_query:
        orders = orders.filter(status=status_query)

    date_from_query = request.GET.get('date_from', '')
    if date_from_query:
        orders = orders.filter(created_at__date__gte=date_from_query)

    date_to_query = request.GET.get('date_to', '')
    if date_to_query:
        orders = orders.filter(created_at__date__lte=date_to_query)

    orders = orders.order_by('-created_at')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="reporte_pedidos_{timezone.now().strftime("%Y-%m-%d")}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID Pedido', 'Mesa', 'Estado', 'Fecha y Hora', 'Total'])

    for order in orders:
        total = 0
        for item in order.orderitem_set.all():
            if item.menu_item: # Asegurarse de que menu_item existe antes de acceder a sus propiedades
                total += item.menu_item.price * item.quantity
        writer.writerow([order.id, order.table.number, order.get_status_display(), order.created_at.strftime('%Y-%m-%d %H:%M'), total])

    return JsonResponse({'error': 'Invalid method'}, status=405)

    return response

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['Administrador', 'Recepcionista']).exists())
def export_orders_csv(request):
    """
    Exports a filtered list of orders to a CSV file.
    """
    import csv
    from django.http import HttpResponse
    from django.utils import timezone

    orders = Order.objects.select_related('table').all()

    # Filtering (same logic as api_orders_report)
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(Q(id__icontains=search_query) | Q(table__number__icontains=search_query))

    status_query = request.GET.get('status', '')
    if status_query:
        orders = orders.filter(status=status_query)

    date_from_query = request.GET.get('date_from', '')
    if date_from_query:
        orders = orders.filter(created_at__date__gte=date_from_query)

    date_to_query = request.GET.get('date_to', '')
    if date_to_query:
        orders = orders.filter(created_at__date__lte=date_to_query)

    orders = orders.order_by('-created_at')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="reporte_pedidos_{timezone.now().strftime("%Y-%m-%d")}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID Pedido', 'Mesa', 'Estado', 'Fecha y Hora', 'Total'])

    for order in orders:
        total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all())
        writer.writerow([order.id, order.table.number, order.get_status_display(), order.created_at.strftime('%Y-%m-%d %H:%M'), total])

    return response

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_dashboard_charts(request):
    from django.db.models import Sum, Count, F
    from django.db.models.functions import TruncDate
    from django.utils import timezone
    from datetime import timedelta

    chart_type = request.GET.get('chart')

    if chart_type == 'sales_by_day':
        # Ventas de los últimos 7 días para pedidos pagados
        seven_days_ago = timezone.now().date() - timedelta(days=6)
        sales_data = Order.objects.filter(
            status='paid',
            created_at__date__gte=seven_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            # Usamos F() para referenciar campos y hacer el cálculo en la DB
            daily_total=Sum(F('orderitem__menu_item__price') * F('orderitem__quantity'))
        ).order_by('date')

        # Preparamos los datos para el gráfico, asegurando que haya 7 días
        labels = [(seven_days_ago + timedelta(days=i)).strftime('%b %d') for i in range(7)]
        sales_dict = {s['date'].strftime('%b %d'): float(s['daily_total']) for s in sales_data}
        data = [sales_dict.get(label, 0) for label in labels]

        return JsonResponse({'labels': labels, 'data': data})

    if chart_type == 'top_dishes':
        # Top 5 platos más vendidos
        top_dishes = MenuItem.objects.annotate(
            total_sold=Sum('orderitem__quantity', filter=F('orderitem__order__status')=='paid')
        ).filter(total_sold__gt=0).order_by('-total_sold')[:5]

        labels = [item.name for item in top_dishes]
        data = [item.total_sold for item in top_dishes]
        return JsonResponse({'labels': labels, 'data': data})

    return JsonResponse({'error': 'Invalid chart type'}, status=400)