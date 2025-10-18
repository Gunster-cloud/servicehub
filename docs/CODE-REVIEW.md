# ServiceHub - Revisão Completa de Código

Documento com análise completa de todas as funções, modelos e fluxos do ServiceHub.

## 📋 Índice

1. [Modelos de Dados](#modelos-de-dados)
2. [Serviços Backend](#serviços-backend)
3. [Páginas Frontend](#páginas-frontend)
4. [Fluxos de Negócio](#fluxos-de-negócio)
5. [APIs](#apis)

---

## 🗄️ Modelos de Dados

### 1. **User (Usuário)**

**Localização:** `backend/servicehub/apps/users/models.py`

**Campos:**
- `username` - Nome de usuário (herdado de AbstractUser)
- `email` - Email único
- `phone` - Telefone
- `role` - Função (admin, manager, salesperson, technician, client)
- `company_name` - Nome da empresa
- `document` - CPF/CNPJ
- `is_active` - Ativo/Inativo
- `created_at` - Data de criação
- `updated_at` - Data de atualização

**Funções:**
- `get_full_name()` - Retorna nome completo do usuário
- `__str__()` - Representação em string

**Relacionamentos:**
- `profile` - OneToOne com UserProfile
- `clients_created` - Clientes criados pelo usuário
- `assigned_clients` - Clientes atribuídos ao usuário
- `quotes_created` - Orçamentos criados
- `quotes_assigned` - Orçamentos atribuídos
- `service_orders` - Pedidos de serviço atribuídos
- `sales_metrics` - Métricas de vendas
- `daily_activities` - Atividades diárias

---

### 2. **UserProfile (Perfil do Usuário)**

**Localização:** `backend/servicehub/apps/users/models.py`

**Campos:**
- `user` - OneToOne com User
- `bio` - Biografia
- `avatar` - Foto de perfil
- `address` - Endereço
- `city` - Cidade
- `state` - Estado (UF)
- `zip_code` - CEP
- `preferences` - Preferências (JSON)
- `created_at` - Data de criação
- `updated_at` - Data de atualização

**Funções:**
- `__str__()` - Representação em string

---

### 3. **Client (Cliente)**

**Localização:** `backend/servicehub/apps/clients/models.py`

**Campos:**
- `name` - Nome do cliente
- `email` - Email único
- `phone` - Telefone
- `type` - Tipo (individual ou company)
- `document` - CPF/CNPJ único
- `address` - Endereço
- `city` - Cidade
- `state` - Estado
- `zip_code` - CEP
- `company_name` - Nome da empresa
- `contact_person` - Pessoa de contato
- `notes` - Notas
- `status` - Status (active, inactive, blocked)
- `created_by` - Criado por (FK User)
- `assigned_to` - Atribuído a (FK User)
- `last_contact` - Último contato
- `created_at` - Data de criação
- `updated_at` - Data de atualização
- `deleted_at` - Data de exclusão (soft delete)

**Herança:**
- `SoftDeleteModel` - Suporta soft delete
- `AuditModel` - Rastreamento de auditoria

**Funções:**
- `__str__()` - Representação em string

**Índices:**
- email
- document
- status
- deleted_at

**Relacionamentos:**
- `contacts` - Contatos adicionais (OneToMany)
- `quotes` - Orçamentos (OneToMany)

---

### 4. **ClientContact (Contato do Cliente)**

**Localização:** `backend/servicehub/apps/clients/models.py`

**Campos:**
- `client` - FK para Client
- `name` - Nome do contato
- `email` - Email
- `phone` - Telefone
- `position` - Cargo
- `is_primary` - Contato principal
- `created_at` - Data de criação
- `updated_at` - Data de atualização

**Herança:**
- `AuditModel` - Rastreamento de auditoria

---

### 5. **Quote (Orçamento)**

**Localização:** `backend/servicehub/apps/quotes/models.py`

**Campos:**
- `quote_number` - Número único do orçamento
- `client` - FK para Client
- `title` - Título
- `description` - Descrição
- `subtotal` - Subtotal
- `discount` - Desconto
- `tax` - Imposto
- `total` - Total
- `status` - Status (draft, sent, viewed, approved, rejected, expired)
- `valid_until` - Válido até
- `sent_at` - Enviado em
- `viewed_at` - Visualizado em
- `approved_at` - Aprovado em
- `created_by` - Criado por (FK User)
- `assigned_to` - Atribuído a (FK User)
- `created_at` - Data de criação
- `updated_at` - Data de atualização
- `deleted_at` - Data de exclusão (soft delete)

**Herança:**
- `SoftDeleteModel` - Suporta soft delete
- `AuditModel` - Rastreamento de auditoria

**Índices:**
- quote_number
- status
- client
- deleted_at

**Relacionamentos:**
- `items` - Itens do orçamento (OneToMany)
- `proposal` - Proposta (OneToOne)
- `activities` - Atividades (OneToMany)

---

### 6. **QuoteItem (Item do Orçamento)**

**Localização:** `backend/servicehub/apps/quotes/models.py`

**Campos:**
- `quote` - FK para Quote
- `description` - Descrição
- `quantity` - Quantidade
- `unit_price` - Preço unitário
- `total` - Total
- `order` - Ordem de exibição
- `created_at` - Data de criação
- `updated_at` - Data de atualização

**Herança:**
- `AuditModel` - Rastreamento de auditoria

---

### 7. **Proposal (Proposta)**

**Localização:** `backend/servicehub/apps/quotes/models.py`

**Campos:**
- `quote` - OneToOne com Quote
- `proposal_number` - Número único da proposta
- `status` - Status (draft, sent, viewed, accepted, rejected, expired)
- `terms` - Termos e condições
- `payment_terms` - Condições de pagamento
- `warranty` - Garantia
- `sent_at` - Enviado em
- `accepted_at` - Aceito em
- `created_at` - Data de criação
- `updated_at` - Data de atualização
- `deleted_at` - Data de exclusão (soft delete)

**Herança:**
- `SoftDeleteModel` - Suporta soft delete
- `AuditModel` - Rastreamento de auditoria

**Índices:**
- proposal_number
- status
- deleted_at

---

### 8. **Service (Serviço)**

**Localização:** `backend/servicehub/apps/services/models.py`

**Campos:**
- `name` - Nome único
- `description` - Descrição
- `category` - Categoria
- `base_price` - Preço base
- `unit` - Unidade (hora, dia, etc)
- `status` - Status (active, inactive, archived)
- `notes` - Notas
- `created_at` - Data de criação
- `updated_at` - Data de atualização

**Relacionamentos:**
- `orders` - Pedidos de serviço (OneToMany)

---

### 9. **ServiceCategory (Categoria de Serviço)**

**Localização:** `backend/servicehub/apps/services/models.py`

**Campos:**
- `name` - Nome único
- `description` - Descrição
- `icon` - Ícone
- `created_at` - Data de criação
- `updated_at` - Data de atualização

---

### 10. **ServiceOrder (Pedido de Serviço)**

**Localização:** `backend/servicehub/apps/services/models.py`

**Campos:**
- `order_number` - Número único do pedido
- `service` - FK para Service
- `assigned_to` - Atribuído a (FK User)
- `status` - Status (pending, in_progress, completed, cancelled)
- `scheduled_date` - Data agendada
- `completed_date` - Data de conclusão
- `notes` - Notas
- `created_at` - Data de criação
- `updated_at` - Data de atualização

**Relacionamentos:**
- `service` - Serviço (FK)
- `assigned_to` - Usuário responsável (FK)

---

### 11. **SalesMetrics (Métricas de Vendas)**

**Localização:** `backend/servicehub/apps/analytics/models.py`

**Campos:**
- `user` - FK para User
- `total_quotes` - Total de orçamentos
- `approved_quotes` - Orçamentos aprovados
- `rejected_quotes` - Orçamentos rejeitados
- `total_revenue` - Receita total
- `average_quote_value` - Valor médio
- `conversion_rate` - Taxa de conversão
- `period_start` - Início do período
- `period_end` - Fim do período
- `created_at` - Data de criação
- `updated_at` - Data de atualização

---

### 12. **DailyActivity (Atividade Diária)**

**Localização:** `backend/servicehub/apps/analytics/models.py`

**Campos:**
- `user` - FK para User
- `activity_type` - Tipo de atividade
- `description` - Descrição
- `quote` - FK para Quote (opcional)
- `metadata` - Metadados (JSON)
- `created_at` - Data de criação

**Índices:**
- user + created_at
- activity_type

---

### 13. **Report (Relatório)**

**Localização:** `backend/servicehub/apps/analytics/models.py`

**Campos:**
- `name` - Nome
- `report_type` - Tipo (sales, revenue, clients, performance)
- `description` - Descrição
- `data` - Dados (JSON)
- `period_start` - Início do período
- `period_end` - Fim do período
- `created_by` - Criado por (FK User)
- `created_at` - Data de criação

---

## 🔧 Serviços Backend

### 1. **Email Service** (`email_service.py`)

**Funções:**
- `send_welcome_email(user)` - Enviar email de boas-vindas
- `send_quote_notification(quote, client)` - Notificar sobre novo orçamento
- `send_quote_approval_notification(quote, client)` - Notificar aprovação
- `send_quote_rejection_notification(quote, client)` - Notificar rejeição
- `send_payment_reminder(quote, client)` - Lembrete de pagamento
- `send_service_completion_notification(order, client)` - Notificar conclusão de serviço

---

### 2. **WhatsApp Service** (`whatsapp_service.py`)

**Funções:**
- `send_quote_notification(client_phone, quote_number, quote_value)` - Notificar orçamento
- `send_quote_approval_notification(client_phone, quote_number)` - Notificar aprovação
- `send_payment_reminder(client_phone, quote_number, amount)` - Lembrete de pagamento
- `send_appointment_reminder(client_phone, appointment_date, appointment_time)` - Lembrete de agendamento
- `send_bulk_message(phones, message)` - Enviar em massa
- `send_custom_message(phone, message)` - Mensagem customizada

**Integração:** Twilio

---

### 3. **Payment Service** (`payment_service.py`)

**Classes:**
- `StripePaymentService` - Integração com Stripe
- `PayPalPaymentService` - Integração com PayPal
- `MercadoPagoService` - Integração com Mercado Pago
- `PaymentService` - Serviço unificado

**Funções Stripe:**
- `create_payment_intent(amount, currency, description, metadata)` - Criar intent
- `confirm_payment(payment_intent_id)` - Confirmar pagamento
- `create_customer(email, name, metadata)` - Criar cliente
- `create_invoice(customer_id, amount, description, metadata)` - Criar fatura
- `refund_payment(payment_intent_id, amount)` - Reembolso

**Funções PayPal:**
- `create_payment(amount, description, return_url, cancel_url)` - Criar pagamento
- `execute_payment(payment_id, payer_id)` - Executar pagamento
- `refund_payment(sale_id, amount)` - Reembolso

**Funções Mercado Pago:**
- `create_preference(items, payer_info, metadata)` - Criar preferência
- `create_quote_preference(quote, client)` - Preferência para orçamento
- `get_payment(payment_id)` - Obter detalhes
- `cancel_payment(payment_id)` - Cancelar
- `refund_payment(payment_id, amount)` - Reembolso
- `create_subscription(payer_email, plan_id, metadata)` - Criar assinatura
- `get_subscription(subscription_id)` - Obter assinatura
- `cancel_subscription(subscription_id)` - Cancelar assinatura

**Funções Unificadas:**
- `PaymentService.create_payment(amount, method, **kwargs)` - Criar pagamento
- `PaymentService.confirm_payment(payment_id, method)` - Confirmar pagamento
- `PaymentService.refund_payment(payment_id, method, amount)` - Reembolso

---

### 4. **Mercado Pago Service** (`mercadopago_service.py`)

**Métodos:**
- `create_preference()` - Criar preferência de pagamento
- `create_quote_preference()` - Criar para orçamento
- `get_payment()` - Obter pagamento
- `cancel_payment()` - Cancelar pagamento
- `refund_payment()` - Fazer reembolso
- `create_subscription()` - Criar assinatura
- `get_subscription()` - Obter assinatura
- `cancel_subscription()` - Cancelar assinatura
- `verify_webhook()` - Verificar webhook
- `get_payment_methods()` - Listar métodos
- `create_plan()` - Criar plano

---

### 5. **Validators** (`utils/validators.py`)

**Validadores Pydantic:**
- `UserValidator` - Validar usuário
- `ClientValidator` - Validar cliente
- `QuoteValidator` - Validar orçamento
- `ServiceValidator` - Validar serviço

**Validações:**
- Email válido
- Telefone válido
- CPF/CNPJ válido
- Valores monetários válidos
- Datas válidas

---

### 6. **Permissions** (`utils/permissions.py`)

**Permissões Customizadas:**
- `IsOwnerOrAdmin` - Apenas proprietário ou admin
- `IsAssignedOrAdmin` - Apenas atribuído ou admin
- `IsClientOwner` - Apenas proprietário do cliente
- `IsQuoteOwner` - Apenas proprietário do orçamento

---

### 7. **Filters** (`utils/filters.py`)

**Filtros:**
- `ClientFilter` - Filtrar clientes por nome, email, status, tipo
- `QuoteFilter` - Filtrar orçamentos por status, data, valor, cliente
- `ServiceFilter` - Filtrar serviços por categoria, status, preço
- `ServiceOrderFilter` - Filtrar pedidos por status, data, serviço

---

### 8. **Audit** (`utils/audit.py`)

**Funcionalidades:**
- `AuditLog` - Modelo para rastreamento
- `AuditMixin` - Mixin para adicionar auditoria
- `@audit_action` - Decorador para rastrear ações
- Registra: usuário, ação, valores antigos/novos, IP, user-agent

---

### 9. **Signals** (`utils/signals.py`)

**Signals:**
- `generate_quote_number()` - Gerar número de orçamento automaticamente
- `generate_proposal_number()` - Gerar número de proposta
- `generate_service_order_number()` - Gerar número de pedido
- `update_sales_metrics()` - Atualizar métricas de vendas
- `log_activity()` - Registrar atividade

---

## 🎨 Páginas Frontend

### 1. **Login** (`pages/Login.jsx`)

**Componentes:**
- Card de login
- Campo de email
- Campo de senha
- Botão de login
- Link de recuperação de senha

**Funcionalidades:**
- Validação de formulário
- Tratamento de erros
- Redirecionamento após login

---

### 2. **Dashboard** (`pages/Dashboard.jsx`)

**Componentes:**
- Cards de KPIs
- Gráficos de vendas
- Atividades recentes
- Próximos agendamentos

**Dados Exibidos:**
- Total de orçamentos
- Taxa de aprovação
- Receita total
- Clientes ativos

---

### 3. **Clients** (`pages/Clients.jsx`)

**Funcionalidades:**
- Listar clientes em tabela
- Criar novo cliente
- Editar cliente
- Deletar cliente
- Filtrar por status, tipo, nome
- Buscar por email

**Campos:**
- Nome
- Email
- Telefone
- Tipo (individual/company)
- CPF/CNPJ
- Endereço
- Cidade
- Estado
- CEP
- Status

---

### 4. **Quotes** (`pages/Quotes.jsx`)

**Funcionalidades:**
- Listar orçamentos em tabela
- Criar novo orçamento
- Editar orçamento
- Deletar orçamento
- Filtrar por status, cliente, data
- Buscar por número

**Campos:**
- Número do orçamento
- Cliente
- Título
- Descrição
- Valor total
- Status
- Data de validade

---

### 5. **Services** (`pages/Services.jsx`)

**Funcionalidades:**
- Listar serviços em tabela
- Criar novo serviço
- Editar serviço
- Deletar serviço
- Filtrar por categoria, status

**Campos:**
- Nome
- Categoria
- Descrição
- Preço base
- Unidade
- Status

---

### 6. **Reports** (`pages/Reports.jsx`)

**Gráficos:**
- LineChart - Receita ao longo do tempo
- PieChart - Distribuição de status
- BarChart - Top clientes
- BarChart - Serviços mais solicitados

**KPIs:**
- Total de orçamentos
- Orçamentos aprovados
- Taxa de aprovação
- Receita total

**Filtros:**
- Data inicial
- Data final

---

### 7. **Schedule** (`pages/Schedule.jsx`)

**Componentes:**
- Calendário interativo (React Big Calendar)
- Dialog para criar/editar agendamentos
- Lista de próximos agendamentos

**Funcionalidades:**
- Criar agendamento
- Editar agendamento
- Deletar agendamento
- Visualizar calendário
- Status colorido

---

### 8. **Payment** (`pages/Payment.jsx`)

**Componentes:**
- Resumo do orçamento
- Seleção de método de pagamento
- Botões de pagamento

**Métodos Suportados:**
- Mercado Pago
- Stripe
- PayPal

---

## 🔄 Fluxos de Negócio

### 1. **Fluxo de Criação de Orçamento**

```
1. Usuário acessa página de Orçamentos
   ↓
2. Clica em "Novo Orçamento"
   ↓
3. Preenche formulário (cliente, itens, valores)
   ↓
4. Salva orçamento (status: draft)
   ↓
5. Sistema gera número automaticamente
   ↓
6. Usuário pode editar ou enviar
   ↓
7. Ao enviar:
   - Status muda para "sent"
   - Email é enviado ao cliente
   - WhatsApp é enviado (opcional)
   - Atividade é registrada
   ↓
8. Cliente recebe e pode visualizar
   ↓
9. Cliente aprova ou rejeita
   ↓
10. Usuário recebe notificação em tempo real (WebSocket)
```

---

### 2. **Fluxo de Pagamento**

```
1. Orçamento aprovado
   ↓
2. Usuário acessa página de Pagamento
   ↓
3. Seleciona método (Mercado Pago, Stripe, PayPal)
   ↓
4. Clica em "Pagar"
   ↓
5. Sistema cria preferência/intent
   ↓
6. Cliente é redirecionado para gateway
   ↓
7. Cliente completa pagamento
   ↓
8. Gateway redireciona de volta
   ↓
9. Sistema recebe webhook
   ↓
10. Orçamento é marcado como pago
   ↓
11. Email de confirmação é enviado
   ↓
12. Notificação em tempo real (WebSocket)
```

---

### 3. **Fluxo de Agendamento**

```
1. Orçamento pago
   ↓
2. Usuário acessa página de Agendamentos
   ↓
3. Clica em data no calendário
   ↓
4. Preenche dados do agendamento
   ↓
5. Seleciona cliente e serviço
   ↓
6. Salva agendamento
   ↓
7. Sistema gera número automaticamente
   ↓
8. Lembrete é agendado
   ↓
9. 24h antes: WhatsApp é enviado ao cliente
   ↓
10. Data do agendamento: Serviço é executado
   ↓
11. Usuário marca como concluído
   ↓
12. Email de conclusão é enviado
```

---

### 4. **Fluxo de Notificação em Tempo Real**

```
1. Usuário abre Dashboard
   ↓
2. WebSocket se conecta ao servidor
   ↓
3. Servidor envia notificações quando:
   - Novo orçamento é criado
   - Orçamento é aprovado/rejeitado
   - Pagamento é recebido
   - Agendamento é criado
   ↓
4. Frontend recebe notificação
   ↓
5. UI é atualizada em tempo real
   ↓
6. Notificação visual é exibida
```

---

### 5. **Fluxo de Relatórios**

```
1. Usuário acessa página de Relatórios
   ↓
2. Seleciona período (data inicial e final)
   ↓
3. Sistema calcula métricas:
   - Total de orçamentos
   - Orçamentos aprovados
   - Taxa de aprovação
   - Receita total
   ↓
4. Gráficos são exibidos:
   - Receita ao longo do tempo
   - Distribuição de status
   - Top clientes
   - Serviços mais solicitados
   ↓
5. Usuário pode exportar em PDF
```

---

## 🔌 APIs

### Endpoints de Usuários

```
GET    /api/v1/users/                    - Listar usuários
POST   /api/v1/users/                    - Criar usuário
GET    /api/v1/users/{id}/               - Obter usuário
PUT    /api/v1/users/{id}/               - Atualizar usuário
DELETE /api/v1/users/{id}/               - Deletar usuário
GET    /api/v1/users/me/                 - Obter usuário atual
```

### Endpoints de Clientes

```
GET    /api/v1/clients/                  - Listar clientes
POST   /api/v1/clients/                  - Criar cliente
GET    /api/v1/clients/{id}/             - Obter cliente
PUT    /api/v1/clients/{id}/             - Atualizar cliente
DELETE /api/v1/clients/{id}/             - Deletar cliente
GET    /api/v1/clients/{id}/contacts/    - Listar contatos
POST   /api/v1/clients/{id}/contacts/    - Criar contato
```

### Endpoints de Orçamentos

```
GET    /api/v1/quotes/                   - Listar orçamentos
POST   /api/v1/quotes/                   - Criar orçamento
GET    /api/v1/quotes/{id}/              - Obter orçamento
PUT    /api/v1/quotes/{id}/              - Atualizar orçamento
DELETE /api/v1/quotes/{id}/              - Deletar orçamento
POST   /api/v1/quotes/{id}/send/         - Enviar orçamento
POST   /api/v1/quotes/{id}/approve/      - Aprovar orçamento
POST   /api/v1/quotes/{id}/reject/       - Rejeitar orçamento
GET    /api/v1/quotes/{id}/items/        - Listar itens
POST   /api/v1/quotes/{id}/items/        - Criar item
```

### Endpoints de Serviços

```
GET    /api/v1/services/                 - Listar serviços
POST   /api/v1/services/                 - Criar serviço
GET    /api/v1/services/{id}/            - Obter serviço
PUT    /api/v1/services/{id}/            - Atualizar serviço
DELETE /api/v1/services/{id}/            - Deletar serviço
GET    /api/v1/services/categories/      - Listar categorias
POST   /api/v1/services/categories/      - Criar categoria
GET    /api/v1/services/orders/          - Listar pedidos
POST   /api/v1/services/orders/          - Criar pedido
```

### Endpoints de Pagamentos

```
POST   /api/v1/payments/stripe/          - Criar pagamento Stripe
POST   /api/v1/payments/paypal/          - Criar pagamento PayPal
POST   /api/v1/payments/mercadopago/     - Criar pagamento Mercado Pago
GET    /api/v1/payments/{id}/status/     - Obter status do pagamento
POST   /api/v1/payments/{id}/refund/     - Fazer reembolso
POST   /api/v1/payments/webhook/         - Receber webhook
```

### Endpoints de Analytics

```
GET    /api/v1/analytics/metrics/        - Obter métricas
GET    /api/v1/analytics/activities/     - Listar atividades
GET    /api/v1/analytics/reports/        - Listar relatórios
POST   /api/v1/analytics/reports/        - Criar relatório
GET    /api/v1/analytics/reports/export/ - Exportar relatório
```

---

## 📊 Resumo de Funcionalidades

### Backend
- ✅ 5 aplicações Django (users, clients, quotes, services, analytics)
- ✅ Autenticação JWT
- ✅ Soft deletes
- ✅ Auditoria completa
- ✅ Validações Pydantic
- ✅ Permissões granulares
- ✅ Filtros avançados
- ✅ 4 métodos de pagamento (Stripe, PayPal, Mercado Pago, integração unificada)
- ✅ Email (SMTP)
- ✅ WhatsApp (Twilio)
- ✅ WebSocket (Channels)
- ✅ Testes unitários (pytest)
- ✅ Seed de dados

### Frontend
- ✅ 8 páginas principais
- ✅ Autenticação JWT
- ✅ Rotas protegidas
- ✅ Componentes Material-UI
- ✅ Gráficos (Recharts)
- ✅ Calendário (React Big Calendar)
- ✅ Formulários com validação
- ✅ Integração com 3 gateways de pagamento
- ✅ WebSocket para notificações em tempo real
- ✅ Responsivo

### Infraestrutura
- ✅ Docker Compose para produção
- ✅ PostgreSQL
- ✅ Redis
- ✅ Nginx
- ✅ Gunicorn
- ✅ Celery
- ✅ SSL/TLS ready
- ✅ Backups automáticos
- ✅ CI/CD (GitHub Actions)
- ✅ Monitoramento (Sentry)

---

## 🎯 Total de Funcionalidades

- **14 Modelos de Dados**
- **9 Serviços Backend**
- **8 Páginas Frontend**
- **5 Fluxos de Negócio Principais**
- **30+ Endpoints de API**
- **100+ Funções/Métodos**
- **Pronto para Produção**


