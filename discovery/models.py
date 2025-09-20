from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class AppType(str, Enum):
    WEB_APPLICATION = "web_application"
    API_SERVICE = "api_service"
    DATABASE = "database"
    MICROSERVICE = "microservice"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    SAAS_TOOL = "saas_tool"
    CUSTOM_TOOL = "custom_tool"

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class IntegrationType(str, Enum):
    API = "api"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    WEBHOOK = "webhook"
    SSO = "sso"
    OAUTH = "oauth"

class ConfigurationItem(BaseModel):
    key: str
    value: Any
    is_secret: bool = False
    description: Optional[str] = None
    source: str  # file path, env var, etc.

class Integration(BaseModel):
    name: str
    type: IntegrationType
    target_app: str
    configuration: Dict[str, Any]
    is_active: bool = True
    health_check_url: Optional[str] = None

class Application(BaseModel):
    id: str
    name: str
    type: AppType
    environment: Environment
    version: Optional[str] = None
    description: Optional[str] = None

    # Infrastructure details
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    container_id: Optional[str] = None
    k8s_namespace: Optional[str] = None
    k8s_deployment: Optional[str] = None

    # Configuration
    configuration: List[ConfigurationItem] = Field(default_factory=list)
    config_files: List[str] = Field(default_factory=list)
    environment_variables: Dict[str, str] = Field(default_factory=dict)

    # Integrations
    integrations: List[Integration] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)

    # Metadata
    discovered_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    health_status: str = "unknown"

    # Documentation
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None
    maintainer: Optional[str] = None

    # Compliance
    compliance_score: Optional[float] = None
    compliance_issues: List[str] = Field(default_factory=list)

class DiscoveryTarget(BaseModel):
    name: str
    type: str  # kubernetes, docker, filesystem, cloud, etc.
    configuration: Dict[str, Any]
    enabled: bool = True

class DiscoveryResult(BaseModel):
    target: str
    applications: List[Application]
    errors: List[str] = Field(default_factory=list)
    scan_duration: float
    timestamp: datetime = Field(default_factory=datetime.now)