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

# Base schemas
class ConfigurationBase(BaseModel):
    key: str
    value: Any
    is_secret: bool = False
    description: Optional[str] = None
    source: str

class ConfigurationCreate(ConfigurationBase):
    pass

class Configuration(ConfigurationBase):
    id: int
    application_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class IntegrationBase(BaseModel):
    name: str
    type: IntegrationType
    target_app: str
    configuration: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    health_check_url: Optional[str] = None

class IntegrationCreate(IntegrationBase):
    pass

class Integration(IntegrationBase):
    id: int
    application_id: str
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ComplianceIssueBase(BaseModel):
    status: str = "open"
    description: Optional[str] = None
    recommendation: Optional[str] = None

class ComplianceIssue(ComplianceIssueBase):
    id: int
    application_id: str
    rule_id: int
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Application schemas
class ApplicationBase(BaseModel):
    name: str
    type: AppType
    environment: Environment
    version: Optional[str] = None
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    container_id: Optional[str] = None
    k8s_namespace: Optional[str] = None
    k8s_deployment: Optional[str] = None
    config_files: List[str] = Field(default_factory=list)
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    is_active: bool = True
    health_status: str = "unknown"
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None
    maintainer: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    id: str
    configurations: List[ConfigurationCreate] = Field(default_factory=list)
    integrations: List[IntegrationCreate] = Field(default_factory=list)

class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    config_files: Optional[List[str]] = None
    environment_variables: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None
    health_status: Optional[str] = None
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None
    maintainer: Optional[str] = None

class Application(ApplicationBase):
    id: str
    discovered_at: datetime
    last_updated: datetime
    last_scanned: datetime
    compliance_score: Optional[float] = None
    compliance_last_checked: Optional[datetime] = None
    configurations: List[Configuration] = Field(default_factory=list)
    integrations: List[Integration] = Field(default_factory=list)
    compliance_issues: List[ComplianceIssue] = Field(default_factory=list)

    class Config:
        orm_mode = True

# List and filter schemas
class ApplicationFilter(BaseModel):
    type: Optional[AppType] = None
    environment: Optional[Environment] = None
    is_active: Optional[bool] = None
    has_issues: Optional[bool] = None

class ApplicationSummary(BaseModel):
    id: str
    name: str
    type: AppType
    environment: Environment
    health_status: str
    is_active: bool
    last_updated: datetime
    compliance_score: Optional[float] = None
    issues_count: int = 0

    class Config:
        orm_mode = True