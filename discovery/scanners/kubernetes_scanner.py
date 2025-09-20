from typing import List, Dict, Any
import time
import logging
from kubernetes import client, config
from .base import BaseScanner
from ..models import Application, AppType, Environment, ConfigurationItem

logger = logging.getLogger(__name__)

class KubernetesScanner(BaseScanner):
    """Scanner for Kubernetes deployments and services."""

    def can_scan(self) -> bool:
        """Check if Kubernetes is available."""
        try:
            config.load_incluster_config()
            return True
        except:
            try:
                config.load_kube_config()
                return True
            except Exception as e:
                logger.debug(f"Kubernetes not available: {e}")
                return False

    def scan(self) -> List[Application]:
        """Scan Kubernetes cluster for applications."""
        start_time = time.time()
        applications = []
        errors = []

        try:
            # Load Kubernetes config
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()

            v1 = client.CoreV1Api()
            apps_v1 = client.AppsV1Api()

            # Get all namespaces
            namespaces = v1.list_namespace()

            for namespace in namespaces.items:
                namespace_name = namespace.metadata.name

                # Skip system namespaces
                if namespace_name.startswith('kube-'):
                    continue

                try:
                    # Get deployments
                    deployments = apps_v1.list_namespaced_deployment(namespace_name)
                    for deployment in deployments.items:
                        app = self._analyze_deployment(deployment, namespace_name, v1)
                        if app:
                            applications.append(app)

                    # Get services
                    services = v1.list_namespaced_service(namespace_name)
                    for service in services.items:
                        app = self._analyze_service(service, namespace_name)
                        if app:
                            applications.append(app)

                except Exception as e:
                    errors.append(f"Error scanning namespace {namespace_name}: {str(e)}")
                    logger.error(f"Error scanning namespace {namespace_name}: {e}")

        except Exception as e:
            errors.append(f"Error connecting to Kubernetes: {str(e)}")
            logger.error(f"Error connecting to Kubernetes: {e}")

        scan_duration = time.time() - start_time
        return self._create_result(applications, errors, scan_duration)

    def _analyze_deployment(self, deployment, namespace: str, v1_client) -> Application:
        """Analyze a Kubernetes deployment."""
        try:
            metadata = deployment.metadata
            spec = deployment.spec
            status = deployment.status

            name = metadata.name
            labels = metadata.labels or {}
            annotations = metadata.annotations or {}

            # Get container information
            containers = spec.template.spec.containers
            main_container = containers[0] if containers else None

            if not main_container:
                return None

            # Extract environment variables
            env_vars = {}
            config_items = []

            if main_container.env:
                for env_var in main_container.env:
                    value = env_var.value or 'from_secret'
                    env_vars[env_var.name] = value

                    is_secret = env_var.value_from is not None
                    config_items.append(ConfigurationItem(
                        key=env_var.name,
                        value='***REDACTED***' if is_secret else value,
                        is_secret=is_secret,
                        source='k8s_env'
                    ))

            # Extract ports
            ports = []
            if main_container.ports:
                ports = [port.container_port for port in main_container.ports]

            # Detect application type
            image = main_container.image
            app_type = self._detect_app_type_from_image(image, ports, env_vars)

            # Get replica status
            desired_replicas = spec.replicas or 1
            ready_replicas = status.ready_replicas or 0
            health_status = 'healthy' if ready_replicas == desired_replicas else 'degraded'

            return Application(
                id=f"k8s_{namespace}_{name}",
                name=name,
                type=app_type,
                environment=self._detect_environment_from_namespace(namespace),
                version=labels.get('version') or annotations.get('version') or 'unknown',
                description=f"Kubernetes deployment in {namespace}",
                k8s_namespace=namespace,
                k8s_deployment=name,
                port=ports[0] if ports else None,
                configuration=config_items,
                environment_variables=env_vars,
                is_active=ready_replicas > 0,
                health_status=health_status,
                repository_url=annotations.get('repository'),
                maintainer=annotations.get('maintainer')
            )

        except Exception as e:
            logger.error(f"Error analyzing deployment {metadata.name}: {e}")
            return None

    def _analyze_service(self, service, namespace: str) -> Application:
        """Analyze a Kubernetes service."""
        try:
            metadata = service.metadata
            spec = service.spec

            # Skip if no selector (might be external service)
            if not spec.selector:
                return None

            name = metadata.name
            labels = metadata.labels or {}

            # Extract ports
            ports = []
            if spec.ports:
                ports = [port.port for port in spec.ports]

            service_type = spec.type or 'ClusterIP'

            return Application(
                id=f"k8s_service_{namespace}_{name}",
                name=f"{name}-service",
                type=AppType.API_SERVICE,
                environment=self._detect_environment_from_namespace(namespace),
                description=f"Kubernetes {service_type} service in {namespace}",
                k8s_namespace=namespace,
                port=ports[0] if ports else None,
                is_active=True,
                health_status='active'
            )

        except Exception as e:
            logger.error(f"Error analyzing service {metadata.name}: {e}")
            return None

    def _detect_app_type_from_image(self, image: str, ports: List[int], env_vars: Dict[str, str]) -> AppType:
        """Detect application type from container image."""
        image_lower = image.lower()

        # Database containers
        if any(db in image_lower for db in ['postgres', 'mysql', 'redis', 'mongo', 'elasticsearch']):
            return AppType.DATABASE

        # Web applications
        if any(framework in image_lower for framework in ['nginx', 'apache', 'frontend']):
            return AppType.WEB_APPLICATION

        # API services
        if any(framework in image_lower for framework in ['api', 'backend', 'service']):
            return AppType.API_SERVICE

        # Check ports for web services
        if any(port in ports for port in [80, 443, 8080, 3000, 8000]):
            return AppType.WEB_APPLICATION

        return AppType.MICROSERVICE

    def _detect_environment_from_namespace(self, namespace: str) -> Environment:
        """Detect environment from namespace name."""
        namespace_lower = namespace.lower()

        if 'prod' in namespace_lower:
            return Environment.PRODUCTION
        elif 'stag' in namespace_lower:
            return Environment.STAGING
        elif 'test' in namespace_lower:
            return Environment.TESTING
        else:
            return Environment.DEVELOPMENT