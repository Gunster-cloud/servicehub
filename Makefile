.PHONY: help build up down logs shell migrate createsuperuser clean

help:
	@echo "ServiceHub Docker Commands"
	@echo "=========================="
	@echo "make build              - Build Docker images"
	@echo "make up                 - Start all services"
	@echo "make down               - Stop all services"
	@echo "make logs               - View logs from all services"
	@echo "make logs-backend       - View backend logs"
	@echo "make logs-frontend      - View frontend logs"
	@echo "make shell              - Open Django shell"
	@echo "make migrate            - Run database migrations"
	@echo "make createsuperuser    - Create superuser"
	@echo "make clean              - Remove all containers and volumes"
	@echo "make test               - Run tests"
	@echo "make lint               - Run linting"

build:
	docker-compose -f docker-compose.prod.yml build

up:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "ServiceHub is starting... Access at http://localhost"

down:
	docker-compose -f docker-compose.prod.yml down

logs:
	docker-compose -f docker-compose.prod.yml logs -f

logs-backend:
	docker-compose -f docker-compose.prod.yml logs -f backend

logs-frontend:
	docker-compose -f docker-compose.prod.yml logs -f frontend

shell:
	docker-compose -f docker-compose.prod.yml exec backend python manage.py shell

migrate:
	docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

createsuperuser:
	docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

test:
	docker-compose -f docker-compose.prod.yml exec backend pytest

lint:
	docker-compose -f docker-compose.prod.yml exec backend flake8 servicehub

clean:
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f

restart:
	docker-compose -f docker-compose.prod.yml restart

ps:
	docker-compose -f docker-compose.prod.yml ps

health:
	@echo "Checking service health..."
	@curl -s http://localhost/health || echo "API not responding"
	@echo ""

