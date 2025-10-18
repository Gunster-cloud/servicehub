"""
Management command to seed the database with test data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from servicehub.apps.clients.models import Client, ClientContact
from servicehub.apps.quotes.models import Quote, QuoteItem
from servicehub.apps.services.models import Service, ServiceCategory
from faker import Faker
from decimal import Decimal

User = get_user_model()
fake = Faker('pt_BR')


class Command(BaseCommand):
    help = 'Seed the database with test data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            User.objects.filter(username__startswith='test_').delete()
            Client.all_objects.filter(name__startswith='Cliente').delete()
            Service.objects.all().delete()
        
        self.stdout.write('Seeding database...')
        
        # Create users
        self.stdout.write('Creating users...')
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@servicehub.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        manager = User.objects.create_user(
            username='manager',
            email='manager@servicehub.com',
            password='manager123',
            first_name='Manager',
            last_name='User',
            role='manager'
        )
        
        salesperson = User.objects.create_user(
            username='salesperson',
            email='sales@servicehub.com',
            password='sales123',
            first_name='Sales',
            last_name='Person',
            role='salesperson'
        )
        
        # Create service categories
        self.stdout.write('Creating service categories...')
        categories = []
        for category_name in ['Pintura', 'Encanamento', 'Eletricidade', 'Limpeza']:
            category = ServiceCategory.objects.create(
                name=category_name,
                description=f'Serviços de {category_name}'
            )
            categories.append(category)
        
        # Create services
        self.stdout.write('Creating services...')
        services = []
        service_names = [
            'Pintura Residencial',
            'Pintura Comercial',
            'Reparo de Encanamento',
            'Instalação de Torneira',
            'Reparo Elétrico',
            'Limpeza Profissional'
        ]
        for i, name in enumerate(service_names):
            service = Service.objects.create(
                name=name,
                description=f'Descrição de {name}',
                category=categories[i % len(categories)].name,
                base_price=Decimal(str(50 + (i * 10))),
                unit='hora'
            )
            services.append(service)
        
        # Create clients
        self.stdout.write('Creating clients...')
        for i in range(10):
            client = Client.objects.create(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number()[:20],
                type='individual' if i % 2 == 0 else 'company',
                document=fake.cpf() if i % 2 == 0 else fake.cnpj(),
                address=fake.address(),
                city=fake.city(),
                state=fake.state_abbr(),
                zip_code=fake.postcode()[:10],
                company_name=fake.company() if i % 2 == 1 else '',
                status='active',
                created_by=salesperson,
                assigned_to=salesperson if i % 2 == 0 else manager
            )
            
            # Add contacts
            for j in range(fake.random_int(min=1, max=3)):
                ClientContact.objects.create(
                    client=client,
                    name=fake.name(),
                    email=fake.email(),
                    phone=fake.phone_number()[:20],
                    position=fake.job(),
                    is_primary=j == 0
                )
        
        # Create quotes
        self.stdout.write('Creating quotes...')
        clients = Client.objects.all()[:5]
        for client in clients:
            for i in range(2):
                subtotal = Decimal(str(fake.random_int(min=500, max=5000)))
                discount = subtotal * Decimal('0.1')
                tax = (subtotal - discount) * Decimal('0.15')
                total = subtotal - discount + tax
                
                quote = Quote.objects.create(
                    client=client,
                    title=f'Orçamento {i+1} - {client.name}',
                    description=fake.text(max_nb_chars=200),
                    subtotal=subtotal,
                    discount=discount,
                    tax=tax,
                    total=total,
                    status='draft' if i == 0 else 'sent',
                    created_by=salesperson,
                    assigned_to=salesperson
                )
                
                # Add items
                for j, service in enumerate(services[:3]):
                    quantity = fake.random_int(min=1, max=10)
                    unit_price = service.base_price
                    item_total = quantity * unit_price
                    
                    QuoteItem.objects.create(
                        quote=quote,
                        description=service.name,
                        quantity=quantity,
                        unit_price=unit_price,
                        total=item_total,
                        order=j
                    )
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

