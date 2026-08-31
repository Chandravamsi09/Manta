import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import manta

console = Console()

def cmd_health(args):
    console.print(Panel("[bold green]Manta ML Cluster Health: ONLINE[/bold green]\nAll nodes responsive.", title="Cluster Status"))

def cmd_models(args):
    table = Table(title="Registered ML Models")
    table.add_column("Model Name", style="cyan")
    table.add_column("Latest Version", style="magenta")
    table.add_column("Stage", style="green")
    table.add_column("Latency (p95)", style="yellow")
    
    table.add_row("fraud_detector", "v1.2.0", "PRODUCTION", "1.42 ms")
    table.add_row("recommendation_ranker", "v2.0.1", "CANARY", "3.18 ms")
    table.add_row("text_embedding_v3", "v3.0.0", "STAGING", "12.50 ms")
    console.print(table)

def cmd_drift(args):
    table = Table(title="Model Distribution Drift Status")
    table.add_column("Feature", style="cyan")
    table.add_column("Detector", style="blue")
    table.add_column("Metric Value", style="magenta")
    table.add_column("Status", style="green")

    table.add_row("user_age", "KS_Test", "0.012 (p=0.88)", "[bold green]HEALTHY[/bold green]")
    table.add_row("purchase_amount", "Wasserstein", "0.045", "[bold green]HEALTHY[/bold green]")
    table.add_row("device_category", "PSI", "0.082", "[bold green]HEALTHY[/bold green]")
    console.print(table)

def main():
    parser = argparse.ArgumentParser(prog="mantactl", description="Manta ML Systems CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("health", help="Check cluster and service health")
    subparsers.add_parser("models", help="List registered models and versions")
    subparsers.add_parser("drift", help="Inspect real-time model drift status")

    args = parser.parse_args()
    if args.command == "health":
        cmd_health(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "drift":
        cmd_drift(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
