from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, F, Q, Prefetch, ExpressionWrapper, fields
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Reservation, Order, OrderItem, MenuItem, Group, RegistrationPin
import json
import decimal


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal objects"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
            return redirect('restaurant:admin_dashboard')
        elif request.user.groups.filter(name='Recepcionista').exists():
            return redirect('restaurant:receptionist_dashboard')
        elif request.user.groups.filter(name='Cocinero').exists():
            return redirect('restaurant:cook_dashboard')
        elif request.user.groups.filter(name='Garzón').exists():
            return redirect('restaurant:waiter_dashboard')
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
            return redirect('restaurant:home')  # Redirige a home, que gestionará el dashboard correcto
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    """
    Vista para el inicio de sesión de usuarios.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('restaurant:home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

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
    # Ahora que total_amount se almacena directamente, no necesitamos annotate aquí.
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Nota: 'orders' aquí es Order.objects.all(), no recent_orders.
    # El resto de los objetos se cargan para el renderizado inicial o como fallback.
    reservations = Reservation.objects.all()
    orders = Order.objects.all()
    menu_items = MenuItem.objects.all()
    groups = Group.objects.all()  # Obtener todos los grupos/roles
    user_role = request.user.groups.first().name if request.user.groups.exists() else None

    # JSON data for JavaScript
    orders_json = json.dumps([{
        'id': o.id,
        'identifier': o.room_number or o.client_identifier,
        'status': o.status,
        'user': o.user.username,
        'created_at': o.created_at.isoformat(),
        'total': float(o.total_amount), # Usar el nuevo campo total_amount
    } for o in orders], cls=DecimalEncoder)
    menu_items_json = json.dumps([{
        'id': m.id,
        'name': m.name,
        'description': m.description,
        'price': float(m.price),
        'category': m.category,
        'available': m.available
    } for m in menu_items], cls=DecimalEncoder)
    return render(request, 'restaurant/admin_dashboard.html', {
        'reservations': reservations,
        'orders': orders,
        'menu_items': menu_items,
        'groups': groups,  # Pasar los grupos a la plantilla
        'total_orders_today': stats.get('total_today', 0),
        'preparing_count': stats.get('preparing', 0),
        'ready_count': stats.get('ready', 0),
        'completed_count': stats.get('completed', 0),
        'recent_orders': recent_orders,
        'user_role': user_role,
        'orders_json': orders_json,
        'menu_items_json': menu_items_json,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Recepcionista').exists())
def receptionist_dashboard(request):
    from django.utils import timezone
    from django.db.models import Sum, F, Q

    # Unificamos los pedidos que necesitan acción de cobro: 'servido' y 'cargado a habitación'
    served_orders = Order.objects.filter(status__in=['served', 'charged_to_room']).order_by('-created_at')
    
    # Ahora que total_amount se almacena directamente, no necesitamos annotate aquí.
    room_charge_orders = Order.objects.filter(status='charged_to_room').order_by('-created_at')



    today = timezone.now().date()
    total_sales_today = Order.objects.filter(
        status='paid',
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0 # Usar el nuevo campo total_amount

    reservations = Reservation.objects.all()
    user_role = request.user.groups.first().name if request.user.groups.exists() else None

    return render(request, 'restaurant/receptionist_dashboard.html', {
        'reservations': reservations,
        'user_role': user_role,
        'served_orders': served_orders,
        'room_charge_orders': room_charge_orders,
        'total_sales_today': total_sales_today,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Cocinero').exists())
def cook_dashboard(request):
    import json
    from django.utils import timezone

    # Consulta optimizada para obtener pedidos y sus items
    # Ahora que total_amount se almacena directamente, no necesitamos annotate aquí.
    orders = Order.objects.filter(status__in=['pending', 'preparing']).select_related('user').prefetch_related('orderitem_set__menu_item').order_by('created_at')

    # Preparar datos JSON para el frontend
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'status': order.status,
            'identifier': order.room_number or order.client_identifier,
            'user_username': order.user.username,
            'created_at': order.created_at.isoformat(), # No need to change, total is not here
            'items': [{
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'note': item.note or ''
            } for item in order.orderitem_set.all()]
        })

    return render(request, 'restaurant/cook_dashboard.html', {
        'orders': orders,
        'orders_json': json.dumps(orders_data, cls=DecimalEncoder)
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Garzón').exists())
def waiter_dashboard(request):
    import json
    from django.utils import timezone

    # --- Datos para la toma de pedidos ---
    menu_items = MenuItem.objects.filter(available=True)
    # Obtenemos todas las categorías, las normalizamos en Python y eliminamos duplicados.
    # Esto asegura que 'Pizzas' y 'pizzas' se traten como una sola categoría en los filtros.
    all_categories = menu_items.values_list('category', flat=True)
    normalized_categories = {cat.capitalize() for cat in all_categories}
    categories = sorted(list(normalized_categories))
    menu_items_json = json.dumps([{'id': item.id, 'name': item.name, 'price': float(item.price)} for item in menu_items], cls=DecimalEncoder)

    # --- Datos para el monitor de pedidos (carga inicial) ---
    # Usamos prefetch_related para cargar los items de una vez y evitar N+1 queries
    orders_for_monitor = Order.objects.filter(
        status__in=['pending', 'preparing', 'ready', 'served']
    ).prefetch_related('orderitem_set__menu_item').order_by('created_at')


    initial_orders_data = []
    for order in orders_for_monitor:
        initial_orders_data.append({
            'id': order.id,
            'status': order.status,
            'status_display': order.get_status_display(),
            'status_class': order.status_class,
            'identifier': order.room_number or order.client_identifier, # No need to change, total is not here
            'total': float(order.total_amount), # Añadir el total para que el monitor lo renderice
            'items': [{
                'name': item.menu_item.name,
                'quantity': item.quantity,
            } for item in order.orderitem_set.all()]
        })

    initial_orders_json = json.dumps(initial_orders_data, cls=DecimalEncoder)

    user_role = request.user.groups.first().name if request.user.groups.exists() else None

    return render(request, 'restaurant/waiter_dashboard.html', {
        'menu_items': menu_items,
        'categories': categories,
        'menu_items_json': menu_items_json,
        'initial_orders_json': initial_orders_json,
        'user_role': user_role,
    })

def public_menu_view(request):
    """
    Vista pública para mostrar el menú del restaurante, ideal para un código QR.
    No requiere autenticación.
    """
    # Obtener solo los items disponibles y ordenarlos por categoría
    menu_url = request.build_absolute_uri()
    menu_items = MenuItem.objects.filter(available=True).order_by('category', 'name')

    # Agrupar items por categoría en un diccionario
    grouped_menu = {}
    for item in menu_items:
        category = item.category
        if not category: # Agrupar items sin categoría en 'Otros'
            category = 'Otros'
        if category not in grouped_menu:
            grouped_menu[category] = []
        grouped_menu[category].append(item)

    return render(request, 'restaurant/public_menu.html', {
        'grouped_menu': grouped_menu,
        # Puedes añadir más contexto si lo necesitas, como el nombre del restaurante
        'restaurant_name': 'Restaurante AbbaHotel',
        'menu_url': menu_url
    })

# Helper function to calculate subtotal for an order instance
def calculate_order_subtotal(order_instance):
    return order_instance.orderitem_set.aggregate(
        subtotal=Sum(F('menu_item__price') * F('quantity'), output_field=fields.DecimalField())
    )['subtotal'] or decimal.Decimal('0.00')
@csrf_exempt
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Garzón').exists())
def save_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            tip_amount = decimal.Decimal(str(data.get('tip_amount', '0.00')))

            order = None
            # Usar una transacción atómica para asegurar la integridad de los datos.
            # O todo se crea, o nada se crea si hay un error.
            with transaction.atomic():
                order = Order.objects.create(
                    client_identifier=data.get('client_identifier'),
                    room_number=data.get('room_number'),
                    user=request.user, 
                    status='pending',
                    tip_amount=tip_amount
                    # total_amount will be calculated after order items are added
                )

                subtotal = decimal.Decimal('0.00')
                for item in items:
                    try:
                        menu_item = MenuItem.objects.get(id=item['id'])
                        OrderItem.objects.create(
                            order=order,
                            menu_item=menu_item,
                            quantity=int(item.get('quantity', 1)),
                            note=str(item.get('note', ''))
                        )
                        subtotal += menu_item.price * int(item.get('quantity', 1))
                    except MenuItem.DoesNotExist:
                        raise ValueError(f"MenuItem with id {item['id']} not found")
                
                order.total_amount = subtotal + tip_amount # El total ahora incluye la propina desde el inicio
                order.save() # Save again to update total_amount
            
            if order:
                return JsonResponse({'success': True, 'order_id': order.id})
            else:
                return JsonResponse({'success': False, 'error': 'Order could not be created'}, status=400)
                
        except MenuItem.DoesNotExist as e:
            return JsonResponse({'success': False, 'error': f'MenuItem not found: {str(e)}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': f'Invalid JSON: {str(e)}'}, status=400)
        except ValueError as e:
            return JsonResponse({'success': False, 'error': f'Validation error: {str(e)}'}, status=400)
        except Exception as e:
            import traceback
            error_msg = str(e)
            traceback_msg = traceback.format_exc()
            print(f"Error in save_order: {error_msg}")
            print(traceback_msg)
            return JsonResponse({'success': False, 'error': f'Server error: {error_msg}'}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

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

        subtotal = sum(item['price'] * item['quantity'] for item in items_data)

        data = {
            'status': order.status,
            'items': items_data,
            'subtotal': subtotal, # Se agrega el subtotal para que el modal de pago funcione
            'total': subtotal + float(order.tip_amount), # El total ahora incluye la propina
            'identifier': order.room_number or order.client_identifier,
            'room_number': order.room_number, # Asegurarse de que este campo siempre esté presente
        }
        return JsonResponse(data)

    if request.method == 'PUT':
        data = json.loads(request.body)
        items_data = data.get('items', [])

        with transaction.atomic(): # Add transaction for atomicity
            # Delete old items and create new ones (simpler than diffing)
            order.orderitem_set.all().delete()

            subtotal = decimal.Decimal('0.00')
            for item_data in items_data:
                menu_item = MenuItem.objects.get(id=item_data['id'])
                OrderItem.objects.create(order=order, menu_item=menu_item, quantity=item_data['quantity'], note=item_data.get('note', ''))
                subtotal += menu_item.price * item_data['quantity']
            
            order.total_amount = subtotal + order.tip_amount # Recalcular total_amount con el nuevo subtotal
            order.save() # Trigger the post_save signal
            return JsonResponse({'success': True, 'order_id': order.id})

@csrf_exempt
@user_passes_test(lambda u: u.groups.filter(name='Recepcionista').exists())
def add_reservation(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        guests = request.POST.get('guests')
        notes = request.POST.get('notes')
        Reservation.objects.create(
            user=request.user,
            client_name=name, 
            phone=phone, 
            date=date, 
            time=time, 
            guests=guests, 
            notes=notes
        )
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
        orders = Order.objects.select_related('user').all().order_by('-created_at')
        data = [{
            'id': o.id,
            'identifier': o.room_number or o.client_identifier,
            'status': o.get_status_display(),
        } for o in orders]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.create(
                client_identifier=data['client_identifier'],
                room_number=data.get('room_number'),
                user=request.user,
                status=data.get('status', 'pending')
            )
            
            return JsonResponse({
                'id': order.id,
                'identifier': order.room_number or order.client_identifier,
                'status': order.get_status_display()
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)



@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
def api_kitchen_orders(request):
    if request.method == 'GET':
        orders = Order.objects.filter(status__in=['pending', 'preparing'])
        data = [{
            'id': o.id,
            'identifier': o.room_number or o.client_identifier,
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

        subtotal = sum(item['price'] * item['quantity'] for item in items_data)
        tip_amount = float(order.tip_amount)

        data = {
            'id': order.id,
            'identifier': order.room_number or order.client_identifier,
            'status': order.status,
            'status_display': order.get_status_display(),
            'created_at': order.created_at.isoformat(),
            'user': order.user.username,
            'items': items_data,
            'subtotal': subtotal,
            'tip_amount': tip_amount,
            'total': subtotal + tip_amount,
        }
        return JsonResponse(data)

    if request.method == 'PUT':
        data = json.loads(request.body)
        order.client_identifier = data.get('client_identifier', order.client_identifier)
        order.room_number = data.get('room_number', order.room_number)
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
        try:
            data = json.loads(request.body)
            order = Order.objects.get(pk=pk)
            new_status = data.get('status')
            
            if not new_status:
                return JsonResponse({'success': False, 'error': 'Status is required'}, status=400)
            
            order.status = new_status
            update_fields = ['status']
            
            # Solo recalcular el total si se envía explícitamente una nueva propina.
            # Esto evita que el modal de recepción recalcule el total con propinas antiguas.
            if new_status in ['paid', 'charged_to_room'] and 'tip_amount' in data:
                try:
                    order.tip_amount = decimal.Decimal(str(data['tip_amount'])) # Ensure it's a Decimal
                    subtotal = calculate_order_subtotal(order)
                    order.total_amount = subtotal + order.tip_amount
                    update_fields.extend(['tip_amount', 'total_amount'])
                except (ValueError, decimal.InvalidOperation) as e:
                    return JsonResponse({'success': False, 'error': f'Invalid tip amount: {str(e)}'}, status=400)

            order.save(update_fields=update_fields)  # Only trigger signal for fields we actually changed
            return JsonResponse({'success': True, 'status': order.status, 'total_amount': float(order.total_amount)})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': f'Invalid JSON: {str(e)}'}, status=400)
        except Exception as e:
            import traceback
            print(f"Error in api_order_status: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)
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
        from datetime import datetime
        orders = Order.objects.all() # total_amount is now a stored field

        # Filtering
        search_query = request.GET.get('search', '')
        if search_query:
            # Búsqueda segura: Intenta buscar por ID si es un número, si no, solo por número de mesa.
            # Esto evita el error si el `search_query` no es un número válido.
            id_query = Q()
            if search_query.isdigit():
                id_query = Q(id=int(search_query))
            orders = orders.filter(id_query | Q(client_identifier__icontains=search_query) | Q(room_number__icontains=search_query))

        status_query = request.GET.get('status', '')
        if status_query:
            orders = orders.filter(status=status_query)

        date_from_query = request.GET.get('date_from', '')
        if date_from_query:
            try:
                date_from = datetime.strptime(date_from_query, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date__gte=date_from)
            except ValueError:
                pass  # Si la fecha no es válida, ignorar el filtro

        date_to_query = request.GET.get('date_to', '')
        if date_to_query:
            try:
                date_to = datetime.strptime(date_to_query, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date__lte=date_to)
            except ValueError:
                pass  # Si la fecha no es válida, ignorar el filtro

        orders = orders.order_by('-created_at')

        # Prepare data for JSON response
        data = []
        for order in orders:
            data.append({
                'id': order.id,
                'identifier': order.room_number or order.client_identifier,
                'status': order.status,
                'status_display': order.get_status_display(),
                'status_class': order.status_class,
                'created_at': order.created_at.isoformat(), # Ensure datetime is serializable
                'total': float(order.total_amount or 0), # Usar el nuevo campo total_amount
            })

        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['Administrador', 'Recepcionista']).exists())
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
        ).values('date').annotate( # Use the new total_amount field
            daily_total=Sum('total_amount')
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
            hour=ExtractHour('created_at') # Use the new total_amount field
        ).values('hour').annotate( 
            hourly_total=Sum('total_amount')
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
            order_count=Count('id'), # Use the new total_amount field
            total_sales=Sum('total_amount', filter=Q(status='paid'))
        ).order_by('-order_count')

        labels = [d['user__username'] for d in performance_data]
        data_orders = [d['order_count'] for d in performance_data]
        data_sales = [float(d['total_sales'] or 0) for d in performance_data]

        return JsonResponse({'labels': labels, 'orders': data_orders, 'sales': data_sales})

    if chart_type == 'sales_by_category':
        # Ventas de hoy por categoría de producto
        category_sales = OrderItem.objects.filter(
            order__status='paid',
            order__created_at__date=today
        ).values('menu_item__category').annotate(
            total=Sum(F('menu_item__price') * F('quantity'))
        ).order_by('-total')
        labels = [c['menu_item__category'] for c in category_sales]
        data = [float(c['total']) for c in category_sales]
        return JsonResponse({'labels': labels, 'data': data})

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
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['Administrador', 'Recepcionista']).exists())
def export_orders_excel(request):
    """
    Exports a filtered list of orders to an Excel file (.xlsx).
    """
    from django.http import HttpResponse
    from django.utils import timezone

    orders = Order.objects.prefetch_related('orderitem_set__menu_item').all()

    # Filtering (same logic as api_orders_report)
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(Q(id__icontains=search_query) | Q(client_identifier__icontains=search_query) | Q(room_number__icontains=search_query))

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

    # Create an Excel workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte de Pedidos"

    # Define styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    total_font = Font(bold=True)
    currency_format = '"$"#,##0'

    # Write headers
    headers = ['ID Pedido', 'Cliente/Habitación', 'Estado', 'Fecha y Hora', 'Total']
    for col_num, header_title in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header_title)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    # Write data rows
    grand_total = 0
    row_num = 2
    grand_total = decimal.Decimal('0.00')
    for order in orders:
        final_total = order.total_amount # Use the new field
        if final_total:
            grand_total += final_total
        local_time = timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M')
        
        ws.cell(row=row_num, column=1, value=order.id)
        ws.cell(row=row_num, column=2, value=order.room_number or order.client_identifier)
        ws.cell(row=row_num, column=3, value=order.get_status_display())
        ws.cell(row=row_num, column=4, value=local_time)
        total_cell = ws.cell(row=row_num, column=5, value=final_total)
        total_cell.number_format = currency_format
        row_num += 1

    # Write total row
    total_label_cell = ws.cell(row=row_num + 1, column=4, value="Total Vendido:")
    total_label_cell.font = total_font
    total_label_cell.alignment = Alignment(horizontal='right')

    grand_total_cell = ws.cell(row=row_num + 1, column=5, value=grand_total)
    grand_total_cell.font = total_font
    grand_total_cell.number_format = currency_format
    grand_total_cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid") # Yellow fill

    # Adjust column widths
    for col_num, header_title in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        ws.column_dimensions[column_letter].width = 20

    # Create the response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="reporte_pedidos_{timezone.now().strftime("%Y-%m-%d")}.xlsx"'
    wb.save(response)

    return response

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administrador').exists())
@csrf_exempt
def api_users(request, pk=None):
    """
    API endpoint to manage users.
    - GET /api/users/ -> List all users.
    - PUT /api/users/<pk>/ -> Update a user's role.
    - DELETE /api/users/<pk>/ -> Delete a user.
    """
    # --- Manejo de un usuario específico (PUT, DELETE) ---
    if pk:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        # Evitar que un administrador se modifique o elimine a sí mismo
        if user == request.user:
            return JsonResponse({'error': 'No puedes modificar o eliminar tu propia cuenta.'}, status=403)

        if request.method == 'PUT':
            data = json.loads(request.body)
            group_id = data.get('group_id')
            try:
                group = Group.objects.get(id=group_id)
                user.groups.set([group]) # set() reemplaza todos los grupos existentes
                return JsonResponse({'success': True, 'message': 'Rol de usuario actualizado.'})
            except Group.DoesNotExist:
                return JsonResponse({'error': 'El rol especificado no existe.'}, status=400)

        elif request.method == 'DELETE':
            user.delete()
            return JsonResponse({'success': True, 'message': 'Usuario eliminado.'}, status=204)

    # --- Manejo de la lista de usuarios (GET) ---
    elif request.method == 'GET':
        users = User.objects.prefetch_related('groups').all().order_by('username')
        data = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'group_id': user.groups.first().id if user.groups.exists() else None,
            'group_name': user.groups.first().name if user.groups.exists() else 'N/A',
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Nunca'
        } for user in users]
        return JsonResponse(data, safe=False)

    # Método no permitido para la URL solicitada
    return JsonResponse({'error': f'Método {request.method} no permitido.'}, status=405)