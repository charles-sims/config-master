from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
import time
import logging
from datetime import datetime, timedelta
import ssl
import socket
import json

logger = logging.getLogger(__name__)

class IntegrationStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class ValidationType(str, Enum):
    HTTP_HEALTH_CHECK = "http_health_check"
    TCP_CONNECTION = "tcp_connection"
    DATABASE_CONNECTION = "database_connection"
    API_ENDPOINT = "api_endpoint"
    WEBHOOK_VALIDATION = "webhook_validation"
    FILE_SYSTEM_CHECK = "file_system_check"

@dataclass
class ValidationResult:
    integration_name: str
    status: IntegrationStatus
    response_time: float
    message: str
    details: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class BaseIntegrationValidator(ABC):
    """Base class for all integration validators."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    @abstractmethod
    async def validate(self, integration: Dict[str, Any]) -> ValidationResult:
        """Validate an integration and return result."""
        pass

    def _create_result(
        self,
        integration_name: str,
        status: IntegrationStatus,
        response_time: float,
        message: str,
        details: Dict[str, Any] = None
    ) -> ValidationResult:
        """Helper to create validation result."""
        return ValidationResult(
            integration_name=integration_name,
            status=status,
            response_time=response_time,
            message=message,
            details=details or {}
        )

class HTTPHealthCheckValidator(BaseIntegrationValidator):
    """Validates HTTP health check endpoints."""

    async def validate(self, integration: Dict[str, Any]) -> ValidationResult:
        """Validate HTTP health check endpoint."""
        name = integration.get('name', 'Unknown')
        url = integration.get('health_check_url')

        if not url:
            return self._create_result(
                name,
                IntegrationStatus.UNKNOWN,
                0.0,
                "No health check URL configured"
            )

        start_time = time.time()

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    response_time = time.time() - start_time
                    response_text = await response.text()

                    if response.status == 200:
                        return self._create_result(
                            name,
                            IntegrationStatus.HEALTHY,
                            response_time,
                            f"Health check passed (HTTP {response.status})",
                            {
                                "status_code": response.status,
                                "response_size": len(response_text),
                                "headers": dict(response.headers)
                            }
                        )
                    elif 200 <= response.status < 300:
                        return self._create_result(
                            name,
                            IntegrationStatus.HEALTHY,
                            response_time,
                            f"Health check passed (HTTP {response.status})",
                            {"status_code": response.status}
                        )
                    elif 500 <= response.status < 600:
                        return self._create_result(
                            name,
                            IntegrationStatus.UNHEALTHY,
                            response_time,
                            f"Server error (HTTP {response.status})",
                            {"status_code": response.status, "response": response_text[:500]}
                        )
                    else:
                        return self._create_result(
                            name,
                            IntegrationStatus.DEGRADED,
                            response_time,
                            f"Unexpected status (HTTP {response.status})",
                            {"status_code": response.status}
                        )

        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNHEALTHY,
                response_time,
                f"Health check timed out after {self.timeout}s"
            )

        except aiohttp.ClientError as e:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNHEALTHY,
                response_time,
                f"Connection error: {str(e)}"
            )

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNKNOWN,
                response_time,
                f"Validation error: {str(e)}"
            )

class TCPConnectionValidator(BaseIntegrationValidator):
    """Validates TCP connections to services."""

    async def validate(self, integration: Dict[str, Any]) -> ValidationResult:
        """Validate TCP connection."""
        name = integration.get('name', 'Unknown')
        config = integration.get('configuration', {})
        host = config.get('host') or integration.get('target_app')
        port = config.get('port')

        if not host or not port:
            return self._create_result(
                name,
                IntegrationStatus.UNKNOWN,
                0.0,
                "Host or port not configured"
            )

        start_time = time.time()

        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            result = sock.connect_ex((host, int(port)))
            response_time = time.time() - start_time

            sock.close()

            if result == 0:
                return self._create_result(
                    name,
                    IntegrationStatus.HEALTHY,
                    response_time,
                    f"TCP connection successful to {host}:{port}",
                    {"host": host, "port": port}
                )
            else:
                return self._create_result(
                    name,
                    IntegrationStatus.UNHEALTHY,
                    response_time,
                    f"TCP connection failed to {host}:{port}",
                    {"host": host, "port": port, "error_code": result}
                )

        except socket.timeout:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNHEALTHY,
                response_time,
                f"TCP connection timed out to {host}:{port}"
            )

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNKNOWN,
                response_time,
                f"TCP validation error: {str(e)}"
            )

class DatabaseConnectionValidator(BaseIntegrationValidator):
    """Validates database connections."""

    async def validate(self, integration: Dict[str, Any]) -> ValidationResult:
        """Validate database connection."""
        name = integration.get('name', 'Unknown')
        config = integration.get('configuration', {})
        db_type = config.get('type', '').lower()

        if db_type == 'postgresql':
            return await self._validate_postgresql(name, config)
        elif db_type == 'mysql':
            return await self._validate_mysql(name, config)
        elif db_type == 'redis':
            return await self._validate_redis(name, config)
        elif db_type == 'mongodb':
            return await self._validate_mongodb(name, config)
        else:
            return self._create_result(
                name,
                IntegrationStatus.UNKNOWN,
                0.0,
                f"Unsupported database type: {db_type}"
            )

    async def _validate_postgresql(self, name: str, config: Dict[str, Any]) -> ValidationResult:
        """Validate PostgreSQL connection."""
        start_time = time.time()

        try:
            import asyncpg

            connection_string = (
                f"postgresql://{config.get('username')}:{config.get('password')}"
                f"@{config.get('host')}:{config.get('port', 5432)}/{config.get('database')}"
            )

            conn = await asyncpg.connect(connection_string)
            await conn.execute('SELECT 1')
            await conn.close()

            response_time = time.time() - start_time

            return self._create_result(
                name,
                IntegrationStatus.HEALTHY,
                response_time,
                "PostgreSQL connection successful",
                {"database": config.get('database'), "host": config.get('host')}
            )

        except ImportError:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNKNOWN,
                response_time,
                "asyncpg library not installed"
            )

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNHEALTHY,
                response_time,
                f"PostgreSQL connection failed: {str(e)}"
            )

    async def _validate_redis(self, name: str, config: Dict[str, Any]) -> ValidationResult:
        """Validate Redis connection."""
        start_time = time.time()

        try:
            import aioredis

            redis = aioredis.from_url(
                f"redis://{config.get('host')}:{config.get('port', 6379)}"
            )

            await redis.ping()
            await redis.close()

            response_time = time.time() - start_time

            return self._create_result(
                name,
                IntegrationStatus.HEALTHY,
                response_time,
                "Redis connection successful",
                {"host": config.get('host'), "port": config.get('port', 6379)}
            )

        except ImportError:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNKNOWN,
                response_time,
                "aioredis library not installed"
            )

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNHEALTHY,
                response_time,
                f"Redis connection failed: {str(e)}"
            )

    async def _validate_mysql(self, name: str, config: Dict[str, Any]) -> ValidationResult:
        """Validate MySQL connection using TCP check (simplified)."""
        # Fall back to TCP connection check for MySQL
        tcp_validator = TCPConnectionValidator(self.timeout)
        tcp_config = {
            'name': name,
            'configuration': {
                'host': config.get('host'),
                'port': config.get('port', 3306)
            }
        }
        return await tcp_validator.validate(tcp_config)

    async def _validate_mongodb(self, name: str, config: Dict[str, Any]) -> ValidationResult:
        """Validate MongoDB connection using TCP check (simplified)."""
        # Fall back to TCP connection check for MongoDB
        tcp_validator = TCPConnectionValidator(self.timeout)
        tcp_config = {
            'name': name,
            'configuration': {
                'host': config.get('host'),
                'port': config.get('port', 27017)
            }
        }
        return await tcp_validator.validate(tcp_config)

class APIEndpointValidator(BaseIntegrationValidator):
    """Validates API endpoints."""

    async def validate(self, integration: Dict[str, Any]) -> ValidationResult:
        """Validate API endpoint."""
        name = integration.get('name', 'Unknown')
        config = integration.get('configuration', {})
        endpoint = config.get('endpoint')
        method = config.get('method', 'GET').upper()
        headers = config.get('headers', {})
        auth_config = config.get('authentication', {})

        if not endpoint:
            return self._create_result(
                name,
                IntegrationStatus.UNKNOWN,
                0.0,
                "No API endpoint configured"
            )

        start_time = time.time()

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)

            # Prepare headers
            request_headers = headers.copy()

            # Add authentication
            if auth_config.get('type') == 'bearer_token':
                request_headers['Authorization'] = f"Bearer {auth_config.get('token')}"
            elif auth_config.get('type') == 'api_key':
                key_header = auth_config.get('header', 'X-API-Key')
                request_headers[key_header] = auth_config.get('key')

            async with aiohttp.ClientSession(timeout=timeout, headers=request_headers) as session:
                async with session.request(method, endpoint) as response:
                    response_time = time.time() - start_time
                    response_text = await response.text()

                    if 200 <= response.status < 300:
                        return self._create_result(
                            name,
                            IntegrationStatus.HEALTHY,
                            response_time,
                            f"API endpoint accessible (HTTP {response.status})",
                            {
                                "status_code": response.status,
                                "method": method,
                                "response_size": len(response_text)
                            }
                        )
                    elif response.status == 401:
                        return self._create_result(
                            name,
                            IntegrationStatus.DEGRADED,
                            response_time,
                            "API endpoint requires authentication",
                            {"status_code": response.status}
                        )
                    elif response.status == 403:
                        return self._create_result(
                            name,
                            IntegrationStatus.DEGRADED,
                            response_time,
                            "API endpoint access forbidden",
                            {"status_code": response.status}
                        )
                    elif 500 <= response.status < 600:
                        return self._create_result(
                            name,
                            IntegrationStatus.UNHEALTHY,
                            response_time,
                            f"API endpoint server error (HTTP {response.status})",
                            {"status_code": response.status}
                        )
                    else:
                        return self._create_result(
                            name,
                            IntegrationStatus.DEGRADED,
                            response_time,
                            f"API endpoint returned HTTP {response.status}",
                            {"status_code": response.status}
                        )

        except Exception as e:
            response_time = time.time() - start_time
            return self._create_result(
                name,
                IntegrationStatus.UNHEALTHY,
                response_time,
                f"API validation error: {str(e)}"
            )

class IntegrationValidationEngine:
    """Main engine for validating application integrations."""

    def __init__(self):
        self.validators = {
            ValidationType.HTTP_HEALTH_CHECK: HTTPHealthCheckValidator(),
            ValidationType.TCP_CONNECTION: TCPConnectionValidator(),
            ValidationType.DATABASE_CONNECTION: DatabaseConnectionValidator(),
            ValidationType.API_ENDPOINT: APIEndpointValidator()
        }

    async def validate_integration(self, integration: Dict[str, Any]) -> ValidationResult:
        """Validate a single integration."""
        integration_type = integration.get('type', '').lower()

        # Determine validation type
        validation_type = self._determine_validation_type(integration_type, integration)

        if validation_type not in self.validators:
            return ValidationResult(
                integration_name=integration.get('name', 'Unknown'),
                status=IntegrationStatus.UNKNOWN,
                response_time=0.0,
                message=f"No validator available for type: {integration_type}"
            )

        validator = self.validators[validation_type]
        return await validator.validate(integration)

    async def validate_application_integrations(self, application: Dict[str, Any]) -> List[ValidationResult]:
        """Validate all integrations for an application."""
        integrations = application.get('integrations', [])

        if not integrations:
            return []

        # Validate all integrations concurrently
        tasks = [self.validate_integration(integration) for integration in integrations]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        validated_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ValidationResult(
                    integration_name=integrations[i].get('name', 'Unknown'),
                    status=IntegrationStatus.UNKNOWN,
                    response_time=0.0,
                    message=f"Validation exception: {str(result)}"
                )
                validated_results.append(error_result)
            else:
                validated_results.append(result)

        return validated_results

    def _determine_validation_type(self, integration_type: str, integration: Dict[str, Any]) -> ValidationType:
        """Determine the appropriate validation type for an integration."""
        # Check if health check URL is provided
        if integration.get('health_check_url'):
            return ValidationType.HTTP_HEALTH_CHECK

        # Determine by integration type
        if integration_type == 'database':
            return ValidationType.DATABASE_CONNECTION
        elif integration_type == 'api':
            return ValidationType.API_ENDPOINT
        elif integration_type in ['tcp', 'socket']:
            return ValidationType.TCP_CONNECTION
        else:
            # Default to TCP connection check
            return ValidationType.TCP_CONNECTION

    def calculate_integration_health_score(self, results: List[ValidationResult]) -> float:
        """Calculate overall health score for integrations (0-100)."""
        if not results:
            return 100.0  # No integrations means no integration issues

        healthy_count = sum(1 for result in results if result.status == IntegrationStatus.HEALTHY)
        return (healthy_count / len(results)) * 100

    def get_integration_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary of integration validation results."""
        if not results:
            return {
                'total_integrations': 0,
                'healthy': 0,
                'degraded': 0,
                'unhealthy': 0,
                'unknown': 0,
                'health_score': 100.0,
                'average_response_time': 0.0
            }

        status_counts = {
            'healthy': sum(1 for r in results if r.status == IntegrationStatus.HEALTHY),
            'degraded': sum(1 for r in results if r.status == IntegrationStatus.DEGRADED),
            'unhealthy': sum(1 for r in results if r.status == IntegrationStatus.UNHEALTHY),
            'unknown': sum(1 for r in results if r.status == IntegrationStatus.UNKNOWN)
        }

        avg_response_time = sum(r.response_time for r in results) / len(results)
        health_score = self.calculate_integration_health_score(results)

        return {
            'total_integrations': len(results),
            'health_score': health_score,
            'average_response_time': avg_response_time,
            **status_counts
        }