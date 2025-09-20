from typing import List, Dict, Any
import psutil
import time
import logging
import os
from .base import BaseScanner
from ..models import Application, AppType, Environment, ConfigurationItem

logger = logging.getLogger(__name__)

class ProcessScanner(BaseScanner):
    """Scanner for running processes and system applications."""

    def can_scan(self) -> bool:
        """Check if process scanning is available."""
        return True  # psutil should work on all platforms

    def scan(self) -> List[Application]:
        """Scan running processes for applications."""
        start_time = time.time()
        applications = []
        errors = []

        try:
            # Get all running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Filter and analyze interesting processes
            for proc_info in processes:
                try:
                    app = self._analyze_process(proc_info)
                    if app:
                        applications.append(app)
                except Exception as e:
                    errors.append(f"Error analyzing process {proc_info.get('name', 'unknown')}: {str(e)}")

        except Exception as e:
            errors.append(f"Error scanning processes: {str(e)}")
            logger.error(f"Error scanning processes: {e}")

        scan_duration = time.time() - start_time
        return self._create_result(applications, errors, scan_duration)

    def _analyze_process(self, proc_info: Dict[str, Any]) -> Application:
        """Analyze a process and determine if it's an application."""
        name = proc_info.get('name', '')
        cmdline = proc_info.get('cmdline', [])
        connections = proc_info.get('connections', [])
        pid = proc_info.get('pid')

        # Skip system processes and common utilities
        if self._should_skip_process(name, cmdline):
            return None

        # Extract ports from network connections
        ports = []
        for conn in connections:
            if conn.status == 'LISTEN' and conn.laddr:
                ports.append(conn.laddr.port)

        # Only include processes that listen on ports or are known applications
        if not ports and not self._is_known_application(name, cmdline):
            return None

        # Try to get environment variables for the process
        env_vars = {}
        try:
            proc = psutil.Process(pid)
            env_vars = proc.environ()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        # Extract configuration from environment
        config_items = []
        for key, value in env_vars.items():
            # Skip common system variables
            if key in ['PATH', 'HOME', 'USER', 'SHELL', 'TERM']:
                continue

            is_secret = any(secret_key in key.lower() for secret_key in [
                'password', 'secret', 'key', 'token', 'api_key', 'private'
            ])

            config_items.append(ConfigurationItem(
                key=key,
                value='***REDACTED***' if is_secret else value[:100],  # Truncate long values
                is_secret=is_secret,
                source='process_env'
            ))

        # Detect application type
        app_type = self._detect_app_type(name, ports, cmdline)

        # Create application
        app_name = self._extract_app_name(name, cmdline)

        return Application(
            id=f"process_{pid}",
            name=app_name,
            type=app_type,
            environment=Environment.DEVELOPMENT,  # Assume development for local processes
            description=f"Process: {' '.join(cmdline[:3])}..." if cmdline else f"Process: {name}",
            host='localhost',
            port=min(ports) if ports else None,
            configuration=config_items[:20],  # Limit config items
            environment_variables={k: v for k, v in list(env_vars.items())[:10]},  # Limit env vars
            is_active=True,
            health_status='running'
        )

    def _should_skip_process(self, name: str, cmdline: List[str]) -> bool:
        """Determine if process should be skipped."""
        name_lower = name.lower()

        # Skip system processes
        system_processes = [
            'kernel', 'init', 'systemd', 'kthreadd', 'migration', 'rcu_',
            'watchdog', 'sshd', 'dbus', 'NetworkManager', 'systemd-',
            'chrome', 'firefox', 'safari', 'code', 'terminal', 'finder',
            'dock', 'windowserver', 'loginwindow', 'launchd'
        ]

        if any(sys_proc in name_lower for sys_proc in system_processes):
            return True

        # Skip if no command line
        if not cmdline:
            return True

        # Skip scripts and interpreters without interesting arguments
        if name_lower in ['python', 'python3', 'node', 'java', 'ruby'] and len(cmdline) < 2:
            return True

        return False

    def _is_known_application(self, name: str, cmdline: List[str]) -> bool:
        """Check if this is a known application even without listening ports."""
        name_lower = name.lower()
        cmdline_str = ' '.join(cmdline).lower()

        known_apps = [
            'postgres', 'mysql', 'redis', 'mongo', 'elasticsearch',
            'nginx', 'apache', 'httpd', 'caddy',
            'docker', 'containerd', 'kubectl'
        ]

        return any(app in name_lower or app in cmdline_str for app in known_apps)

    def _extract_app_name(self, process_name: str, cmdline: List[str]) -> str:
        """Extract a meaningful application name."""
        # If cmdline has script name, use that
        if len(cmdline) > 1:
            script_path = cmdline[1]
            if '/' in script_path:
                script_name = os.path.basename(script_path)
                if script_name.endswith('.py'):
                    return script_name[:-3]
                elif script_name.endswith('.js'):
                    return script_name[:-3]
                else:
                    return script_name

        # Use process name
        return process_name