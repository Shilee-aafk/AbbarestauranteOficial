from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, login
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, F, Q, Prefetch, ExpressionWrapper, fields
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
import json, decimal
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from .models import Reservation, Order, OrderItem, MenuItem, Table, Group, RegistrationPin

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

def signup_view(request):
    """
    Vista para el registro de nuevos usuarios.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Inicia sesión automáticamente para el nuevo usuario
            login(request, user)
            return redirect('home')  # Redirige a home, que gestionará el dashboard correcto
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def admin_dashboard(request):
    # ... (el resto de la vista se mantiene igual)
    import json
    from django.utils import timezone    

    # --- Optimización de Consultas ---
    # 1. Usar aggregate para obtener todos los contadores en una sola consulta
    stats = Order.objects.aggregate(
        total_today=Count('id', filter=Q(created_at__date=timezone.now().date())),
        preparing=Count('id', filter=Q(status='preparing')),
        ready=Count('id', filter=Q(status='ready')),
        completed=Count('id', filter=Q(status__in=['served', 'paid']))
    )

    # 2. Usar annotate para calcular el total de cada pedido en la DB (evita N+1)
    #    y prefetch_related para cargar los items eficientemente.
    recent_orders = Order.objects.annotate(
        total=Sum(F('orderitem__menu_item__price') * F('orderitem__quantity'))
    ).select_related('table', 'user').order_by('-created_at')[:10]

    # El resto de los objetos se cargan para el renderizado inicial o como fallback.
    reservations = Reservation.objects.all()
    orders = Order.objects.all()
    menu_items = MenuItem.objects.all()
    tables = Table.objects.all()
    groups = Group.objects.all()  # Obtener todos los grupos/roles
    user_role = request.user.groups.first().name if request.user.groups.exists() else None

    # JSON data for JavaScript
    orders_json = json.dumps([{
        'id': o.id,
        'table': o.table.number,
        'status': o.status,
        'user': o.user.username,
        'created_at': o.created_at.isoformat(),
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
        'groups': groups,  # Pasar los grupos a la plantilla
        'total_orders_today': stats.get('total_today', 0),
        'preparing_count': stats.get('preparing', 0),
        'ready_count': stats.get('ready', 0),
        'completed_count': stats.get('completed', 0),
        'recent_orders': recent_orders,
        'user_role': user_role,
        'orders_json': orders_json,
        'tables_json': tables_json,
        'menu_items_json': menu_items_json,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Recepcionista').exists())
def receptionist_dashboard(request):
    from django.utils import timezone

    # --- Optimización de Consultas ---
    # 1. Usar annotate para calcular el total de cada pedido en la DB (evita N+1)
    served_orders = Order.objects.filter(status='served').annotate(
        total=Sum(F('orderitem__menu_item__price') * F('orderitem__quantity'))
    ).select_related('table').order_by('-created_at')

    reservations = Reservation.objects.all()
    tables = Table.objects.all()
    user_role = request.user.groups.first().name if request.user.groups.exists() else None

    return render(request, 'restaurant/receptionist_dashboard.html', {
        'reservations': reservations,
        'tables': tables,
        'user_role': user_role,
        'served_orders': served_orders,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Cocinero').exists())
def cook_dashboard(request):
    import json
    from django.utils import timezone

    # Consulta optimizada para obtener pedidos y sus items
    orders = Order.objects.filter(status__in=['pending', 'preparing']).annotate(
        total=Sum(F('orderitem__menu_item__price') * F('orderitem__quantity'))
    ).select_related('table', 'user').prefetch_related('orderitem_set__menu_item').order_by('created_at')

    # Preparar datos JSON para el frontend
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'status': order.status,
            'table_number': order.table.number if order.table else 'N/A',
            'user_username': order.user.username,
            'created_at': order.created_at.isoformat(),
            'items': [{
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'note': item.note or ''
            } for item in order.orderitem_set.all()]
        })

    return render(request, 'restaurant/cook_dashboard.html', {
        'orders': orders,
        'orders_json': json.dumps(orders_data)
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Garzón').exists())
def waiter_dashboard(request):
    import json
    from django.utils import timezone

    # --- Optimización de Consultas ---
    menu_items = MenuItem.objects.filter(available=True)
    categories = menu_items.values_list('category', flat=True).distinct()

    # Consultas para obtener los pedidos y las mesas
    relevant_orders = Order.objects.filter(status__in=['pending', 'preparing', 'ready', 'served'])
    active_orders = relevant_orders.exclude(status='served').select_related('table').prefetch_related('orderitem_set__menu_item').order_by('created_at')
    served_orders = Order.objects.filter(status='served').order_by('-created_at')
    
    # Usar Prefetch para cargar eficientemente los pedidos relevantes para cada mesa
    order_prefetch = Prefetch('order_set', queryset=relevant_orders.order_by('created_at'), to_attr='relevant_orders')
    tables = Table.objects.prefetch_related(order_prefetch).all()

    # Determinar el estado de cada mesa en Python para evitar consultas adicionales en el bucle
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
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['Administrador', 'Recepcionista']).exists())
def api_order_detail(request, pk):
    """
    API endpoint for admin to get and update a specific order.
    GET: Returns the details of an order.
    PUT: Updates the order details.
    DELETE: Deletes the order.
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
            'id': order.id,
            'table_number': order.table.number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at.isoformat(),
            'user': order.user.username,
            'items': items_data,
            'total': total,
        }
        return JsonResponse(data)

    if request.method == 'PUT':
        data = json.loads(request.body)
        order.status = data.get('status', order.status)

        order.save()
        return JsonResponse({'success': True, 'order_id': order.id})

    if request.method == 'DELETE':
        order.delete()
        return JsonResponse({'success': True}, status=204)

    return JsonResponse({'error': 'Invalid method'}, status=405)

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

    if request.method == 'GET':
        data = {
            'id': table.id,
            'number': table.number,
            'capacity': table.capacity,
        }
        return JsonResponse(data)

    if request.method == 'PUT': # El frontend envía PUT para editar
        data = json.loads(request.body)
        table.number = data.get('number', table.number)
        table.capacity = data.get('capacity', table.capacity)
        table.save()
        return JsonResponse({'id': table.id, 'number': table.number, 'capacity': table.capacity})

    elif request.method == 'DELETE':
        table.delete()
        return JsonResponse({'success': True}, status=204)

    return JsonResponse({'error': 'Invalid method'}, status=405)

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
    writer.writerow(['ID Pedido', 'Mesa', 'Estado', 'Fecha y Hora', 'Total', 'Items'])

    for order in orders:
        total = 0 
        for item in order.orderitem_set.all():
            if item.menu_item: # Asegurarse de que menu_item existe antes de acceder a sus propiedades
                total += item.menu_item.price * item.quantity
        writer.writerow([order.id, order.table.number, order.get_status_display(), order.created_at.strftime('%Y-%m-%d %H:%M'), total])

    return response
    
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_dashboard_charts(request):
    from django.db.models import Sum, Count, F, Q, Case, When, Value, IntegerField
    from django.db.models.functions import TruncDate, ExtractHour
    from django.utils import timezone
    from datetime import timedelta

    chart_type = request.GET.get('chart')
    today = timezone.now().date()

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
            total_sold=Sum('orderitem__quantity', filter=Q(orderitem__order__status='paid'))
        ).filter(total_sold__gt=0).order_by('-total_sold')[:5]

        labels = [item.name for item in top_dishes]
        data = [item.total_sold for item in top_dishes]
        return JsonResponse({'labels': labels, 'data': data})

    if chart_type == 'sales_by_hour':
        # Ventas de hoy por hora
        sales_data = Order.objects.filter(
            status='paid',
            created_at__date=today
        ).annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(
            hourly_total=Sum(F('orderitem__menu_item__price') * F('orderitem__quantity'))
        ).order_by('hour')

        labels = [f"{h}:00" for h in range(24)]
        sales_dict = {s['hour']: float(s['hourly_total']) for s in sales_data}
        data = [sales_dict.get(h, 0) for h in range(24)]
        
        return JsonResponse({'labels': labels, 'data': data})

    if chart_type == 'waiter_performance':
        # Rendimiento de garzones (pedidos atendidos hoy)
        waiters = User.objects.filter(groups__name='Garzón')
        performance_data = Order.objects.filter(
            created_at__date=today,
            user__in=waiters
        ).values('user__username').annotate(
            order_count=Count('id'),
            total_sales=Sum(F('orderitem__menu_item__price') * F('orderitem__quantity'), filter=Q(status='paid'))
        ).order_by('-order_count')

        labels = [d['user__username'] for d in performance_data]
        data_orders = [d['order_count'] for d in performance_data]
        data_sales = [float(d['total_sales'] or 0) for d in performance_data]

        return JsonResponse({'labels': labels, 'orders': data_orders, 'sales': data_sales})

    return JsonResponse({'error': 'Invalid chart type'}, status=400)

@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_registration_pins(request, pk=None):
    """
    API para gestionar los PINs de registro.
    - GET /api/pins/ -> Devuelve todos los PINs.
    - POST /api/pins/ -> Crea un nuevo PIN para un grupo.
    - DELETE /api/pins/<pk>/ -> Elimina un PIN específico.
    """
    from django.utils import timezone
    import string
    import random

    # --- Manejo de un PIN específico (DELETE) ---
    if pk is not None:
        if request.method == 'DELETE':
            try:
                pin = RegistrationPin.objects.get(pk=pk)
                pin.delete()
                return JsonResponse({'success': True, 'message': 'PIN eliminado'}, status=204) # 204 No Content
            except RegistrationPin.DoesNotExist:
                return JsonResponse({'error': 'PIN no encontrado'}, status=404)
        else:
            # No se permite GET o POST a un PIN específico por ahora
            return JsonResponse({'error': f'Método {request.method} no permitido para esta URL.'}, status=405)

    # --- Manejo de la colección de PINs (GET, POST) ---
    if request.method == 'GET':
        pins = RegistrationPin.objects.select_related('group', 'used_by').order_by('-created_at')
        data = [{
            'id': pin.id,
            'pin': pin.pin,
            'group_name': pin.group.name,
            'is_used': pin.used_by is not None,
            'used_by': pin.used_by.username if pin.used_by else '-',
            'created_at': timezone.localtime(pin.created_at).strftime('%Y-%m-%d %H:%M')
        } for pin in pins]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        group_id = data.get('group_id')
        if not group_id:
            return JsonResponse({'error': 'El ID del grupo (group_id) es requerido.'}, status=400)
        try:
            group = Group.objects.get(id=group_id)
            # Generar un PIN aleatorio y único
            while True:
                pin_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                if not RegistrationPin.objects.filter(pin=pin_code).exists():
                    break
            pin = RegistrationPin.objects.create(pin=pin_code, group=group)
            return JsonResponse({'success': True, 'pin': pin.pin, 'group': group.name}, status=201)
        except Group.DoesNotExist:
            return JsonResponse({'error': 'El grupo seleccionado no existe.'}, status=400)
    
    # Si llega aquí, es un método no manejado para la URL base
    return JsonResponse({'error': f'Método {request.method} no permitido.'}, status=405)

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
        total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all() if item.menu_item)
        # Convertir a la zona horaria local antes de formatear
        local_time = timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M')
        writer.writerow([order.id, order.table.number, order.get_status_display(), local_time, total])

    return response