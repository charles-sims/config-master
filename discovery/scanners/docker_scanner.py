from typing import List, Dict, Any
import docker
import logging
from .base import BaseScanner
from ..models import Application, AppType, Environment, ConfigurationItem

logger = logging.getLogger(__name__)

class DockerScanner(BaseScanner):
    """Scanner for Docker containers."""

    def can_scan(self) -> bool:
        """Check if Docker is available."""
        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception as e:
            logger.debug(f"Docker not available: {e}")
            return False

    def scan(self) -> List[Application]:
        """Scan Docker containers for applications."""
        start_time = time.time()
        applications = []
        errors = []

        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)

            for container in containers:
                try:
                    app = self._analyze_container(container)
                    if app:
                        applications.append(app)
                except Exception as e:
                    errors.append(f"Error analyzing container {container.name}: {str(e)}")
                    logger.error(f"Error analyzing container {container.name}: {e}")

        except Exception as e:
            errors.append(f"Error connecting to Docker: {str(e)}")
            logger.error(f"Error connecting to Docker: {e}")

        scan_duration = time.time() - start_time
        return self._create_result(applications, errors, scan_duration)

    def _analyze_container(self, container) -> Application:
        """Analyze a Docker container and create Application object."""
        try:
            # Get container details
            container.reload()
            attrs = container.attrs

            # Extract basic info
            name = container.name
            image = attrs.get('Config', {}).get('Image', 'unknown')
            state = attrs.get('State', {})
            is_running = state.get('Running', False)

            # Extract ports
            ports = []
            port_bindings = attrs.get('NetworkSettings', {}).get('Ports', {})
            for port_spec, bindings in port_bindings.items():
                if bindings:
                    port = port_spec.split('/')[0]
                    ports.append(int(port))

            # Extract environment variables
            env_vars = {}
            env_list = attrs.get('Config', {}).get('Env', [])
            for env_var in env_list:
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    env_vars[key] = value

            # Extract configuration
            config_items = []
            for key, value in env_vars.items():
                is_secret = any(secret_key in key.lower() for secret_key in [
                    'password', 'secret', 'key', 'token', 'api_key', 'private'
                ])
                config_items.append(ConfigurationItem(
                    key=key,
                    value='***REDACTED***' if is_secret else value,
                    is_secret=is_secret,
                    source='docker_env'
                ))

            # Detect application type
            app_type = self._detect_container_type(image, ports, env_vars)

            # Extract labels for metadata
            labels = attrs.get('Config', {}).get('Labels') or {}

            return Application(
                id=f"docker_{container.id[:12]}",
                name=name,
                type=app_type,
                environment=self._detect_environment(name, labels),
                version=labels.get('version') or 'unknown',
                description=f"Docker container running {image}",
                host='localhost',
                port=ports[0] if ports else None,
                container_id=container.id,
                configuration=config_items,
                environment_variables=env_vars,
                is_active=is_running,
                health_status='running' if is_running else 'stopped',
                repository_url=labels.get('repository'),
                maintainer=labels.get('maintainer')
            )

        except Exception as e:
            logger.error(f"Error analyzing container {container.name}: {e}")
            return None

    def _detect_container_type(self, image: str, ports: List[int], env_vars: Dict[str, str]) -> AppType:
        """Detect application type from container image and configuration."""
        image_lower = image.lower()

        # Database containers
        if any(db in image_lower for db in ['postgres', 'mysql', 'redis', 'mongo', 'elasticsearch', 'cassandra']):
            return AppType.DATABASE

        # Web servers
        if any(server in image_lower for server in ['nginx', 'apache', 'httpd']):
            return AppType.WEB_APPLICATION

        # Application frameworks
        if any(framework in image_lower for framework in ['node', 'python', 'java', 'php', 'ruby', 'go']):
            if any(port in ports for port in [80, 443, 8080, 3000, 8000, 5000]):
                return AppType.WEB_APPLICATION
            return AppType.API_SERVICE

        # Check environment variables for clues
        if any('database' in key.lower() for key in env_vars.keys()):
            return AppType.API_SERVICE

        return AppType.CONTAINER

    def _detect_environment(self, name: str, labels: Dict[str, str]) -> Environment:
        """Detect environment from container name and labels."""
        name_lower = name.lower()

        if 'prod' in name_lower or labels.get('environment') == 'production':
            return Environment.PRODUCTION
        elif 'stag' in name_lower or labels.get('environment') == 'staging':
            return Environment.STAGING
        elif 'test' in name_lower or labels.get('environment') == 'testing':
            return Environment.TESTING
        else:
            return Environment.DEVELOPMENT