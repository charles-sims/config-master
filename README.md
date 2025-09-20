# ConfigMaster

A comprehensive configuration discovery, management, and recommendation platform for innovation studios.

## Features

- **Automated Discovery**: Scans and catalogs all applications (off-the-shelf and custom)
- **Configuration Management**: Centralized configuration storage and versioning
- **Compliance Monitoring**: Validates configurations against organizational standards
- **Documentation Generation**: Auto-generates configuration documentation
- **Integration Validation**: Ensures proper application integrations
- **Organization-as-Code**: Infrastructure and configuration as version-controlled code

## Architecture

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Discovery     │  │   Frontend      │  │   Infrastructure│
│   Engine        │  │   Dashboard     │  │   as Code       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
         └──────────┬──────────┴──────────┬──────────┘
                    │                     │
            ┌─────────────────┐  ┌─────────────────┐
            │   Backend API   │  │   Database      │
            │   (FastAPI)     │  │   (PostgreSQL)  │
            └─────────────────┘  └─────────────────┘
```

## Quick Start

1. **Setup Backend**: `cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
2. **Setup Frontend**: `cd frontend && npm install`
3. **Run Discovery**: `cd discovery && python discover.py`
4. **Deploy Infrastructure**: `cd infrastructure && terraform init && terraform apply`

## Components

- `/backend` - FastAPI application with configuration management APIs
- `/frontend` - Next.js dashboard for configuration management
- `/discovery` - Python scripts for application discovery
- `/infrastructure` - Terraform and Ansible for deployment
- `/docs` - Generated documentation and schemas

## Development

```bash
# Start backend
cd backend && uvicorn main:app --reload

# Start frontend
cd frontend && npm run dev

# Run discovery
cd discovery && python discover.py --scan-all
```