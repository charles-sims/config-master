from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime

from database.database import get_db, create_tables
from database import models
from schemas.application import (
    Application, ApplicationCreate, ApplicationUpdate, ApplicationSummary, ApplicationFilter
)
from compliance.rules import ComplianceEngine

# Create FastAPI app
app = FastAPI(
    title="ConfigMaster API",
    description="Configuration discovery, management, and recommendation platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize compliance engine
compliance_engine = ComplianceEngine()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    create_tables()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ConfigMaster API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

# Application endpoints
@app.get("/applications", response_model=List[ApplicationSummary])
async def list_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = None,
    environment: Optional[str] = None,
    is_active: Optional[bool] = None,
    has_issues: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List applications with optional filtering."""
    query = db.query(models.Application)

    # Apply filters
    if type:
        query = query.filter(models.Application.type == type)
    if environment:
        query = query.filter(models.Application.environment == environment)
    if is_active is not None:
        query = query.filter(models.Application.is_active == is_active)

    applications = query.offset(skip).limit(limit).all()

    # Convert to summary format
    summaries = []
    for app in applications:
        issues_count = len(app.compliance_issues) if app.compliance_issues else 0

        # Apply has_issues filter
        if has_issues is not None:
            if has_issues and issues_count == 0:
                continue
            if not has_issues and issues_count > 0:
                continue

        summary = ApplicationSummary(
            id=app.id,
            name=app.name,
            type=app.type,
            environment=app.environment,
            health_status=app.health_status,
            is_active=app.is_active,
            last_updated=app.last_updated,
            compliance_score=app.compliance_score,
            issues_count=issues_count
        )
        summaries.append(summary)

    return summaries

@app.get("/applications/{application_id}", response_model=Application)
async def get_application(application_id: str, db: Session = Depends(get_db)):
    """Get application by ID."""
    app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@app.post("/applications", response_model=Application)
async def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    """Create a new application."""
    # Check if application already exists
    existing = db.query(models.Application).filter(models.Application.id == application.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Application ID already exists")

    # Create application
    db_app = models.Application(**application.dict(exclude={'configurations', 'integrations'}))
    db.add(db_app)
    db.flush()

    # Add configurations
    for config in application.configurations:
        db_config = models.Configuration(application_id=db_app.id, **config.dict())
        db.add(db_config)

    # Add integrations
    for integration in application.integrations:
        db_integration = models.Integration(application_id=db_app.id, **integration.dict())
        db.add(db_integration)

    db.commit()
    db.refresh(db_app)
    return db_app

@app.put("/applications/{application_id}", response_model=Application)
async def update_application(
    application_id: str,
    application: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update an application."""
    db_app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update fields
    update_data = application.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_app, field, value)

    db_app.last_updated = datetime.now()
    db.commit()
    db.refresh(db_app)
    return db_app

@app.delete("/applications/{application_id}")
async def delete_application(application_id: str, db: Session = Depends(get_db)):
    """Delete an application."""
    db_app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(db_app)
    db.commit()
    return {"message": "Application deleted successfully"}

# Compliance endpoints
@app.post("/applications/{application_id}/compliance")
async def evaluate_compliance(application_id: str, db: Session = Depends(get_db)):
    """Evaluate compliance for an application."""
    db_app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Convert to dict for compliance engine
    app_dict = {
        'id': db_app.id,
        'name': db_app.name,
        'type': db_app.type,
        'environment': db_app.environment,
        'host': db_app.host,
        'port': db_app.port,
        'container_id': db_app.container_id,
        'k8s_namespace': db_app.k8s_namespace,
        'configurations': [
            {
                'key': config.key,
                'value': config.value,
                'is_secret': config.is_secret,
                'source': config.source
            }
            for config in db_app.configurations
        ],
        'integrations': [
            {
                'name': integration.name,
                'type': integration.type,
                'health_check_url': integration.health_check_url
            }
            for integration in db_app.integrations
        ],
        'environment_variables': db_app.environment_variables or {},
        'description': db_app.description,
        'documentation_url': db_app.documentation_url,
        'repository_url': db_app.repository_url,
        'maintainer': db_app.maintainer
    }

    # Run compliance evaluation
    results = compliance_engine.evaluate_application(app_dict)
    compliance_score = compliance_engine.calculate_compliance_score(results)
    recommendations = compliance_engine.get_recommendations(results)

    # Update application with compliance score
    db_app.compliance_score = compliance_score
    db_app.compliance_last_checked = datetime.now()

    # Clear existing compliance issues
    db.query(models.ComplianceIssue).filter(
        models.ComplianceIssue.application_id == application_id
    ).delete()

    # Add new compliance issues
    for result in results:
        if not result.passed:
            issue = models.ComplianceIssue(
                application_id=application_id,
                rule_id=1,  # Would map to actual rule IDs in production
                description=result.description,
                recommendation=result.recommendation,
                status="open"
            )
            db.add(issue)

    db.commit()

    return {
        "application_id": application_id,
        "compliance_score": compliance_score,
        "results": [
            {
                "rule_id": result.rule_id,
                "rule_name": result.rule_name,
                "passed": result.passed,
                "severity": result.severity,
                "description": result.description,
                "recommendation": result.recommendation,
                "details": result.details
            }
            for result in results
        ],
        "recommendations": recommendations
    }

@app.get("/applications/{application_id}/recommendations")
async def get_recommendations(application_id: str, db: Session = Depends(get_db)):
    """Get recommendations for an application."""
    db_app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Get open compliance issues
    issues = db.query(models.ComplianceIssue).filter(
        models.ComplianceIssue.application_id == application_id,
        models.ComplianceIssue.status == "open"
    ).all()

    recommendations = [
        {
            "issue_id": issue.id,
            "description": issue.description,
            "recommendation": issue.recommendation,
            "detected_at": issue.detected_at
        }
        for issue in issues
    ]

    return {"application_id": application_id, "recommendations": recommendations}

# Discovery endpoints
@app.post("/discovery/scan")
async def trigger_discovery_scan():
    """Trigger a discovery scan."""
    # This would typically trigger a background job
    return {"message": "Discovery scan triggered", "status": "started"}

@app.get("/discovery/status")
async def get_discovery_status():
    """Get discovery scan status."""
    return {"status": "idle", "last_scan": datetime.now()}

# Statistics endpoints
@app.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get platform statistics."""
    total_apps = db.query(models.Application).count()
    active_apps = db.query(models.Application).filter(models.Application.is_active == True).count()
    total_issues = db.query(models.ComplianceIssue).filter(models.ComplianceIssue.status == "open").count()

    # Get applications by type
    type_stats = {}
    for app in db.query(models.Application).all():
        type_stats[app.type] = type_stats.get(app.type, 0) + 1

    # Get applications by environment
    env_stats = {}
    for app in db.query(models.Application).all():
        env_stats[app.environment] = env_stats.get(app.environment, 0) + 1

    return {
        "total_applications": total_apps,
        "active_applications": active_apps,
        "total_open_issues": total_issues,
        "applications_by_type": type_stats,
        "applications_by_environment": env_stats
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)