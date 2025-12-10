# Plan de Implementación: Métodos de Pago

## 1. Cambios en Modelos (models.py)

### Opción A: Campo simple en Order (Recomendado para empezar)
```python
class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('check', 'Cheque'),
        ('mixed', 'Mixto'),
    ]
    
    # ... campos existentes ...
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        default='cash',
        help_text="Payment method used for this order"
    )
    paid_at = models.DateTimeField(null=True, blank=True, help_text="When the order was paid")
```

### Opción B: Modelo separado PaymentTransaction (Más robusto)
```python
class PaymentTransaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('check', 'Cheque'),
        ('mixed', 'Mixto'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)  # # de cheque, referencia transferencia, etc
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
```

---

## 2. Migraciones

```bash
# Crear migración
python manage.py makemigrations

# Aplicar cambios
python manage.py migrate
```

---

## 3. Cambios en Views

### API para procesar pago con método:

```python
@login_required
def api_process_payment(request, pk):
    """
    Procesa el pago de una orden con un método específico
    """
    if request.method == 'PUT':
        try:
            order = Order.objects.get(pk=pk)
            data = json.loads(request.body)
            
            payment_method = data.get('payment_method', 'cash')
            tip_amount = data.get('tip_amount', 0)
            reference = data.get('reference', '')  # Para cheque/transferencia
            
            # Validar método de pago válido
            valid_methods = dict(Order.PAYMENT_METHOD_CHOICES).keys()
            if payment_method not in valid_methods:
                return JsonResponse({'error': 'Invalid payment method'}, status=400)
            
            # Actualizar orden
            order.payment_method = payment_method
            order.paid_at = timezone.now()
            order.status = 'paid'
            order.tip_amount = tip_amount
            order.total_amount = order.total_amount + tip_amount
            order.save()
            
            return JsonResponse({'success': True, 'order_id': order.id})
            
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
```

---

## 4. Cambios en Template (receptionist_dashboard.html)

### Modal de Pago Mejorado:

```html
<!-- Payment Modal -->
<div id="payment-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 class="text-xl font-bold mb-4">Procesar Pago</h2>
        
        <div class="mb-4">
            <p class="text-sm text-gray-600">Total:</p>
            <p id="payment-total" class="text-3xl font-bold text-amber-900">$0</p>
        </div>
        
        <!-- Método de Pago -->
        <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Método de Pago</label>
            <select id="payment-method" class="w-full border border-gray-300 rounded-lg p-2">
                <option value="cash">💵 Efectivo</option>
                <option value="card">💳 Tarjeta</option>
                <option value="transfer">🏦 Transferencia</option>
                <option value="check">📋 Cheque</option>
                <option value="mixed">🔀 Mixto</option>
            </select>
        </div>
        
        <!-- Referencia (para cheque/transferencia) -->
        <div id="reference-section" class="mb-4 hidden">
            <label class="block text-sm font-medium text-gray-700 mb-2">Referencia</label>
            <input type="text" id="payment-reference" 
                   placeholder="Nº cheque, referencia transfer, etc" 
                   class="w-full border border-gray-300 rounded-lg p-2">
        </div>
        
        <!-- Propina -->
        <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Propina</label>
            <div class="flex gap-2">
                <button class="flex-1 border border-gray-300 rounded p-2 hover:bg-gray-50" 
                        onclick="setTip(0)">Sin propina</button>
                <button class="flex-1 border border-gray-300 rounded p-2 hover:bg-gray-50" 
                        onclick="setTip('10%')">10%</button>
                <button class="flex-1 border border-gray-300 rounded p-2 hover:bg-gray-50" 
                        onclick="setTip('15%')">15%</button>
                <button class="flex-1 border border-gray-300 rounded p-2 hover:bg-gray-50" 
                        onclick="setTip('20%')">20%</button>
            </div>
            <input type="number" id="custom-tip" placeholder="Propina personalizada" 
                   class="w-full border border-gray-300 rounded p-2 mt-2">
        </div>
        
        <!-- Botones -->
        <div class="flex gap-2">
            <button onclick="closePaymentModal()" 
                    class="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg">
                Cancelar
            </button>
            <button onclick="confirmPayment()" 
                    class="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                Confirmar Pago
            </button>
        </div>
    </div>
</div>

<script>
// Mostrar referencia solo si es cheque o transferencia
document.getElementById('payment-method').addEventListener('change', (e) => {
    const refSection = document.getElementById('reference-section');
    if (['check', 'transfer'].includes(e.target.value)) {
        refSection.classList.remove('hidden');
    } else {
        refSection.classList.add('hidden');
    }
});

function setTip(amount) {
    if (amount === 0) {
        document.getElementById('custom-tip').value = '0';
    } else if (typeof amount === 'string' && amount.includes('%')) {
        const percent = parseInt(amount);
        const total = parseFloat(document.getElementById('payment-total').textContent.replace('$', ''));
        const tip = (total * percent) / 100;
        document.getElementById('custom-tip').value = tip.toFixed(2);
    }
}

async function confirmPayment() {
    const orderId = document.getElementById('payment-modal').dataset.orderId;
    const method = document.getElementById('payment-method').value;
    const reference = document.getElementById('payment-reference').value;
    const tip = parseFloat(document.getElementById('custom-tip').value) || 0;
    
    try {
        const response = await fetch(`/restaurant/api/orders/${orderId}/payment/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                payment_method: method,
                reference: reference,
                tip_amount: tip
            })
        });
        
        if (response.ok) {
            showToast('Pago registrado correctamente', 'success');
            closePaymentModal();
            // Recargar la lista de pedidos
            location.reload();
        } else {
            showToast('Error al procesar pago', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al procesar pago', 'error');
    }
}
</script>
```

---

## 5. URLs (urls.py)

```python
path('api/orders/<int:pk>/payment/', views.api_process_payment, name='api_process_payment'),
```

---

## 6. Ventajas y Desventajas

### Opción A (Campo en Order):
✅ Más simple
✅ Fácil de implementar
❌ No guarda detalles de pago
❌ No permite auditoría completa

### Opción B (PaymentTransaction):
✅ Historial detallado
✅ Mejor para auditoría
✅ Permite reembolsos futuros
❌ Más complejo
❌ Requiere más migraciones

---

## 7. Próximos Pasos

1. Elegir Opción A o B
2. Crear migraciones
3. Actualizar views
4. Actualizar templates
5. Agregar reportes de métodos de pago
