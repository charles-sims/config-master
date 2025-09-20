#!/usr/bin/env python3
"""
ConfigMaster Organizational Technology Maturity Framework (COTMF)

A comprehensive framework similar to COBIT or InfoTech's periodic table that defines
the technology stack every company should have based on their maturity stage.

Think of it as the "Periodic Table of Business Technology" with evolutionary growth patterns.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

class MaturityStage(Enum):
    """Organizational maturity stages"""
    STARTUP = "startup"                    # 1-10 people, MVP stage
    GROWING = "growing"                    # 11-50 people, product-market fit
    SCALING = "scaling"                    # 51-200 people, scaling operations
    ESTABLISHED = "established"            # 201-1000 people, mature processes
    ENTERPRISE = "enterprise"              # 1000+ people, complex operations

class TechnologyCategory(Enum):
    """Core technology categories (like elements in periodic table)"""
    # Core Business Infrastructure (Period 1 - Essential)
    COMMUNICATION = "communication"        # Email, chat, video conferencing
    FILE_STORAGE = "file_storage"         # Cloud storage, document management
    FINANCIAL = "financial"               # Accounting, payments, invoicing

    # Operational Foundation (Period 2 - Growth)
    PROJECT_MGMT = "project_management"    # Task tracking, project planning
    CRM = "customer_relationship"          # Customer management, sales tracking
    HR_BASIC = "human_resources_basic"     # Employee records, basic HR

    # Business Intelligence (Period 3 - Scaling)
    ANALYTICS = "analytics"                # Business intelligence, reporting
    MARKETING = "marketing_automation"     # Email marketing, lead nurturing
    SUPPORT = "customer_support"          # Help desk, knowledge base

    # Security & Compliance (Period 4 - Established)
    SECURITY = "security_infrastructure"  # Identity management, security tools
    COMPLIANCE = "compliance_management"   # Audit, governance, risk
    DEV_OPS = "development_operations"     # CI/CD, infrastructure as code

    # Advanced Operations (Period 5 - Enterprise)
    ADVANCED_ANALYTICS = "advanced_analytics"  # AI/ML, predictive analytics
    ENTERPRISE_INTEGRATION = "enterprise_integration"  # ESB, API management
    SUPPLY_CHAIN = "supply_chain"          # ERP, supply chain management

class IntegrationComplexity(Enum):
    """Integration complexity levels"""
    NONE = "none"           # Standalone tool
    SIMPLE = "simple"       # Basic integrations (OAuth, webhooks)
    MODERATE = "moderate"   # API integrations, data sync
    COMPLEX = "complex"     # Complex workflows, enterprise integrations
    ADVANCED = "advanced"   # Custom integrations, real-time processing

@dataclass
class TechnologyCapability:
    """Individual technology capability within a category"""
    name: str
    description: str
    category: TechnologyCategory
    required_stage: MaturityStage
    priority: str  # critical, high, medium, low

    # Implementation details
    typical_solutions: List[str] = field(default_factory=list)
    integration_complexity: IntegrationComplexity = IntegrationComplexity.SIMPLE
    setup_time_days: int = 7
    monthly_cost_range: Tuple[int, int] = (0, 100)  # USD range

    # Prerequisites and relationships
    prerequisites: List[str] = field(default_factory=list)  # Other capabilities needed first
    synergies: List[str] = field(default_factory=list)      # Works better with these
    replaces: List[str] = field(default_factory=list)       # Replaces these capabilities

    # Business metrics
    productivity_impact: float = 1.0    # Multiplier for team productivity
    risk_reduction: float = 0.0         # Risk reduction factor
    compliance_impact: List[str] = field(default_factory=list)  # Compliance frameworks helped

@dataclass
class StageGate:
    """Criteria for moving between maturity stages"""
    from_stage: MaturityStage
    to_stage: MaturityStage

    # Quantitative triggers
    employee_count_min: int
    revenue_threshold: int  # Annual revenue in USD
    customer_count_min: int

    # Qualitative triggers
    business_indicators: List[str] = field(default_factory=list)
    technology_requirements: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)

    # Recommended technology additions for this transition
    new_capabilities: List[str] = field(default_factory=list)
    integration_updates: List[str] = field(default_factory=list)

class OrganizationalTechnologyFramework:
    """
    The main framework that defines the complete technology evolution path
    for organizations from startup to enterprise.
    """

    def __init__(self):
        self.capabilities = self._define_capabilities()
        self.stage_gates = self._define_stage_gates()
        self.integration_patterns = self._define_integration_patterns()

    def _define_capabilities(self) -> Dict[str, TechnologyCapability]:
        """Define all technology capabilities across maturity stages"""

        capabilities = {}

        # STARTUP STAGE - Essential survival tools
        capabilities.update({
            "email_system": TechnologyCapability(
                name="Professional Email System",
                description="Business email with custom domain and collaboration features",
                category=TechnologyCategory.COMMUNICATION,
                required_stage=MaturityStage.STARTUP,
                priority="critical",
                typical_solutions=["Google Workspace", "Microsoft 365", "Zoho Mail"],
                integration_complexity=IntegrationComplexity.SIMPLE,
                setup_time_days=1,
                monthly_cost_range=(5, 15),
                productivity_impact=1.2
            ),

            "cloud_storage": TechnologyCapability(
                name="Cloud File Storage & Sharing",
                description="Secure cloud storage with file sharing and collaboration",
                category=TechnologyCategory.FILE_STORAGE,
                required_stage=MaturityStage.STARTUP,
                priority="critical",
                typical_solutions=["Google Drive", "Dropbox Business", "OneDrive"],
                integration_complexity=IntegrationComplexity.SIMPLE,
                setup_time_days=1,
                monthly_cost_range=(10, 25),
                synergies=["email_system"],
                productivity_impact=1.15
            ),

            "basic_accounting": TechnologyCapability(
                name="Basic Accounting & Bookkeeping",
                description="Track income, expenses, and generate basic financial reports",
                category=TechnologyCategory.FINANCIAL,
                required_stage=MaturityStage.STARTUP,
                priority="critical",
                typical_solutions=["QuickBooks", "Xero", "FreshBooks"],
                integration_complexity=IntegrationComplexity.SIMPLE,
                setup_time_days=3,
                monthly_cost_range=(15, 50),
                compliance_impact=["Tax Compliance", "Financial Reporting"]
            ),

            "video_conferencing": TechnologyCapability(
                name="Video Conferencing & Meetings",
                description="Virtual meetings, screen sharing, and remote collaboration",
                category=TechnologyCategory.COMMUNICATION,
                required_stage=MaturityStage.STARTUP,
                priority="high",
                typical_solutions=["Zoom", "Google Meet", "Microsoft Teams"],
                integration_complexity=IntegrationComplexity.SIMPLE,
                setup_time_days=1,
                monthly_cost_range=(0, 20),
                synergies=["email_system"],
                productivity_impact=1.3
            ),

            "password_manager": TechnologyCapability(
                name="Business Password Management",
                description="Secure password storage and sharing for team accounts",
                category=TechnologyCategory.SECURITY,
                required_stage=MaturityStage.STARTUP,
                priority="high",
                typical_solutions=["1Password Business", "Bitwarden", "LastPass"],
                integration_complexity=IntegrationComplexity.SIMPLE,
                setup_time_days=2,
                monthly_cost_range=(3, 8),
                risk_reduction=0.3,
                compliance_impact=["Security Best Practices"]
            )
        })

        # GROWING STAGE - Operational efficiency
        capabilities.update({
            "project_management": TechnologyCapability(
                name="Project & Task Management",
                description="Track projects, assign tasks, and manage team workflows",
                category=TechnologyCategory.PROJECT_MGMT,
                required_stage=MaturityStage.GROWING,
                priority="critical",
                typical_solutions=["Asana", "Monday.com", "Notion", "ClickUp"],
                integration_complexity=IntegrationComplexity.MODERATE,
                setup_time_days=5,
                monthly_cost_range=(10, 25),
                prerequisites=["email_system"],
                productivity_impact=1.4
            ),

            "basic_crm": TechnologyCapability(
                name="Customer Relationship Management",
                description="Track leads, manage customer relationships, and sales pipeline",
                category=TechnologyCategory.CRM,
                required_stage=MaturityStage.GROWING,
                priority="critical",
                typical_solutions=["HubSpot", "Pipedrive", "Zoho CRM", "Salesforce Essentials"],
                integration_complexity=IntegrationComplexity.MODERATE,
                setup_time_days=7,
                monthly_cost_range=(20, 75),
                synergies=["email_system", "project_management"],
                productivity_impact=1.3
            ),

            "hr_management": TechnologyCapability(
                name="HR Information System",
                description="Employee records, onboarding, time tracking, and basic HR",
                category=TechnologyCategory.HR_BASIC,
                required_stage=MaturityStage.GROWING,
                priority="high",
                typical_solutions=["BambooHR", "Gusto", "Workday", "Zenefits"],
                integration_complexity=IntegrationComplexity.MODERATE,
                setup_time_days=10,
                monthly_cost_range=(25, 50),
                compliance_impact=["Employment Law", "Data Privacy"]
            ),

            "backup_system": TechnologyCapability(
                name="Automated Data Backup",
                description="Automated backup of critical business data and systems",
                category=TechnologyCategory.FILE_STORAGE,
                required_stage=MaturityStage.GROWING,
                priority="high",
                typical_solutions=["Backblaze", "Carbonite", "AWS Backup"],
                integration_complexity=IntegrationComplexity.SIMPLE,
                setup_time_days=3,
                monthly_cost_range=(5, 25),
                prerequisites=["cloud_storage"],
                risk_reduction=0.4
            ),

            "invoicing_system": TechnologyCapability(
                name="Professional Invoicing & Payments",
                description="Create invoices, track payments, and accept online payments",
                category=TechnologyCategory.FINANCIAL,
                required_stage=MaturityStage.GROWING,
                priority="high",
                typical_solutions=["Stripe", "Square", "PayPal Business", "Wave"],
                integration_complexity=IntegrationComplexity.MODERATE,
                setup_time_days=5,
                monthly_cost_range=(0, 30),
                synergies=["basic_accounting", "basic_crm"],
                productivity_impact=1.2
            )
        })

        # SCALING STAGE - Process optimization
        capabilities.update({
            "marketing_automation": TechnologyCapability(
                name="Marketing Automation Platform",
                description="Email campaigns, lead nurturing, and marketing analytics",
                category=TechnologyCategory.MARKETING,
                required_stage=MaturityStage.SCALING,
                priority="critical",
                typical_solutions=["Mailchimp", "Constant Contact", "ActiveCampaign"],
                integration_complexity=IntegrationComplexity.COMPLEX,
                setup_time_days=14,
                monthly_cost_range=(50, 300),
                prerequisites=["basic_crm"],
                synergies=["analytics_platform"],
                productivity_impact=1.5
            ),

            "analytics_platform": TechnologyCapability(
                name="Business Intelligence & Analytics",
                description="Data analytics, reporting dashboards, and business insights",
                category=TechnologyCategory.ANALYTICS,
                required_stage=MaturityStage.SCALING,
                priority="critical",
                typical_solutions=["Google Analytics", "Mixpanel", "Tableau", "Power BI"],
                integration_complexity=IntegrationComplexity.COMPLEX,
                setup_time_days=21,
                monthly_cost_range=(50, 200),
                synergies=["basic_crm", "marketing_automation"],
                productivity_impact=1.3
            ),

            "customer_support": TechnologyCapability(
                name="Customer Support & Help Desk",
                description="Ticket management, knowledge base, and customer support tools",
                category=TechnologyCategory.SUPPORT,
                required_stage=MaturityStage.SCALING,
                priority="high",
                typical_solutions=["Zendesk", "Freshdesk", "Intercom", "Help Scout"],
                integration_complexity=IntegrationComplexity.MODERATE,
                setup_time_days=10,
                monthly_cost_range=(25, 100),
                synergies=["basic_crm"],
                productivity_impact=1.2
            ),

            "identity_management": TechnologyCapability(
                name="Identity & Access Management",
                description="Single sign-on, user provisioning, and access controls",
                category=TechnologyCategory.SECURITY,
                required_stage=MaturityStage.SCALING,
                priority="high",
                typical_solutions=["Okta", "Azure AD", "OneLogin", "Auth0"],
                integration_complexity=IntegrationComplexity.COMPLEX,
                setup_time_days=14,
                monthly_cost_range=(25, 75),
                prerequisites=["password_manager"],
                risk_reduction=0.5,
                compliance_impact=["SOC 2", "GDPR"]
            ),

            "advanced_accounting": TechnologyCapability(
                name="Advanced Financial Management",
                description="Advanced accounting, financial planning, and expense management",
                category=TechnologyCategory.FINANCIAL,
                required_stage=MaturityStage.SCALING,
                priority="high",
                typical_solutions=["NetSuite", "Sage Intacct", "QuickBooks Enterprise"],
                integration_complexity=IntegrationComplexity.COMPLEX,
                setup_time_days=30,
                monthly_cost_range=(100, 500),
                replaces=["basic_accounting"],
                synergies=["analytics_platform"],
                compliance_impact=["Financial Reporting", "SOX Compliance"]
            )
        })

        # ESTABLISHED STAGE - Governance and compliance
        capabilities.update({
            "enterprise_crm": TechnologyCapability(
                name="Enterprise CRM & Sales Operations",
                description="Advanced CRM with sales operations, forecasting, and automation",
                category=TechnologyCategory.CRM,
                required_stage=MaturityStage.ESTABLISHED,
                priority="critical",
                typical_solutions=["Salesforce", "HubSpot Enterprise", "Microsoft Dynamics"],
                integration_complexity=IntegrationComplexity.ADVANCED,
                setup_time_days=45,
                monthly_cost_range=(150, 500),
                replaces=["basic_crm"],
                synergies=["marketing_automation", "analytics_platform"],
                productivity_impact=1.6
            ),

            "compliance_management": TechnologyCapability(
                name="Governance, Risk & Compliance",
                description="Compliance monitoring, risk assessment, and audit management",
                category=TechnologyCategory.COMPLIANCE,
                required_stage=MaturityStage.ESTABLISHED,
                priority="critical",
                typical_solutions=["ServiceNow GRC", "MetricStream", "LogicGate"],
                integration_complexity=IntegrationComplexity.ADVANCED,
                setup_time_days=60,
                monthly_cost_range=(200, 1000),
                prerequisites=["identity_management"],
                risk_reduction=0.6,
                compliance_impact=["SOC 2", "ISO 27001", "GDPR", "HIPAA"]
            ),

            "devops_platform": TechnologyCapability(
                name="DevOps & CI/CD Platform",
                description="Continuous integration, deployment, and infrastructure automation",
                category=TechnologyCategory.DEV_OPS,
                required_stage=MaturityStage.ESTABLISHED,
                priority="high",
                typical_solutions=["GitLab", "Azure DevOps", "GitHub Enterprise"],
                integration_complexity=IntegrationComplexity.ADVANCED,
                setup_time_days=30,
                monthly_cost_range=(100, 400),
                productivity_impact=1.4
            ),

            "enterprise_hr": TechnologyCapability(
                name="Enterprise HR Management System",
                description="Comprehensive HR with performance, benefits, and talent management",
                category=TechnologyCategory.HR_BASIC,
                required_stage=MaturityStage.ESTABLISHED,
                priority="high",
                typical_solutions=["Workday", "SuccessFactors", "BambooHR Advanced"],
                integration_complexity=IntegrationComplexity.ADVANCED,
                setup_time_days=90,
                monthly_cost_range=(50, 150),
                replaces=["hr_management"],
                compliance_impact=["Employment Law", "Benefits Compliance"]
            ),

            "security_monitoring": TechnologyCapability(
                name="Security Information & Event Management",
                description="Security monitoring, threat detection, and incident response",
                category=TechnologyCategory.SECURITY,
                required_stage=MaturityStage.ESTABLISHED,
                priority="critical",
                typical_solutions=["Splunk", "IBM QRadar", "Azure Sentinel"],
                integration_complexity=IntegrationComplexity.ADVANCED,
                setup_time_days=45,
                monthly_cost_range=(200, 800),
                prerequisites=["identity_management"],
                risk_reduction=0.7,
                compliance_impact=["SOC 2", "ISO 27001"]
            )
        })

        # ENTERPRISE STAGE - Advanced operations
        capabilities.update({
            "erp_system": TechnologyCapability(
                name="Enterprise Resource Planning",
                description="Integrated business processes, supply chain, and operations management",
                category=TechnologyCategory.SUPPLY_CHAIN,
                required_stage=MaturityStage.ENTERPRISE,
                priority="critical",
                typical_solutions=["SAP", "Oracle ERP", "Microsoft Dynamics 365"],
                integration_complexity=IntegrationComplexity.ADVANCED,
                setup_time_days=180,
                monthly_cost_range=(500, 2000),
                synergies=["advanced_accounting", "enterprise_crm"],
                productivity_impact=1.5
            ),

            "ai_ml_platform": TechnologyCapability(
                name="AI/ML & Advanced Analytics",
                description="Machine learning, predictive analytics, and AI-powered insights",
                category=TechnologyCategory.ADVANCED_ANALYTICS,
                required_stage=MaturityStage.ENTERPRISE,
                priority="high",
                typical_solutions=["Databricks", "AWS SageMaker", "Azure ML"],
                integration_complexity=IntegrationComplexity.ADVANCED,
                setup_time_days=90,
                monthly_cost_range=(500, 2000),
                prerequisites=["analytics_platform"],
                productivity_impact=1.8
            ),

            "api_management": TechnologyCapability(
                name="Enterprise API Management",
                description="API gateway, management, and enterprise integration platform",
                category=TechnologyCategory.ENTERPRISE_INTEGRATION,
                required_stage=MaturityStage.ENTERPRISE,
                priority="high",
                typical_solutions=["MuleSoft", "Apigee", "Azure API Management"],
                integration_complexity=IntegrationComplexity.ADVANCED,
                setup_time_days=60,
                monthly_cost_range=(300, 1500),
                prerequisites=["devops_platform"],
                productivity_impact=1.3
            )
        })

        return capabilities

    def _define_stage_gates(self) -> List[StageGate]:
        """Define the criteria for moving between maturity stages"""

        return [
            StageGate(
                from_stage=MaturityStage.STARTUP,
                to_stage=MaturityStage.GROWING,
                employee_count_min=10,
                revenue_threshold=500000,  # $500K ARR
                customer_count_min=50,
                business_indicators=[
                    "Product-market fit achieved",
                    "Consistent monthly growth",
                    "First paying customers",
                    "Basic team structure in place"
                ],
                technology_requirements=[
                    "Basic communication tools established",
                    "Financial tracking in place",
                    "File management system working"
                ],
                new_capabilities=[
                    "project_management",
                    "basic_crm",
                    "hr_management"
                ]
            ),

            StageGate(
                from_stage=MaturityStage.GROWING,
                to_stage=MaturityStage.SCALING,
                employee_count_min=50,
                revenue_threshold=2000000,  # $2M ARR
                customer_count_min=200,
                business_indicators=[
                    "Scalable business model proven",
                    "Multiple revenue streams",
                    "Dedicated departments forming",
                    "Process documentation needed"
                ],
                technology_requirements=[
                    "CRM system actively used",
                    "Project management workflows established",
                    "Basic reporting capabilities"
                ],
                new_capabilities=[
                    "marketing_automation",
                    "analytics_platform",
                    "customer_support",
                    "identity_management"
                ]
            ),

            StageGate(
                from_stage=MaturityStage.SCALING,
                to_stage=MaturityStage.ESTABLISHED,
                employee_count_min=200,
                revenue_threshold=10000000,  # $10M ARR
                customer_count_min=1000,
                business_indicators=[
                    "Market leadership position",
                    "Predictable revenue model",
                    "Formal governance needed",
                    "Compliance requirements increasing"
                ],
                technology_requirements=[
                    "Marketing automation optimized",
                    "Business intelligence active",
                    "Security controls implemented"
                ],
                compliance_requirements=[
                    "SOC 2 Type II",
                    "Industry-specific compliance"
                ],
                new_capabilities=[
                    "enterprise_crm",
                    "compliance_management",
                    "security_monitoring",
                    "devops_platform"
                ]
            ),

            StageGate(
                from_stage=MaturityStage.ESTABLISHED,
                to_stage=MaturityStage.ENTERPRISE,
                employee_count_min=1000,
                revenue_threshold=50000000,  # $50M ARR
                customer_count_min=5000,
                business_indicators=[
                    "Multiple product lines",
                    "Global operations",
                    "Complex supply chains",
                    "Advanced analytics needs"
                ],
                technology_requirements=[
                    "Enterprise-grade security",
                    "Comprehensive compliance program",
                    "Advanced integration capabilities"
                ],
                compliance_requirements=[
                    "ISO 27001",
                    "Industry certifications",
                    "Global data protection compliance"
                ],
                new_capabilities=[
                    "erp_system",
                    "ai_ml_platform",
                    "api_management"
                ]
            )
        ]

    def _define_integration_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Define common integration patterns between capabilities"""

        return {
            "crm_marketing_sync": {
                "capabilities": ["basic_crm", "marketing_automation"],
                "pattern": "bidirectional_sync",
                "description": "Sync leads and contacts between CRM and marketing automation",
                "complexity": IntegrationComplexity.MODERATE,
                "business_value": "Unified customer journey tracking"
            },

            "financial_analytics": {
                "capabilities": ["advanced_accounting", "analytics_platform"],
                "pattern": "data_flow",
                "description": "Financial data flows to analytics for business intelligence",
                "complexity": IntegrationComplexity.MODERATE,
                "business_value": "Financial performance insights"
            },

            "hr_identity_integration": {
                "capabilities": ["hr_management", "identity_management"],
                "pattern": "provisioning",
                "description": "Automatic user provisioning and deprovisioning",
                "complexity": IntegrationComplexity.COMPLEX,
                "business_value": "Automated access management and security"
            },

            "support_crm_integration": {
                "capabilities": ["customer_support", "enterprise_crm"],
                "pattern": "unified_customer_view",
                "description": "Unified customer view across sales and support",
                "complexity": IntegrationComplexity.MODERATE,
                "business_value": "360-degree customer understanding"
            },

            "security_monitoring_integration": {
                "capabilities": ["security_monitoring", "identity_management", "compliance_management"],
                "pattern": "security_orchestration",
                "description": "Integrated security monitoring and compliance reporting",
                "complexity": IntegrationComplexity.ADVANCED,
                "business_value": "Comprehensive security posture and compliance"
            }
        }

    def assess_organization_maturity(self, org_data: Dict[str, Any]) -> Tuple[MaturityStage, List[str]]:
        """
        Assess an organization's current maturity stage based on provided data

        Args:
            org_data: Dictionary containing org metrics like employee_count, revenue, etc.

        Returns:
            Tuple of (current_stage, recommendations)
        """

        employee_count = org_data.get('employee_count', 0)
        revenue = org_data.get('annual_revenue', 0)
        customer_count = org_data.get('customer_count', 0)
        current_tools = org_data.get('current_technology_tools', [])

        # Determine stage based on quantitative metrics
        current_stage = MaturityStage.STARTUP

        for stage_gate in self.stage_gates:
            if (employee_count >= stage_gate.employee_count_min and
                revenue >= stage_gate.revenue_threshold and
                customer_count >= stage_gate.customer_count_min):
                current_stage = stage_gate.to_stage

        # Generate recommendations
        recommendations = self._generate_stage_recommendations(current_stage, current_tools)

        return current_stage, recommendations

    def _generate_stage_recommendations(self, stage: MaturityStage, current_tools: List[str]) -> List[str]:
        """Generate technology recommendations for the current stage"""

        recommendations = []

        # Get all capabilities for current stage and below
        relevant_capabilities = [
            cap for cap in self.capabilities.values()
            if cap.required_stage.value <= stage.value or cap.required_stage == stage
        ]

        # Sort by priority and stage
        relevant_capabilities.sort(key=lambda x: (
            x.required_stage.value,
            {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.priority]
        ))

        for capability in relevant_capabilities:
            # Check if any of the typical solutions are already implemented
            has_solution = any(
                tool.lower() in [sol.lower() for sol in capability.typical_solutions]
                for tool in current_tools
            )

            if not has_solution:
                recommendations.append(f"{capability.name}: {capability.description}")

        return recommendations

    def get_technology_roadmap(self, current_stage: MaturityStage, target_stage: MaturityStage) -> Dict[str, Any]:
        """Generate a technology roadmap from current to target maturity stage"""

        roadmap = {
            "current_stage": current_stage.value,
            "target_stage": target_stage.value,
            "phases": [],
            "total_estimated_cost": 0,
            "total_timeline_days": 0
        }

        # Get all stages between current and target
        stages = list(MaturityStage)
        current_idx = stages.index(current_stage)
        target_idx = stages.index(target_stage)

        for stage_idx in range(current_idx, target_idx + 1):
            stage = stages[stage_idx]

            # Get capabilities for this stage
            stage_capabilities = [
                cap for cap in self.capabilities.values()
                if cap.required_stage == stage
            ]

            if stage_capabilities:
                phase = {
                    "stage": stage.value,
                    "capabilities": [],
                    "estimated_cost": 0,
                    "timeline_days": 0
                }

                for cap in sorted(stage_capabilities, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.priority]):
                    cap_info = {
                        "name": cap.name,
                        "priority": cap.priority,
                        "typical_solutions": cap.typical_solutions,
                        "setup_time_days": cap.setup_time_days,
                        "monthly_cost_range": cap.monthly_cost_range,
                        "integration_complexity": cap.integration_complexity.value,
                        "prerequisites": cap.prerequisites
                    }

                    phase["capabilities"].append(cap_info)
                    phase["estimated_cost"] += cap.monthly_cost_range[1] * 12  # Annual cost estimate
                    phase["timeline_days"] = max(phase["timeline_days"], cap.setup_time_days)

                roadmap["phases"].append(phase)
                roadmap["total_estimated_cost"] += phase["estimated_cost"]
                roadmap["total_timeline_days"] += phase["timeline_days"]

        return roadmap