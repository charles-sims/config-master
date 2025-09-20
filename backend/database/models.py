from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # AppType enum
    environment = Column(String(50), nullable=False)  # Environment enum
    version = Column(String(100))
    description = Column(Text)

    # Infrastructure details
    host = Column(String(255))
    port = Column(Integer)
    path = Column(String(500))
    container_id = Column(String(100))
    k8s_namespace = Column(String(100))
    k8s_deployment = Column(String(100))

    # Configuration
    config_files = Column(JSON)  # List of config file paths
    environment_variables = Column(JSON)  # Dict of env vars

    # Metadata
    discovered_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    last_scanned = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    health_status = Column(String(50), default="unknown")

    # Documentation
    documentation_url = Column(String(500))
    repository_url = Column(String(500))
    maintainer = Column(String(255))

    # Compliance
    compliance_score = Column(Float)
    compliance_last_checked = Column(DateTime)

    # Relationships
    configurations = relationship("Configuration", back_populates="application", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="application", cascade="all, delete-orphan")
    compliance_issues = relationship("ComplianceIssue", back_populates="application", cascade="all, delete-orphan")
    discovery_logs = relationship("DiscoveryLog", back_populates="application")

    # Indexes
    __table_args__ = (
        Index('idx_app_name_env', 'name', 'environment'),
        Index('idx_app_type', 'type'),
        Index('idx_app_active', 'is_active'),
        Index('idx_app_updated', 'last_updated'),
    )

class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text)
    is_secret = Column(Boolean, default=False)
    description = Column(Text)
    source = Column(String(100))  # file path, env var, etc.

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    application = relationship("Application", back_populates="configurations")

    # Indexes
    __table_args__ = (
        Index('idx_config_app_key', 'application_id', 'key'),
        Index('idx_config_secret', 'is_secret'),
    )

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # IntegrationType enum
    target_app = Column(String(255))
    configuration = Column(JSON)
    is_active = Column(Boolean, default=True)
    health_check_url = Column(String(500))
    last_health_check = Column(DateTime)
    health_status = Column(String(50), default="unknown")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    application = relationship("Application", back_populates="integrations")

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # security, performance, documentation, etc.
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    rule_type = Column(String(50), nullable=False)  # config, integration, documentation
    rule_config = Column(JSON)  # Rule-specific configuration
    is_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    issues = relationship("ComplianceIssue", back_populates="rule")

class ComplianceIssue(Base):
    __tablename__ = "compliance_issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id"), nullable=False)
    status = Column(String(20), default="open")  # open, resolved, ignored
    description = Column(Text)
    recommendation = Column(Text)
    detected_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)

    # Relationships
    application = relationship("Application", back_populates="compliance_issues")
    rule = relationship("ComplianceRule", back_populates="issues")

    # Indexes
    __table_args__ = (
        Index('idx_issue_app_status', 'application_id', 'status'),
        Index('idx_issue_rule', 'rule_id'),
    )

class DiscoveryLog(Base):
    __tablename__ = "discovery_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, ForeignKey("applications.id"))
    scanner_name = Column(String(100), nullable=False)
    scan_type = Column(String(50))  # full, incremental, health_check
    status = Column(String(20), nullable=False)  # success, error, partial
    message = Column(Text)
    scan_duration = Column(Float)
    applications_found = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=func.now())

    # Relationships
    application = relationship("Application", back_populates="discovery_logs")

    # Indexes
    __table_args__ = (
        Index('idx_log_scanner_time', 'scanner_name', 'created_at'),
        Index('idx_log_status', 'status'),
    )

class ConfigurationTemplate(Base):
    __tablename__ = "configuration_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    app_type = Column(String(50), nullable=False)
    environment = Column(String(50))
    description = Column(Text)
    template_config = Column(JSON)  # Template configuration structure
    required_keys = Column(JSON)  # List of required configuration keys
    default_values = Column(JSON)  # Default values for configuration
    validation_rules = Column(JSON)  # Validation rules for values

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    settings = Column(JSON)  # Organization-wide settings
    compliance_profile = Column(JSON)  # Compliance rules and thresholds

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class IntegrationTemplate(Base):
    __tablename__ = "integration_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    integration_type = Column(String(50), nullable=False)
    source_app_type = Column(String(50))
    target_app_type = Column(String(50))
    description = Column(Text)
    configuration_schema = Column(JSON)
    setup_instructions = Column(Text)
    health_check_config = Column(JSON)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class PlatformCapability(Base):
    """AI-discovered platform capabilities and features"""
    __tablename__ = "platform_capabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    capability_type = Column(String(50), nullable=False)  # api, webhook, integration, feature
    name = Column(String(255), nullable=False)
    description = Column(Text)
    technical_details = Column(JSON)  # Endpoints, parameters, schemas, etc.
    documentation_url = Column(String(500))
    confidence_score = Column(Float, default=0.0)  # AI confidence in this capability
    discovery_method = Column(String(50))  # exa, firecrawl, playwright, manual

    # API-specific fields
    api_endpoint = Column(String(500))
    http_method = Column(String(10))
    authentication_required = Column(Boolean, default=False)
    rate_limit_info = Column(JSON)

    discovered_at = Column(DateTime, default=func.now())
    last_verified = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    application = relationship("Application")

    # Indexes
    __table_args__ = (
        Index('idx_capability_app_type', 'application_id', 'capability_type'),
        Index('idx_capability_confidence', 'confidence_score'),
    )

class IntegrationRecommendation(Base):
    """AI-generated integration recommendations"""
    __tablename__ = "integration_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_app_id = Column(String, ForeignKey("applications.id"), nullable=False)
    target_app_id = Column(String, ForeignKey("applications.id"))
    target_platform_name = Column(String(255))  # For external platforms not in our system

    recommendation_type = Column(String(50), nullable=False)  # sync, workflow, notification, etc.
    purpose = Column(Text, nullable=False)  # Why this integration is recommended
    complexity = Column(String(20), default="medium")  # low, medium, high
    priority = Column(String(20), default="medium")  # low, medium, high, critical

    # Benefits and details
    benefits = Column(JSON)  # List of benefits this integration provides
    use_cases = Column(JSON)  # Specific use cases
    implementation_steps = Column(JSON)  # Step-by-step implementation guide
    estimated_effort_hours = Column(Integer)

    # AI scoring
    ai_confidence = Column(Float, default=0.0)
    business_value_score = Column(Float, default=0.0)
    technical_feasibility_score = Column(Float, default=0.0)

    # Status tracking
    status = Column(String(20), default="suggested")  # suggested, planned, in_progress, implemented, rejected
    implemented_at = Column(DateTime)
    notes = Column(Text)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    source_app = relationship("Application", foreign_keys=[source_app_id])
    target_app = relationship("Application", foreign_keys=[target_app_id])

    # Indexes
    __table_args__ = (
        Index('idx_recommendation_source', 'source_app_id'),
        Index('idx_recommendation_priority', 'priority'),
        Index('idx_recommendation_status', 'status'),
    )

class PlatformAnalysis(Base):
    """Comprehensive AI analysis results for platforms"""
    __tablename__ = "platform_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)

    # Analysis metadata
    analysis_version = Column(String(20), default="1.0")
    analysis_timestamp = Column(DateTime, default=func.now())
    ai_model_used = Column(String(50))  # gpt-4, gpt-3.5-turbo, etc.
    confidence_score = Column(Float, default=0.0)

    # Core analysis results
    category = Column(String(100))  # CRM, Marketing, Analytics, etc.
    primary_functions = Column(JSON)  # List of main functions
    business_model = Column(String(100))  # SaaS, Enterprise, Freemium, etc.
    pricing_tiers = Column(JSON)  # Pricing information

    # Technical capabilities
    api_capabilities = Column(JSON)  # REST, GraphQL, Webhooks, etc.
    integration_ecosystem = Column(JSON)  # Supported integrations
    security_features = Column(JSON)  # Security and compliance features
    scalability_info = Column(JSON)  # Scalability and performance info

    # Discovery sources
    documentation_sources = Column(JSON)  # URLs and sources analyzed
    web_exploration_results = Column(JSON)  # Playwright exploration data
    search_results_summary = Column(JSON)  # Exa.ai search summary

    # Quality metrics
    data_completeness_score = Column(Float, default=0.0)
    source_reliability_score = Column(Float, default=0.0)
    analysis_freshness_days = Column(Integer, default=0)

    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    application = relationship("Application")

    # Indexes
    __table_args__ = (
        Index('idx_analysis_app_time', 'application_id', 'analysis_timestamp'),
        Index('idx_analysis_confidence', 'confidence_score'),
    )

class ConfigurationOption(Base):
    """AI-discovered configuration options for platforms"""
    __tablename__ = "configuration_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)

    option_name = Column(String(255), nullable=False)
    option_category = Column(String(100))  # security, integration, ui, workflow, etc.
    option_type = Column(String(50))  # boolean, string, number, select, multi-select
    description = Column(Text)

    # Configuration details
    default_value = Column(Text)
    possible_values = Column(JSON)  # For select/multi-select options
    validation_rules = Column(JSON)  # Validation constraints
    dependencies = Column(JSON)  # Other options this depends on

    # Access control
    user_access_level = Column(String(50))  # admin, user, api_only
    requires_premium = Column(Boolean, default=False)
    affects_billing = Column(Boolean, default=False)

    # Discovery metadata
    discovery_method = Column(String(50))
    confidence_score = Column(Float, default=0.0)
    documentation_url = Column(String(500))

    discovered_at = Column(DateTime, default=func.now())
    last_verified = Column(DateTime)
    is_available = Column(Boolean, default=True)

    # Relationships
    application = relationship("Application")

    # Indexes
    __table_args__ = (
        Index('idx_config_option_app_category', 'application_id', 'option_category'),
        Index('idx_config_option_access', 'user_access_level'),
    )