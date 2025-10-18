# ServiceHub - Recursos Avançados

Guia completo para usar os recursos avançados do ServiceHub.

## 🔔 Notificações em Tempo Real (WebSocket)

### Configuração

1. **Backend**: Já configurado em `servicehub/settings/websocket.py`
2. **Frontend**: Hook `useWebSocket` em `src/hooks/useWebSocket.js`

### Como Usar no Frontend

```javascript
import useWebSocket from '../hooks/useWebSocket';

function MyComponent() {
  const { send, isConnected } = useWebSocket(
    '/ws/notifications/',
    (data) => {
      console.log('Notificação recebida:', data);
      // Atualizar UI com dados
    },
    (error) => {
      console.error('Erro WebSocket:', error);
    }
  );

  return (
    <div>
      Status: {isConnected ? 'Conectado' : 'Desconectado'}
    </div>
  );
}
```

### Tipos de Notificações

```javascript
// Notificação genérica
{
  type: 'notification_message',
  title: 'Novo Orçamento',
  message: 'Um novo orçamento foi criado',
  data: { quote_id: 123 },
  timestamp: '2024-01-01T10:00:00Z'
}

// Atualização de orçamento
{
  type: 'quote_update',
  quote_id: 123,
  status: 'approved',
  message: 'Orçamento aprovado',
  timestamp: '2024-01-01T10:00:00Z'
}

// Atualização de cliente
{
  type: 'client_update',
  client_id: 456,
  action: 'created',
  data: { name: 'João Silva' },
  timestamp: '2024-01-01T10:00:00Z'
}
```

### Enviar Notificação do Backend

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from datetime import datetime

channel_layer = get_channel_layer()

# Enviar para usuário específico
async_to_sync(channel_layer.group_send)(
    f'notifications_{user_id}',
    {
        'type': 'notification_message',
        'title': 'Novo Orçamento',
        'message': 'Um novo orçamento foi criado',
        'data': {'quote_id': quote.id},
        'timestamp': datetime.now().isoformat(),
    }
)
```

## 📊 Relatórios e Dashboards

### Página de Relatórios

Localização: `frontend/src/pages/Reports.jsx`

### Gráficos Disponíveis

1. **Receita ao Longo do Tempo** - LineChart
2. **Distribuição de Status** - PieChart
3. **Top Clientes** - BarChart
4. **Serviços Mais Solicitados** - BarChart

### KPIs Exibidos

- Total de Orçamentos
- Orçamentos Aprovados
- Taxa de Aprovação
- Receita Total

### Exportar Relatório

```javascript
const exportReport = async () => {
  const response = await apiService.get('/analytics/reports/export/', {
    params: {
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      format: 'pdf',
    },
    responseType: 'blob',
  });

  // Download do arquivo
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'report.pdf');
  document.body.appendChild(link);
  link.click();
};
```

## 💬 Integração com WhatsApp (Twilio)

### Configuração

1. Criar conta em https://www.twilio.com
2. Obter credenciais:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_NUMBER`

3. Configurar variáveis de ambiente:

```bash
TWILIO_ACCOUNT_SID=seu-sid
TWILIO_AUTH_TOKEN=seu-token
TWILIO_WHATSAPP_NUMBER=+55-seu-numero
```

### Como Usar

```python
from servicehub.services.whatsapp_service import WhatsAppService

whatsapp = WhatsAppService()

# Enviar notificação de orçamento
whatsapp.send_quote_notification(
    client_phone='11999999999',
    quote_number='ORÇ-001',
    quote_value=1500.00
)

# Enviar notificação de aprovação
whatsapp.send_quote_approval_notification(
    client_phone='11999999999',
    quote_number='ORÇ-001'
)

# Enviar lembrete de pagamento
whatsapp.send_payment_reminder(
    client_phone='11999999999',
    quote_number='ORÇ-001',
    amount=1500.00
)

# Enviar lembrete de agendamento
whatsapp.send_appointment_reminder(
    client_phone='11999999999',
    appointment_date='01/02/2024',
    appointment_time='14:00'
)
```

### Enviar em Massa

```python
whatsapp = WhatsAppService()

phones = ['11999999999', '11988888888', '11977777777']
message = 'Olá! Confira nossos serviços em https://servicehub.com.br'

results = whatsapp.send_bulk_message(phones, message)

for result in results:
    print(f"{result['phone']}: {'✓' if result['success'] else '✗'}")
```

## 💳 Sistema de Pagamento (Stripe/PayPal)

### Configuração Stripe

```bash
STRIPE_PUBLIC_KEY=pk_live_seu-chave
STRIPE_SECRET_KEY=sk_live_seu-chave
```

### Configuração PayPal

```bash
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=seu-client-id
PAYPAL_CLIENT_SECRET=seu-client-secret
```

### Como Usar - Stripe

```python
from servicehub.services.payment_service import StripePaymentService

# Criar intent de pagamento
intent = StripePaymentService.create_payment_intent(
    amount=1500.00,
    currency='brl',
    description='Orçamento #001',
    metadata={'quote_id': 1}
)

# Confirmar pagamento
is_paid = StripePaymentService.confirm_payment(intent.id)

# Criar cliente
customer = StripePaymentService.create_customer(
    email='cliente@example.com',
    name='João Silva'
)

# Criar fatura
invoice = StripePaymentService.create_invoice(
    customer_id=customer.id,
    amount=1500.00,
    description='Orçamento #001'
)

# Fazer reembolso
refund = StripePaymentService.refund_payment(intent.id, amount=1500.00)
```

### Como Usar - PayPal

```python
from servicehub.services.payment_service import PayPalPaymentService

# Criar pagamento
payment = PayPalPaymentService.create_payment(
    amount=1500.00,
    description='Orçamento #001',
    return_url='https://seu-site.com/success',
    cancel_url='https://seu-site.com/cancel'
)

# Executar pagamento
executed = PayPalPaymentService.execute_payment(
    payment_id=payment.id,
    payer_id='payer-id'
)

# Fazer reembolso
refund = PayPalPaymentService.refund_payment(
    sale_id='sale-id',
    amount=1500.00
)
```

### Frontend - Integração Stripe

```javascript
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);

function PaymentForm() {
  const stripe = useStripe();
  const elements = useElements();

  const handlePayment = async (e) => {
    e.preventDefault();

    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement),
    });

    if (!error) {
      // Enviar paymentMethod.id para backend
      const response = await apiService.post('/payments/create/', {
        payment_method_id: paymentMethod.id,
        amount: 1500.00,
      });
    }
  };

  return (
    <form onSubmit={handlePayment}>
      <CardElement />
      <button type="submit">Pagar</button>
    </form>
  );
}

export default function PaymentPage() {
  return (
    <Elements stripe={stripePromise}>
      <PaymentForm />
    </Elements>
  );
}
```

## 📅 Agendamento (Calendar)

### Página de Agendamentos

Localização: `frontend/src/pages/Schedule.jsx`

### Recursos

- Calendário interativo
- Criar agendamentos clicando nas datas
- Editar agendamentos existentes
- Deletar agendamentos
- Listar próximos agendamentos

### Como Usar no Backend

```python
from servicehub.apps.services.models import ServiceOrder

# Criar agendamento
schedule = ServiceOrder.objects.create(
    client_id=1,
    service_id=1,
    title='Manutenção do ar condicionado',
    start_time='2024-02-01 10:00:00',
    end_time='2024-02-01 12:00:00',
    notes='Trazer ferramentas especiais',
    status='scheduled'
)

# Listar agendamentos
schedules = ServiceOrder.objects.filter(
    start_time__gte=datetime.now()
).order_by('start_time')

# Atualizar status
schedule.status = 'completed'
schedule.save()
```

### Enviar Lembrete

```python
from servicehub.services.whatsapp_service import WhatsAppService
from datetime import datetime, timedelta

whatsapp = WhatsAppService()

# Buscar agendamentos de amanhã
tomorrow = datetime.now() + timedelta(days=1)
schedules = ServiceOrder.objects.filter(
    start_time__date=tomorrow.date()
)

# Enviar lembretes
for schedule in schedules:
    whatsapp.send_appointment_reminder(
        client_phone=schedule.client.phone,
        appointment_date=schedule.start_time.strftime('%d/%m/%Y'),
        appointment_time=schedule.start_time.strftime('%H:%M')
    )
```

## 🔄 Fluxo Completo de Exemplo

### 1. Cliente cria orçamento

```
Cliente → Frontend → Backend → Banco de Dados
```

### 2. Notificação em tempo real

```
Backend → WebSocket → Frontend → UI atualizada
```

### 3. Enviar notificação por WhatsApp

```
Backend → Twilio → WhatsApp → Cliente
```

### 4. Cliente aprova orçamento

```
Cliente → Frontend → Backend → Banco de Dados
```

### 5. Agendar serviço

```
Backend → Calendar → Frontend → Agendamento criado
```

### 6. Processar pagamento

```
Cliente → Frontend → Stripe/PayPal → Backend → Banco de Dados
```

### 7. Enviar lembrete

```
Cron Job → Backend → Twilio → WhatsApp → Cliente
```

## 📚 Referências

- [Channels Documentation](https://channels.readthedocs.io/)
- [Recharts Documentation](https://recharts.org/)
- [React Big Calendar](https://jquense.github.io/react-big-calendar/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Stripe API](https://stripe.com/docs/api)
- [PayPal API](https://developer.paypal.com/docs/)

