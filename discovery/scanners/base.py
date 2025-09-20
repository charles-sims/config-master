from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time
import logging

# Handle imports for both direct execution and package usage
try:
    from ..models import Application, DiscoveryResult
except ImportError:
    from models import Application, DiscoveryResult

logger = logging.getLogger(__name__)

class BaseScanner(ABC):
    """Base class for all application scanners."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def scan(self) -> DiscoveryResult:
        """Scan for applications and return discovery result."""
        pass

    @abstractmethod
    def can_scan(self) -> bool:
        """Check if this scanner can run in current environment."""
        pass

    def _create_result(self, applications: List[Application], errors: List[str] = None, scan_duration: float = 0) -> DiscoveryResult:
        """Helper to create discovery result."""
        return DiscoveryResult(
            target=self.name,
            applications=applications,
            errors=errors or [],
            scan_duration=scan_duration
        )

    def _extract_config_from_env(self, env_vars: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract configuration items from environment variables."""
        configs = []
        for key, value in env_vars.items():
            is_secret = any(secret_key in key.lower() for secret_key in [
                'password', 'secret', 'key', 'token', 'api_key', 'private'
            ])
            configs.append({
                'key': key,
                'value': '***REDACTED***' if is_secret else value,
                'is_secret': is_secret,
                'source': 'environment'
            })
        return configs

    def _detect_app_type(self, process_name: str, ports: List[int], files: List[str]) -> str:
        """Detect application type based on process name, ports, and files."""
        process_lower = process_name.lower()

        # Database detection
        if any(db in process_lower for db in ['postgres', 'mysql', 'redis', 'mongo', 'elasticsearch']):
            return 'database'

        # Web servers
        if any(server in process_lower for server in ['nginx', 'apache', 'httpd']):
            return 'web_application'

        # Application servers
        if any(server in process_lower for server in ['node', 'python', 'java', 'php', 'ruby']):
            # Check for common web ports
            if any(port in ports for port in [80, 443, 8080, 3000, 8000, 5000]):
                return 'web_application'
            return 'api_service'

        # Container runtime
        if 'docker' in process_lower or 'containerd' in process_lower:
            return 'container'

        return 'custom_tool'

    def _health_check(self, url: str) -> str:
        """Perform basic health check on application."""
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return 'healthy'
            else:
                return f'unhealthy (HTTP {response.status_code})'
        except Exception as e:
            return f'unreachable ({str(e)})'