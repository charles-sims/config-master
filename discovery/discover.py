#!/usr/bin/env python3
"""
ConfigMaster Discovery Engine

Discovers applications across different environments and platforms.
"""

import json
import logging
import os
import time
from typing import List, Dict, Any
from datetime import datetime
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from models import DiscoveryResult, Application
from scanners import DockerScanner, KubernetesScanner, ProcessScanner, AIPlatformScanner

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()
app = typer.Typer()

class DiscoveryEngine:
    """Main discovery engine that orchestrates all scanners."""

    def __init__(self):
        # Load AI scanner configuration
        ai_config = {
            'platforms': ['HubSpot', 'Salesforce', 'Slack', 'Asana', 'Notion'],
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'exa_api_key': os.getenv('EXA_API_KEY'),
            'firecrawl_api_key': os.getenv('FIRECRAWL_API_KEY')
        }

        self.scanners = [
            ProcessScanner({}),
            DockerScanner({}),
            KubernetesScanner({}),
            AIPlatformScanner(ai_config)
        ]

    def discover_all(self) -> List[DiscoveryResult]:
        """Run all available scanners."""
        results = []

        console.print("[bold blue]Starting application discovery...[/bold blue]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            for scanner in self.scanners:
                scanner_name = scanner.__class__.__name__

                if not scanner.can_scan():
                    console.print(f"[yellow]Skipping {scanner_name} (not available)[/yellow]")
                    continue

                task = progress.add_task(f"Scanning with {scanner_name}...", total=None)

                try:
                    result = scanner.scan()
                    results.append(result)

                    app_count = len(result.applications)
                    error_count = len(result.errors)

                    console.print(f"[green]✓ {scanner_name}: Found {app_count} applications")
                    if error_count > 0:
                        console.print(f"[yellow]  {error_count} errors occurred[/yellow]")

                except Exception as e:
                    console.print(f"[red]✗ {scanner_name}: {str(e)}[/red]")
                    logger.error(f"Scanner {scanner_name} failed: {e}")

                progress.remove_task(task)

        return results

    def display_results(self, results: List[DiscoveryResult]):
        """Display discovery results in a nice table."""
        all_apps = []
        total_errors = 0

        for result in results:
            all_apps.extend(result.applications)
            total_errors += len(result.errors)

        if not all_apps:
            console.print("[yellow]No applications discovered[/yellow]")
            return

        # Create summary table
        table = Table(title="Discovered Applications")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Environment", style="green")
        table.add_column("Host:Port", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Source", style="dim")

        for app in all_apps:
            host_port = f"{app.host or 'N/A'}:{app.port}" if app.port else app.host or "N/A"
            source = "Docker" if app.container_id else "K8s" if app.k8s_namespace else "Process"

            status_color = "green" if app.health_status in ['healthy', 'running'] else "red"

            table.add_row(
                app.name,
                app.type.replace('_', ' ').title(),
                app.environment.title(),
                host_port,
                f"[{status_color}]{app.health_status}[/{status_color}]",
                source
            )

        console.print(table)

        # Display summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"Total applications: {len(all_apps)}")
        console.print(f"Total errors: {total_errors}")

        # Group by type
        type_counts = {}
        for app in all_apps:
            type_counts[app.type] = type_counts.get(app.type, 0) + 1

        console.print(f"\n[bold]By Type:[/bold]")
        for app_type, count in sorted(type_counts.items()):
            console.print(f"  {app_type.replace('_', ' ').title()}: {count}")

    def export_results(self, results: List[DiscoveryResult], output_file: str):
        """Export discovery results to JSON file."""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_applications': sum(len(r.applications) for r in results),
            'total_errors': sum(len(r.errors) for r in results),
            'results': []
        }

        for result in results:
            result_data = {
                'scanner': result.target,
                'scan_duration': result.scan_duration,
                'applications': [app.dict() for app in result.applications],
                'errors': result.errors
            }
            export_data['results'].append(result_data)

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        console.print(f"[green]Results exported to {output_file}[/green]")

@app.command()
def scan(
    output: str = typer.Option(None, "--output", "-o", help="Output file for JSON results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Scan for applications across all available platforms."""

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    engine = DiscoveryEngine()

    # Run discovery
    start_time = time.time()
    results = engine.discover_all()
    total_time = time.time() - start_time

    # Display results
    engine.display_results(results)

    console.print(f"\n[dim]Discovery completed in {total_time:.2f} seconds[/dim]")

    # Export if requested
    if output:
        engine.export_results(results, output)

@app.command()
def list_scanners():
    """List available scanners and their status."""

    table = Table(title="Available Scanners")
    table.add_column("Scanner", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Description")

    scanners = [
        (ProcessScanner({}), "Scans running processes for applications"),
        (DockerScanner({}), "Scans Docker containers"),
        (KubernetesScanner({}), "Scans Kubernetes deployments and services")
    ]

    for scanner, description in scanners:
        status = "[green]Available[/green]" if scanner.can_scan() else "[red]Not Available[/red]"
        table.add_row(scanner.__class__.__name__, status, description)

    console.print(table)

if __name__ == "__main__":
    app()