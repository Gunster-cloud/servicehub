# ServiceHub - Integração Mercado Pago

Guia completo para integração com Mercado Pago.

## 📋 Pré-requisitos

1. Conta no Mercado Pago: https://www.mercadopago.com.br
2. Credenciais de acesso (Access Token)

## 🔑 Configuração

### 1. Obter Credenciais

1. Acesse https://www.mercadopago.com.br/developers
2. Faça login com sua conta
3. Vá para "Credenciais"
4. Copie o **Access Token** (Produção)

### 2. Configurar Variáveis de Ambiente

```bash
# .env.prod
MERCADOPAGO_ACCESS_TOKEN=seu-access-token
MERCADOPAGO_PUBLIC_KEY=sua-chave-publica
```

### 3. Instalar Dependência

```bash
pip install mercado-pago==2.0.0
```

## 🚀 Como Usar

### Backend - Criar Preferência de Pagamento

```python
from servicehub.services.mercadopago_service import MercadoPagoService

mp = MercadoPagoService()

# Criar preferência para orçamento
preference = mp.create_quote_preference(quote, client)

# Redirecionar para Mercado Pago
# preference['init_point'] contém a URL de checkout
```

### Backend - Verificar Status de Pagamento

```python
from servicehub.services.mercadopago_service import MercadoPagoService

mp = MercadoPagoService()

# Obter detalhes do pagamento
payment = mp.get_payment(payment_id)

# Verificar se foi aprovado
if payment['status'] == 'approved':
    # Pagamento aprovado
    pass
```

### Backend - Fazer Reembolso

```python
from servicehub.services.mercadopago_service import MercadoPagoService

mp = MercadoPagoService()

# Reembolso total
refund = mp.refund_payment(payment_id)

# Reembolso parcial
refund = mp.refund_payment(payment_id, amount=500.00)
```

### Frontend - Usar Componente de Pagamento

```javascript
import MercadoPagoButton from '../components/MercadoPagoButton';

function QuoteDetail() {
  const quote = { id: 1, total_value: 1500.00, client: { id: 1 } };

  return (
    <MercadoPagoButton
      amount={quote.total_value}
      quoteId={quote.id}
      clientId={quote.client.id}
      onSuccess={() => {
        console.log('Pagamento realizado com sucesso!');
      }}
      onError={(error) => {
        console.error('Erro no pagamento:', error);
      }}
    />
  );
}
```

### Frontend - Página de Pagamento

```javascript
import Payment from '../pages/Payment';

// Adicionar rota
<Route path="/payments/:quoteId" element={<Payment />} />
```

## 🔔 Webhooks

### Configurar Webhook no Mercado Pago

1. Acesse https://www.mercadopago.com.br/developers/panel
2. Vá para "Webhooks"
3. Adicione URL: `https://seu-dominio.com/api/v1/payments/mercadopago/webhook/`
4. Selecione eventos:
   - `payment.created`
   - `payment.updated`

### Processar Webhook no Backend

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from servicehub.services.mercadopago_service import MercadoPagoService
import json

@require_http_methods(["POST"])
def mercadopago_webhook(request):
    try:
        data = json.loads(request.body)
        
        # Verificar tipo de evento
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            # Obter detalhes do pagamento
            mp = MercadoPagoService()
            payment = mp.get_payment(payment_id)
            
            if payment['status'] == 'approved':
                # Atualizar orçamento como pago
                quote_id = payment['metadata']['quote_id']
                quote = Quote.objects.get(id=quote_id)
                quote.status = 'paid'
                quote.save()
                
                # Enviar confirmação
                send_payment_confirmation_email(quote)
        
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f'Webhook error: {str(e)}')
        return JsonResponse({'status': 'error'}, status=400)
```

## 💳 Tipos de Pagamento Suportados

- Cartão de crédito
- Cartão de débito
- Boleto
- Pix
- Dinheiro (Mercado Crédito)

## 📊 Status de Pagamento

| Status | Descrição |
|--------|-----------|
| `pending` | Pendente de processamento |
| `approved` | Pagamento aprovado |
| `authorized` | Autorizado, aguardando captura |
| `in_process` | Em processamento |
| `in_mediation` | Em mediação |
| `rejected` | Pagamento rejeitado |
| `cancelled` | Pagamento cancelado |
| `refunded` | Pagamento reembolsado |
| `charged_back` | Chargeback |

## 🔄 Fluxo Completo

```
1. Cliente clica em "Pagar com Mercado Pago"
   ↓
2. Sistema cria preferência de pagamento
   ↓
3. Cliente é redirecionado para Mercado Pago
   ↓
4. Cliente completa o pagamento
   ↓
5. Mercado Pago redireciona de volta
   ↓
6. Sistema recebe webhook de confirmação
   ↓
7. Orçamento é marcado como pago
   ↓
8. Email de confirmação é enviado
```

## 🛡️ Segurança

### Validação de Webhook

```python
import hmac
import hashlib

def verify_mercadopago_webhook(request):
    # Obter assinatura do header
    signature = request.headers.get('X-Signature')
    
    # Obter timestamp do header
    timestamp = request.headers.get('X-Timestamp')
    
    # Obter dados do request
    data = request.body
    
    # Criar string para assinar
    to_sign = f"{timestamp}:{data}"
    
    # Assinar com secret
    secret = settings.MERCADOPAGO_WEBHOOK_SECRET
    signed = hmac.new(
        secret.encode(),
        to_sign.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Comparar assinaturas
    return hmac.compare_digest(signed, signature)
```

## 📱 Teste com Cartões

### Cartões de Teste

| Tipo | Número | CVV | Vencimento |
|------|--------|-----|-----------|
| Visa | 4111 1111 1111 1111 | 123 | 11/25 |
| Mastercard | 5555 5555 5555 4444 | 123 | 11/25 |
| Amex | 3782 822463 10005 | 1234 | 11/25 |

### CPF de Teste

- `12345678900` (Pessoa Física)
- `12345678901234` (Pessoa Jurídica)

## 🐛 Troubleshooting

### Erro: "Access Token inválido"

```
Solução: Verifique se o token está correto em .env.prod
```

### Erro: "Preferência não criada"

```
Solução: Verifique se os itens estão formatados corretamente
```

### Webhook não recebido

```
Solução: Verifique se a URL do webhook está acessível publicamente
```

## 📚 Referências

- [Documentação Mercado Pago](https://www.mercadopago.com.br/developers/pt/docs)
- [SDK Python](https://github.com/mercadopago/sdk-python)
- [Integração de Preferências](https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/integrate-preference)
- [Webhooks](https://www.mercadopago.com.br/developers/pt/docs/notifications/webhooks)

## 💡 Dicas

1. **Teste em sandbox primeiro** - Use credenciais de teste antes de produção
2. **Implemente retry logic** - Webhooks podem ser reenviados
3. **Valide assinatura** - Sempre valide webhooks recebidos
4. **Log de transações** - Mantenha registro de todas as transações
5. **Tratamento de erros** - Implemente fallback para falhas de pagamento

## 🎯 Próximos Passos

1. Testar pagamentos em sandbox
2. Configurar webhooks
3. Implementar lógica de reembolso
4. Adicionar notificações por email
5. Implementar relatórios de pagamento

