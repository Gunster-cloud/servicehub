# Guia de Testes - ServiceHub

## Visão Geral

ServiceHub utiliza **pytest** com **pytest-django** para testes automatizados, garantindo qualidade e confiabilidade do código.

## Configuração

### Instalação

As dependências de teste já estão incluídas em `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Arquivo de Configuração

O arquivo `pytest.ini` define as configurações padrão:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --cov=servicehub --cov-report=html
```

## Executando Testes

### Todos os testes

```bash
pytest
```

### Testes de um app específico

```bash
pytest servicehub/apps/users/
```

### Testes de um arquivo específico

```bash
pytest servicehub/apps/clients/tests.py
```

### Testes de uma classe específica

```bash
pytest servicehub/apps/clients/tests.py::TestClientModel
```

### Testes de um método específico

```bash
pytest servicehub/apps/clients/tests.py::TestClientModel::test_create_client
```

### Com cobertura de código

```bash
pytest --cov=servicehub --cov-report=html
```

Após executar, abra `htmlcov/index.html` no navegador para ver o relatório detalhado.

### Testes em paralelo

```bash
pytest -n auto
```

### Apenas testes rápidos

```bash
pytest -m "not slow"
```

## Estrutura de Testes

### Exemplo de Teste de Model

```python
import pytest
from django.contrib.auth import get_user_model
from servicehub.apps.clients.models import Client

User = get_user_model()

@pytest.mark.django_db
class TestClientModel:
    """Tests for Client model."""
    
    def setup_method(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_client(self):
        """Test creating a client."""
        client = Client.objects.create(
            name='John Doe',
            email='john@example.com',
            phone='11999999999',
            type='individual',
            document='12345678901',
            created_by=self.user
        )
        assert client.name == 'John Doe'
        assert not client.is_deleted
```

### Exemplo de Teste de API

```python
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestClientAPI:
    """Tests for Client API."""
    
    def setup_method(self):
        """Setup test client and users."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_client(self):
        """Test creating a client via API."""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Test Client',
            'email': 'test@client.com',
            'phone': '11999999999',
            'type': 'individual',
            'document': '12345678901'
        }
        response = self.client.post('/api/v1/clients/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Client'
```

## Fixtures

Fixtures reutilizáveis estão definidas em `conftest.py`:

### Usuário Padrão

```python
def test_something(user):
    """Test with default user."""
    assert user.username == 'testuser'
```

### Usuário Admin

```python
def test_admin_action(admin_user):
    """Test with admin user."""
    assert admin_user.is_superuser
```

### Usuário Vendedor

```python
def test_sales_action(salesperson_user):
    """Test with salesperson user."""
    assert salesperson_user.role == 'salesperson'
```

## Seeding de Dados

Para popular o banco com dados de teste:

```bash
python manage.py seed_data
```

Para limpar e recriar:

```bash
python manage.py seed_data --clear
```

Isso cria:
- 3 usuários (admin, manager, salesperson)
- 4 categorias de serviço
- 6 serviços
- 10 clientes com contatos
- 10 orçamentos com itens

## Boas Práticas

### 1. Use `@pytest.mark.django_db`

Sempre marque testes que usam banco de dados:

```python
@pytest.mark.django_db
def test_something():
    Model.objects.create(...)
```

### 2. Organize em Classes

Agrupe testes relacionados em classes:

```python
class TestClientModel:
    """Tests for Client model."""
    
    def test_create(self):
        ...
    
    def test_update(self):
        ...
```

### 3. Use `setup_method`

Prepare dados antes de cada teste:

```python
def setup_method(self):
    self.user = User.objects.create_user(...)
```

### 4. Nomes Descritivos

Use nomes que descrevam o que está sendo testado:

```python
def test_create_client_with_valid_data(self):
    ...

def test_create_client_with_invalid_email(self):
    ...
```

### 5. Teste Comportamentos

Teste o comportamento, não a implementação:

```python
# ✅ Bom
def test_soft_delete_removes_from_queryset(self):
    client = Client.objects.create(...)
    client.delete()
    assert Client.objects.filter(id=client.id).count() == 0

# ❌ Ruim
def test_deleted_at_is_set(self):
    client = Client.objects.create(...)
    client.delete()
    assert client.deleted_at is not None
```

### 6. Teste Casos Extremos

```python
def test_create_client_with_empty_name(self):
    with pytest.raises(ValidationError):
        Client.objects.create(name='', ...)

def test_create_client_with_duplicate_email(self):
    Client.objects.create(email='test@example.com', ...)
    with pytest.raises(IntegrityError):
        Client.objects.create(email='test@example.com', ...)
```

## Cobertura de Código

### Gerar Relatório

```bash
pytest --cov=servicehub --cov-report=html --cov-report=term-missing
```

### Metas de Cobertura

- **Models**: 90%+
- **Views/Serializers**: 85%+
- **Utils**: 80%+
- **Overall**: 85%+

## CI/CD

### GitHub Actions

Exemplo de workflow para testes automáticos:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: servicehub_test
          POSTGRES_USER: servicehub
          POSTGRES_PASSWORD: servicehub
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=servicehub
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Erro: "No such table"

Certifique-se de que as migrações foram executadas:

```bash
python manage.py migrate
```

### Erro: "Database is locked"

Use SQLite em memória para testes:

```python
# settings.py
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
```

### Testes Lentos

Use `pytest-xdist` para paralelização:

```bash
pytest -n auto
```

## Recursos Adicionais

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Django](https://pytest-django.readthedocs.io/)
- [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)

