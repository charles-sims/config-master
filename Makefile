# ConfigMaster Makefile

.PHONY: help install dev build test clean deploy

# Default target
help:
	@echo "ConfigMaster - Configuration Management Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start development environment"
	@echo "  make build      - Build all containers"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run linting and formatting"
	@echo "  make deploy     - Deploy to staging environment"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make docs       - Generate documentation"
	@echo "  make monitor    - Start monitoring stack"

# Install dependencies
install:
	@echo "Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cd discovery && pip install -r requirements.txt

# Development environment
dev:
	@echo "Starting development environment..."
	docker-compose up --build

# Build containers
build:
	@echo "Building containers..."
	docker-compose build

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test
	@echo "Running discovery tests..."
	cd discovery && python -m pytest tests/ -v

# Linting and formatting
lint:
	@echo "Running backend linting..."
	cd backend && black . && flake8 .
	@echo "Running frontend linting..."
	cd frontend && npm run lint
	@echo "Running discovery linting..."
	cd discovery && black . && flake8 .

# Type checking
type-check:
	@echo "Running type checks..."
	cd frontend && npm run type-check

# Clean up
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f

# Generate documentation
docs:
	@echo "Generating documentation..."
	cd backend && python -c "from documentation.generator import DocumentationGenerator; gen = DocumentationGenerator(); print('Documentation templates created')"

# Start monitoring stack
monitor:
	@echo "Starting monitoring stack..."
	docker-compose up -d prometheus grafana

# Database operations
db-init:
	@echo "Initializing database..."
	cd backend && alembic upgrade head

db-migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	docker-compose stop postgres
	docker-compose rm -f postgres
	docker volume rm config-master_postgres_data
	docker-compose up -d postgres
	sleep 10
	make db-init

# Discovery operations
discover:
	@echo "Running discovery scan..."
	cd discovery && python discover.py scan --verbose

# Compliance check
compliance:
	@echo "Running compliance checks..."
	curl -X POST http://localhost:8000/discovery/scan

# Terraform operations
tf-init:
	@echo "Initializing Terraform..."
	cd infrastructure/terraform && terraform init

tf-plan:
	@echo "Planning Terraform deployment..."
	cd infrastructure/terraform && terraform plan

tf-apply:
	@echo "Applying Terraform configuration..."
	cd infrastructure/terraform && terraform apply

tf-destroy:
	@echo "Destroying Terraform infrastructure..."
	cd infrastructure/terraform && terraform destroy

# Kubernetes operations
k8s-deploy:
	@echo "Deploying to Kubernetes..."
	kubectl apply -f infrastructure/kubernetes/

k8s-status:
	@echo "Checking Kubernetes status..."
	kubectl get pods -n configmaster
	kubectl get services -n configmaster

# Development helpers
logs:
	@echo "Showing logs..."
	docker-compose logs -f

logs-backend:
	@echo "Showing backend logs..."
	docker-compose logs -f backend

logs-frontend:
	@echo "Showing frontend logs..."
	docker-compose logs -f frontend

logs-discovery:
	@echo "Showing discovery logs..."
	docker-compose logs -f discovery

# Health checks
health:
	@echo "Checking application health..."
	curl -s http://localhost:8000/health | jq .
	curl -s http://localhost:8000/statistics | jq .

# Backup operations
backup:
	@echo "Creating backup..."
	docker exec $$(docker-compose ps -q postgres) pg_dump -U configmaster configmaster > backup_$$(date +%Y%m%d_%H%M%S).sql

# Load test data
load-sample-data:
	@echo "Loading sample data..."
	cd backend && python scripts/load_sample_data.py

# Security scan
security-scan:
	@echo "Running security scan..."
	docker run --rm -v $$(pwd):/src aquasec/trivy fs /src

# Performance test
perf-test:
	@echo "Running performance tests..."
	cd tests && artillery run load-test.yml

# Release operations
tag-release:
	@echo "Tagging release..."
	git tag -a v$$(cat VERSION) -m "Release v$$(cat VERSION)"
	git push origin v$$(cat VERSION)

# Environment setup
setup-dev:
	@echo "Setting up development environment..."
	cp .env.example .env
	make install
	make build
	make db-init
	make discover

# CI/CD helpers
ci-test:
	@echo "Running CI tests..."
	make test
	make lint
	make type-check
	make security-scan

# Quick start
quick-start: setup-dev
	@echo "Starting ConfigMaster..."
	make dev