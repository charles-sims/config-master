#!/usr/bin/env python3
"""
Simplified ConfigMaster Backend API
"""

from fastapi import FastAPI
from datetime import datetime
import os
import sqlite3

app = FastAPI(
    title="ConfigMaster API",
    description="Configuration discovery, management, and recommendation platform",
    version="1.0.0"
)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('configmaster.db')
    cursor = conn.cursor()

    # Create applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            environment TEXT NOT NULL,
            description TEXT,
            host TEXT,
            port INTEGER,
            is_active BOOLEAN DEFAULT 1,
            health_status TEXT DEFAULT 'unknown',
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create configurations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT,
            key TEXT NOT NULL,
            value TEXT,
            is_secret BOOLEAN DEFAULT 0,
            source TEXT,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')

    # Create compliance_issues table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compliance_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT,
            description TEXT,
            status TEXT DEFAULT 'open',
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')

    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ConfigMaster API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/statistics")
async def get_statistics():
    """Get platform statistics."""
    try:
        conn = sqlite3.connect('configmaster.db')
        cursor = conn.cursor()

        # Get total applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        total_apps = cursor.fetchone()[0]

        # Get active applications
        cursor.execute("SELECT COUNT(*) FROM applications WHERE is_active = 1")
        active_apps = cursor.fetchone()[0]

        # Get open issues
        cursor.execute("SELECT COUNT(*) FROM compliance_issues WHERE status = 'open'")
        total_issues = cursor.fetchone()[0]

        # Get applications by type
        cursor.execute("SELECT type, COUNT(*) FROM applications GROUP BY type")
        type_results = cursor.fetchall()
        applications_by_type = {row[0]: row[1] for row in type_results}

        # Get applications by environment
        cursor.execute("SELECT environment, COUNT(*) FROM applications GROUP BY environment")
        env_results = cursor.fetchall()
        applications_by_environment = {row[0]: row[1] for row in env_results}

        conn.close()

        return {
            "total_applications": total_apps,
            "active_applications": active_apps,
            "total_open_issues": total_issues,
            "applications_by_type": applications_by_type,
            "applications_by_environment": applications_by_environment
        }
    except Exception as e:
        return {
            "total_applications": 0,
            "active_applications": 0,
            "total_open_issues": 0,
            "applications_by_type": {},
            "applications_by_environment": {},
            "error": str(e)
        }

@app.get("/applications")
async def list_applications():
    """List all applications."""
    try:
        conn = sqlite3.connect('configmaster.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM applications")
        apps = cursor.fetchall()

        conn.close()

        # Convert to list of dictionaries
        applications = []
        for app in apps:
            applications.append({
                "id": app[0],
                "name": app[1],
                "type": app[2],
                "environment": app[3],
                "description": app[4],
                "host": app[5],
                "port": app[6],
                "is_active": bool(app[7]),
                "health_status": app[8],
                "discovered_at": app[9],
                "last_updated": app[10]
            })

        return applications
    except Exception as e:
        return {"error": str(e), "applications": []}

@app.post("/applications")
async def create_application(application_data: dict):
    """Create a new application."""
    try:
        conn = sqlite3.connect('configmaster.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO applications (id, name, type, environment, description, host, port, is_active, health_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            application_data.get('id'),
            application_data.get('name'),
            application_data.get('type'),
            application_data.get('environment'),
            application_data.get('description'),
            application_data.get('host'),
            application_data.get('port'),
            application_data.get('is_active', True),
            application_data.get('health_status', 'unknown')
        ))

        conn.commit()
        conn.close()

        return {"message": "Application created successfully", "id": application_data.get('id')}
    except Exception as e:
        return {"error": str(e)}

@app.post("/discovery/scan")
async def trigger_discovery_scan():
    """Trigger a discovery scan (simplified)."""
    try:
        # Create some sample applications
        conn = sqlite3.connect('configmaster.db')
        cursor = conn.cursor()

        # Sample applications
        sample_apps = [
            {
                'id': 'configmaster-backend',
                'name': 'ConfigMaster Backend',
                'type': 'api_service',
                'environment': 'development',
                'description': 'ConfigMaster FastAPI backend service',
                'host': 'localhost',
                'port': 8000,
                'is_active': True,
                'health_status': 'healthy'
            },
            {
                'id': 'local-database',
                'name': 'Local SQLite Database',
                'type': 'database',
                'environment': 'development',
                'description': 'SQLite database for ConfigMaster',
                'host': 'localhost',
                'port': None,
                'is_active': True,
                'health_status': 'healthy'
            }
        ]

        for app in sample_apps:
            # Check if application already exists
            cursor.execute("SELECT id FROM applications WHERE id = ?", (app['id'],))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO applications (id, name, type, environment, description, host, port, is_active, health_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    app['id'], app['name'], app['type'], app['environment'],
                    app['description'], app['host'], app['port'],
                    app['is_active'], app['health_status']
                ))

        conn.commit()
        conn.close()

        return {"message": "Discovery scan completed", "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)