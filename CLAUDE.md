# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ConfigMaster is a comprehensive configuration discovery, management, and recommendation platform for innovation studios. It features automated application discovery, AI-powered platform analysis, organizational technology maturity assessment, and intelligent integration recommendations.

## Development Commands

### Backend (Flask/FastAPI)
```bash
# Start Flask development server (currently running)
cd backend && source venv/bin/activate && python flask_server.py

# Start FastAPI server (alternative)
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Initialize database
make db-init

# Run backend tests
cd backend && python -m pytest tests/ -v

# Backend linting
cd backend && black . && flake8 .
```

### Frontend (Next.js)
```bash
# Start development server (currently running)
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Type checking
cd frontend && npm run type-check

# Linting
cd frontend && npm run lint
```

### Discovery System
```bash
# Run full discovery scan
cd discovery && python discover.py scan --verbose

# Run AI-powered platform scanner demo
python ai_scanner_demo.py

# Install discovery dependencies
cd discovery && pip install -r requirements.txt
```

### Maturity Framework
```bash
# Run maturity assessment demo
python maturity_assessment_demo.py

# Generate technology periodic table
python technology_periodic_table.py
```

### Make Commands
```bash
# Full development setup
make setup-dev

# Start full development environment (Docker)
make dev

# Run all tests and linting
make ci-test

# Database operations
make db-init        # Initialize database
make db-migrate     # Run migrations
make db-reset       # Reset database completely

# Discovery operations
make discover       # Run discovery scan
make compliance     # Run compliance checks
```

## Architecture Overview

### Multi-Service Architecture
- **Backend**: Flask/FastAPI APIs (currently Flask on port 8000)
- **Frontend**: Next.js dashboard (port 3000)
- **Discovery**: Python-based scanner system
- **Database**: SQLite (development), PostgreSQL (production)
- **AI Services**: LangChain, OpenAI, Exa.ai, Playwright, Firecrawl

### Key Components

#### Backend (`/backend/`)
- **Flask Server**: `flask_server.py` - Main API server (currently running)
- **FastAPI Alternative**: `main.py` - Feature-complete FastAPI implementation
- **Maturity Framework**: `maturity_framework.py` - COTMF implementation
- **AI Recommendations**: `recommendation_engine.py` - Integration analysis
- **Database Models**: `database/models.py` - SQLAlchemy ORM models
- **Compliance Engine**: `compliance/rules.py` - Configuration validation

#### Discovery System (`/discovery/`)
- **AI Platform Scanner**: `scanners/ai_platform_scanner.py` - LangChain-powered analysis
- **Infrastructure Scanners**: Docker, Kubernetes, process discovery
- **Base Scanner**: `scanners/base.py` - Common scanner interface

#### Frontend (`/frontend/`)
- **Next.js 14**: TypeScript, Tailwind CSS, React Query
- **Component Library**: Headless UI, Heroicons, Lucide React
- **Charts**: Recharts for data visualization

### Database Schema

#### Core Tables
- **applications**: Main application registry
- **configurations**: Application configuration key-value pairs
- **integrations**: Application integration mappings
- **compliance_issues**: Compliance validation results

#### AI-Enhanced Tables (from AI scanner)
- **platform_capabilities**: AI-discovered platform features
- **integration_recommendations**: AI-generated integration suggestions
- **platform_analyses**: Comprehensive platform analysis results
- **configuration_options**: AI-discovered configuration options

### AI Enhancement System

#### Multi-Stage AI Analysis Pipeline
1. **Exa.ai Search**: Neural search for technical documentation
2. **Firecrawl Extraction**: Structured content extraction from docs
3. **Playwright Exploration**: Interactive platform exploration
4. **LLM Analysis**: OpenAI GPT-4 for analysis and structuring

#### Required API Keys
```bash
export OPENAI_API_KEY="your-openai-key"
export EXA_API_KEY="your-exa-key"
export FIRECRAWL_API_KEY="your-firecrawl-key"
```

## Framework Features

### COTMF (ConfigMaster Organizational Technology Maturity Framework)
- **5 Maturity Stages**: Startup → Growing → Scaling → Established → Enterprise
- **30+ Technology Capabilities**: Across 15 categories
- **Visual Periodic Table**: HTML representation with interactive elements
- **Automated Assessment**: Quantitative stage determination based on org metrics
- **Integration Recommendations**: Stage-appropriate technology suggestions

### Key Framework Files
- `maturity_framework.py`: Core framework implementation
- `technology_periodic_table.py`: Visual HTML generator
- `maturity_assessment_demo.py`: Complete demo with sample organizations

## Development Workflow

### Working with AI Scanners
```python
# Import the AI scanner
from discovery.scanners.ai_platform_scanner import AIPlatformScanner

# Initialize with config
scanner = AIPlatformScanner(api_keys_config)

# Scan a platform
platform_info = await scanner.scan_platform("HubSpot")
```

### Database Operations
- Use SQLAlchemy models in `backend/database/models.py`
- Database connection via `backend/database/database.py`
- Alembic for migrations: `alembic upgrade head`

### Adding New Scanners
1. Inherit from `discovery/scanners/base.py:BaseScanner`
2. Implement `scan()` method returning `PlatformInfo`
3. Add to scanner registry in `discovery/discover.py`

### Frontend Development
- Components in `frontend/app/components/`
- API integration via axios and React Query
- Tailwind classes for styling
- TypeScript throughout

## Current Development Status

### Running Services
- Flask backend: http://localhost:8000 (currently active)
- Next.js frontend: http://localhost:3000 (currently active)
- SQLite database: `backend/configmaster.db`

### Demo Scripts Ready
- `ai_scanner_demo.py`: AI platform scanning demonstration
- `maturity_assessment_demo.py`: COTMF framework demonstration
- `technology_periodic_table.py`: Interactive periodic table generator

### API Endpoints
- `GET /applications`: List applications with filtering
- `GET /statistics`: Platform statistics dashboard
- `POST /discovery/scan`: Trigger discovery scan
- `POST /applications/{id}/compliance`: Run compliance evaluation
- `GET /health`: Health check endpoint

## Testing and Quality

### Backend Testing
```bash
cd backend && python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend && npm test
```

### Linting
- Backend: Black formatter + flake8
- Frontend: ESLint + TypeScript compiler
- Use `make lint` for all components

## Configuration Management

### Environment Variables
- Database: `DATABASE_URL` (defaults to SQLite)
- API Keys: OpenAI, Exa.ai, Firecrawl for AI features
- Flask: `FLASK_ENV=development` for debug mode

### Docker Deployment
- `docker-compose.yml`: Full stack with PostgreSQL, Redis
- Individual service Dockerfiles in respective directories
- Use `make dev` for containerized development

## Integration Patterns

### Common Integration Types
- **Data Sync**: CRM ↔ Marketing automation
- **Webhook Workflows**: Event-driven automation chains
- **Notification Integration**: Business apps → Communication tools
- **Analytics Aggregation**: Data sources → BI platforms

### Adding Integration Recommendations
1. Extend `RecommendationEngine` in `backend/recommendation_engine.py`
2. Define integration patterns in the engine
3. Use AI scanner results for technical feasibility assessment
4. Score recommendations using business value + technical complexity

## AI Platform Analysis

### Supported Platforms
Currently optimized for analyzing: HubSpot, Salesforce, Slack, Asana, Notion, and other SaaS platforms.

### Adding New Platform Analysis
1. Configure platform in `ai_scanner_demo.py`
2. AI scanner automatically discovers API documentation and capabilities
3. Results stored in enhanced database schema
4. Integration recommendations generated automatically