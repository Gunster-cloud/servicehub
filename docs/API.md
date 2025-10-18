# ServiceHub API Documentation

## Visão Geral

A API do ServiceHub é uma REST API construída com Django REST Framework, fornecendo endpoints para gerenciar clientes, orçamentos, propostas, serviços e análise de dados.

## Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação. Todos os endpoints (exceto login e registro) requerem um token JWT válido.

### Obter Token

**Endpoint:** `POST /api/auth/token/`

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seu_usuario",
    "password": "sua_senha"
  }'
```

**Resposta:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Usar Token

Inclua o token no header `Authorization`:

```bash
curl -H "Authorization: Bearer {access_token}" \
  http://localhost:8000/api/v1/users/
```

### Renovar Token

**Endpoint:** `POST /api/auth/token/refresh/`

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "seu_refresh_token"
  }'
```

## Endpoints

### Usuários

#### Listar Usuários
**GET** `/api/v1/users/`

Parâmetros de query:
- `role`: Filtrar por função (admin, manager, salesperson, technician, client)
- `is_active`: Filtrar por status (true/false)
- `search`: Buscar por username, email, nome
- `ordering`: Ordenar por created_at, first_name

#### Registrar Novo Usuário
**POST** `/api/v1/users/register/`

```json
{
  "username": "novo_usuario",
  "email": "usuario@example.com",
  "password": "senha_segura",
  "password_confirm": "senha_segura",
  "first_name": "João",
  "last_name": "Silva",
  "phone": "11999999999",
  "role": "salesperson"
}
```

#### Obter Usuário Atual
**GET** `/api/v1/users/me/`

#### Alterar Senha
**POST** `/api/v1/users/{id}/change-password/`

```json
{
  "old_password": "senha_atual",
  "new_password": "nova_senha",
  "new_password_confirm": "nova_senha"
}
```

### Clientes

#### Listar Clientes
**GET** `/api/v1/clients/`

Parâmetros:
- `status`: active, inactive, blocked
- `type`: individual, company
- `search`: Buscar por nome, email, documento

#### Criar Cliente
**POST** `/api/v1/clients/`

```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "phone": "11999999999",
  "type": "individual",
  "document": "12345678901",
  "address": "Rua A, 123",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310100",
  "company_name": "Silva Serviços",
  "contact_person": "Maria Silva"
}
```

#### Adicionar Contato ao Cliente
**POST** `/api/v1/clients/{id}/add-contact/`

```json
{
  "name": "Maria Silva",
  "email": "maria@example.com",
  "phone": "11988888888",
  "position": "Gerente",
  "is_primary": true
}
```

### Orçamentos

#### Listar Orçamentos
**GET** `/api/v1/quotes/quotes/`

Parâmetros:
- `status`: draft, sent, viewed, approved, rejected, expired
- `client`: ID do cliente

#### Criar Orçamento
**POST** `/api/v1/quotes/quotes/`

```json
{
  "client": 1,
  "title": "Orçamento de Pintura",
  "description": "Pintura completa da sala",
  "subtotal": 1000.00,
  "discount": 100.00,
  "tax": 180.00,
  "total": 1080.00,
  "valid_until": "2024-12-31",
  "assigned_to": 2,
  "items": [
    {
      "description": "Pintura parede",
      "quantity": 50,
      "unit_price": 20.00,
      "total": 1000.00,
      "order": 1
    }
  ]
}
```

#### Enviar Orçamento
**POST** `/api/v1/quotes/quotes/{id}/send/`

#### Aprovar Orçamento
**POST** `/api/v1/quotes/quotes/{id}/approve/`

### Serviços

#### Listar Serviços
**GET** `/api/v1/services/services/`

#### Criar Serviço
**POST** `/api/v1/services/services/`

```json
{
  "name": "Pintura Residencial",
  "description": "Serviço de pintura para residências",
  "category": "Pintura",
  "base_price": 50.00,
  "unit": "hora"
}
```

#### Listar Pedidos de Serviço
**GET** `/api/v1/services/orders/`

#### Criar Pedido de Serviço
**POST** `/api/v1/services/orders/`

```json
{
  "service": 1,
  "assigned_to": 2,
  "scheduled_date": "2024-12-15T10:00:00Z",
  "notes": "Cliente solicitou manhã"
}
```

### Análise

#### Listar Métricas de Vendas
**GET** `/api/v1/analytics/metrics/`

#### Listar Atividades Diárias
**GET** `/api/v1/analytics/activities/`

#### Listar Relatórios
**GET** `/api/v1/analytics/reports/`

#### Criar Relatório
**POST** `/api/v1/analytics/reports/`

```json
{
  "name": "Relatório de Vendas Mensal",
  "report_type": "sales",
  "description": "Vendas do mês de dezembro",
  "data": {
    "total_quotes": 10,
    "approved": 8,
    "revenue": 5000.00
  },
  "period_start": "2024-12-01",
  "period_end": "2024-12-31"
}
```

## Códigos de Status HTTP

- **200 OK**: Requisição bem-sucedida
- **201 Created**: Recurso criado com sucesso
- **204 No Content**: Sucesso sem conteúdo de resposta
- **400 Bad Request**: Erro na requisição
- **401 Unauthorized**: Autenticação necessária
- **403 Forbidden**: Acesso proibido
- **404 Not Found**: Recurso não encontrado
- **500 Internal Server Error**: Erro do servidor

## Tratamento de Erros

Respostas de erro seguem este formato:

```json
{
  "detail": "Mensagem de erro",
  "field_name": ["Erro específico do campo"]
}
```

## Paginação

Endpoints que retornam listas usam paginação com 20 itens por página:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/clients/?page=2",
  "previous": null,
  "results": [...]
}
```

## Documentação Interativa

Acesse a documentação interativa em:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Rate Limiting

- Usuários anônimos: 100 requisições/hora
- Usuários autenticados: 1000 requisições/hora

