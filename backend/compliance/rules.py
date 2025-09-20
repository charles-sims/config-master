from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
import json

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RuleType(str, Enum):
    CONFIGURATION = "configuration"
    INTEGRATION = "integration"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class ComplianceResult:
    rule_id: str
    rule_name: str
    passed: bool
    severity: Severity
    description: str
    recommendation: str
    details: Dict[str, Any] = None

class BaseComplianceRule(ABC):
    """Base class for all compliance rules."""

    def __init__(self, rule_id: str, name: str, description: str, severity: Severity, rule_type: RuleType):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.severity = severity
        self.rule_type = rule_type

    @abstractmethod
    def evaluate(self, application: Dict[str, Any]) -> ComplianceResult:
        """Evaluate the rule against an application."""
        pass

    def _create_result(self, passed: bool, recommendation: str, details: Dict[str, Any] = None) -> ComplianceResult:
        """Helper to create compliance result."""
        return ComplianceResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            description=self.description,
            recommendation=recommendation,
            details=details or {}
        )

# Configuration Rules
class RequiredConfigurationRule(BaseComplianceRule):
    """Rule to check for required configuration keys."""

    def __init__(self, required_keys: List[str], app_types: List[str] = None):
        super().__init__(
            rule_id="config_required_keys",
            name="Required Configuration Keys",
            description="Checks that required configuration keys are present",
            severity=Severity.HIGH,
            rule_type=RuleType.CONFIGURATION
        )
        self.required_keys = required_keys
        self.app_types = app_types or []

    def evaluate(self, application: Dict[str, Any]) -> ComplianceResult:
        # Skip if app type doesn't match
        if self.app_types and application.get('type') not in self.app_types:
            return self._create_result(True, "Rule not applicable to this application type")

        configurations = application.get('configurations', [])
        config_keys = {config['key'] for config in configurations}

        missing_keys = [key for key in self.required_keys if key not in config_keys]

        if missing_keys:
            return self._create_result(
                False,
                f"Add missing configuration keys: {', '.join(missing_keys)}",
                {"missing_keys": missing_keys}
            )

        return self._create_result(True, "All required configuration keys are present")

class SecretManagementRule(BaseComplianceRule):
    """Rule to check that secrets are properly managed."""

    def __init__(self):
        super().__init__(
            rule_id="security_secret_management",
            name="Secret Management",
            description="Ensures secrets are marked as secret and not exposed in plain text",
            severity=Severity.CRITICAL,
            rule_type=RuleType.SECURITY
        )

    def evaluate(self, application: Dict[str, Any]) -> ComplianceResult:
        configurations = application.get('configurations', [])
        issues = []

        secret_patterns = [
            r'password', r'secret', r'key', r'token', r'api[_-]?key',
            r'private[_-]?key', r'access[_-]?token', r'auth[_-]?token'
        ]

        for config in configurations:
            key = config['key'].lower()
            value = str(config.get('value', ''))
            is_secret = config.get('is_secret', False)

            # Check if key suggests it's a secret
            is_likely_secret = any(re.search(pattern, key) for pattern in secret_patterns)

            if is_likely_secret and not is_secret:
                issues.append(f"'{config['key']}' appears to be a secret but is not marked as such")

            # Check for hardcoded secrets in values
            if not is_secret and value and len(value) > 10:
                # Simple heuristic for potential secrets
                if re.match(r'^[A-Za-z0-9+/=]{20,}$', value) or 'secret' in value.lower():
                    issues.append(f"'{config['key']}' may contain a hardcoded secret")

        if issues:
            return self._create_result(
                False,
                "Review and properly secure the identified secrets",
                {"issues": issues}
            )

        return self._create_result(True, "Secret management appears to be properly configured")

class EnvironmentVariableRule(BaseComplianceRule):
    """Rule to check environment variable best practices."""

    def __init__(self):
        super().__init__(
            rule_id="config_env_vars",
            name="Environment Variable Best Practices",
            description="Checks for proper environment variable naming and usage",
            severity=Severity.MEDIUM,
            rule_type=RuleType.CONFIGURATION
        )

    def evaluate(self, application: Dict[str, Any]) -> ComplianceResult:
        env_vars = application.get('environment_variables', {})
        issues = []

        for key, value in env_vars.items():
            # Check naming convention (should be UPPERCASE_WITH_UNDERSCORES)
            if not re.match(r'^[A-Z][A-Z0-9_]*$', key):
                issues.append(f"Environment variable '{key}' doesn't follow naming convention")

            # Check for empty values
            if not value or value.strip() == '':
                issues.append(f"Environment variable '{key}' has empty value")

        if issues:
            return self._create_result(
                False,
                "Fix environment variable naming and values",
                {"issues": issues}
            )

        return self._create_result(True, "Environment variables follow best practices")

# Documentation Rules
class DocumentationRule(BaseComplianceRule):
    """Rule to check for proper documentation."""

    def __init__(self):
        super().__init__(
            rule_id="docs_required",
            name="Documentation Required",
            description="Ensures applications have proper documentation",
            severity=Severity.MEDIUM,
            rule_type=RuleType.DOCUMENTATION
        )

    def evaluate(self, application: Dict[str, Any]) -> ComplianceResult:
        issues = []

        if not application.get('description'):
            issues.append("Application description is missing")

        if not application.get('documentation_url'):
            issues.append("Documentation URL is missing")

        if not application.get('repository_url'):
            issues.append("Repository URL is missing")

        if not application.get('maintainer'):
            issues.append("Maintainer information is missing")

        if issues:
            return self._create_result(
                False,
                "Add missing documentation and metadata",
                {"missing_items": issues}
            )

        return self._create_result(True, "Documentation requirements are met")

# Integration Rules
class HealthCheckRule(BaseComplianceRule):
    """Rule to check for health check endpoints."""

    def __init__(self):
        super().__init__(
            rule_id="integration_health_check",
            name="Health Check Endpoints",
            description="Ensures applications have health check endpoints",
            severity=Severity.HIGH,
            rule_type=RuleType.INTEGRATION
        )

    def evaluate(self, application: Dict[str, Any]) -> ComplianceResult:
        app_type = application.get('type')

        # Skip for databases and non-service applications
        if app_type in ['database', 'desktop_app', 'mobile_app']:
            return self._create_result(True, "Health checks not required for this application type")

        integrations = application.get('integrations', [])
        has_health_check = any(
            integration.get('health_check_url') for integration in integrations
        )

        # Check if application has a health endpoint based on common patterns
        host = application.get('host', 'localhost')
        port = application.get('port')

        if port and not has_health_check:
            # Suggest common health check endpoints
            suggestions = [
                f"http://{host}:{port}/health",
                f"http://{host}:{port}/healthz",
                f"http://{host}:{port}/ping",
                f"http://{host}:{port}/status"
            ]

            return self._create_result(
                False,
                f"Add health check endpoint. Consider: {', '.join(suggestions)}",
                {"suggested_endpoints": suggestions}
            )

        if has_health_check:
            return self._create_result(True, "Health check endpoint is configured")

        return self._create_result(
            False,
            "Configure health check monitoring for this application"
        )

# Performance Rules
class ResourceLimitsRule(BaseComplianceRule):
    """Rule to check for resource limits in containerized applications."""

    def __init__(self):
        super().__init__(
            rule_id="performance_resource_limits",
            name="Resource Limits",
            description="Ensures containerized applications have resource limits",
            severity=Severity.MEDIUM,
            rule_type=RuleType.PERFORMANCE
        )

    def evaluate(self, application: Dict[str, Any]) -> ComplianceResult:
        # Only apply to containerized applications
        if not (application.get('container_id') or application.get('k8s_namespace')):
            return self._create_result(True, "Resource limits not applicable to non-containerized applications")

        configurations = application.get('configurations', [])
        config_keys = {config['key'].lower() for config in configurations}

        resource_configs = [
            'memory_limit', 'cpu_limit', 'memory_request', 'cpu_request',
            'max_memory', 'max_cpu', 'limits_memory', 'limits_cpu'
        ]

        has_resource_config = any(key in config_keys for key in resource_configs)

        if not has_resource_config:
            return self._create_result(
                False,
                "Configure resource limits for better resource management",
                {"suggested_configs": ["MEMORY_LIMIT", "CPU_LIMIT"]}
            )

        return self._create_result(True, "Resource limits are configured")

class ComplianceEngine:
    """Main compliance engine that runs all rules against applications."""

    def __init__(self):
        self.rules = [
            RequiredConfigurationRule(['DATABASE_URL', 'PORT'], ['api_service', 'web_application']),
            SecretManagementRule(),
            EnvironmentVariableRule(),
            DocumentationRule(),
            HealthCheckRule(),
            ResourceLimitsRule()
        ]

    def evaluate_application(self, application: Dict[str, Any]) -> List[ComplianceResult]:
        """Evaluate all rules against an application."""
        results = []

        for rule in self.rules:
            try:
                result = rule.evaluate(application)
                results.append(result)
            except Exception as e:
                # Log error and continue with other rules
                error_result = ComplianceResult(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    passed=False,
                    severity=Severity.LOW,
                    description=f"Error evaluating rule: {str(e)}",
                    recommendation="Check rule configuration"
                )
                results.append(error_result)

        return results

    def calculate_compliance_score(self, results: List[ComplianceResult]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not results:
            return 0.0

        total_weight = 0
        weighted_score = 0

        severity_weights = {
            Severity.CRITICAL: 10,
            Severity.HIGH: 5,
            Severity.MEDIUM: 3,
            Severity.LOW: 1
        }

        for result in results:
            weight = severity_weights[result.severity]
            total_weight += weight

            if result.passed:
                weighted_score += weight

        return (weighted_score / total_weight) * 100 if total_weight > 0 else 0.0

    def get_recommendations(self, results: List[ComplianceResult]) -> List[Dict[str, Any]]:
        """Get prioritized recommendations based on compliance results."""
        failed_results = [r for r in results if not r.passed]

        # Sort by severity (critical first)
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
        failed_results.sort(key=lambda x: severity_order.index(x.severity))

        recommendations = []
        for result in failed_results:
            recommendations.append({
                'rule_id': result.rule_id,
                'rule_name': result.rule_name,
                'severity': result.severity,
                'recommendation': result.recommendation,
                'details': result.details
            })

        return recommendations