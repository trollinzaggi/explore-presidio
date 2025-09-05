"""
Command-line interface for the bias anonymizer.
"""

import click
import json
import sys
from pathlib import Path
from typing import List, Optional
import logging
from colorama import init, Fore, Style

from .anonymizer import JSONAnonymizer
from .config import AnonymizerConfig
from .utils import load_json_file, save_json_file

# Initialize colorama for colored output
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Bias Anonymizer - Remove bias and PII from JSON data."""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output file path')
@click.option('-k', '--keys', multiple=True, help='Specific keys to anonymize (can be used multiple times)')
@click.option('-c', '--config', type=click.Path(exists=True), help='Configuration file path')
@click.option('--no-bias', is_flag=True, help='Disable bias detection')
@click.option('--no-pii', is_flag=True, help='Disable PII detection')
@click.option('--threshold', type=float, default=0.7, help='Confidence threshold (0-1)')
@click.option('--pretty', is_flag=True, help='Pretty print JSON output')
@click.option('--report', is_flag=True, help='Generate analysis report')
@click.option('--verbose', is_flag=True, help='Verbose output')
def anonymize(input_file, output, keys, config, no_bias, no_pii, threshold, pretty, report, verbose):
    """Anonymize a JSON file."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load configuration
        if config:
            click.echo(f"Loading configuration from {config}")
            anonymizer_config = AnonymizerConfig.from_yaml(config)
        else:
            anonymizer_config = AnonymizerConfig(
                detect_bias=not no_bias,
                detect_pii=not no_pii,
                confidence_threshold=threshold
            )
        
        # Initialize anonymizer
        anonymizer = JSONAnonymizer(config=anonymizer_config)
        
        # Load input file
        click.echo(f"Loading {input_file}")
        data = load_json_file(input_file)
        
        # Convert keys tuple to list
        keys_to_anonymize = list(keys) if keys else None
        
        # Generate report if requested
        if report:
            click.echo("\n" + Fore.CYAN + "=== ANALYSIS REPORT ===" + Style.RESET_ALL)
            analysis = anonymizer.analyze(data, keys_to_anonymize)
            
            click.echo(f"\n{Fore.YELLOW}Summary:{Style.RESET_ALL}")
            click.echo(f"  Total entities found: {analysis['total_entities']}")
            click.echo(f"  Bias categories: {', '.join(analysis['bias_categories']) or 'None'}")
            click.echo(f"  PII types: {', '.join(analysis['pii_types']) or 'None'}")
            
            if analysis['entities_by_type']:
                click.echo(f"\n{Fore.YELLOW}Entities by type:{Style.RESET_ALL}")
                for entity_type, count in analysis['entities_by_type'].items():
                    click.echo(f"  {entity_type}: {count}")
            
            if analysis['entities_by_path']:
                click.echo(f"\n{Fore.YELLOW}Entities by path:{Style.RESET_ALL}")
                for path, entities in list(analysis['entities_by_path'].items())[:10]:
                    click.echo(f"  {path}: {len(entities)} entities")
                    if verbose:
                        for entity in entities[:3]:
                            click.echo(f"    - {entity['type']}: '{entity['text']}' (confidence: {entity['confidence']:.2f})")
        
        # Anonymize data
        click.echo(f"\n{Fore.GREEN}Anonymizing...{Style.RESET_ALL}")
        anonymized = anonymizer.anonymize(data, keys_to_anonymize)
        
        # Get statistics
        stats = anonymizer.get_statistics()
        if stats:
            click.echo(f"\n{Fore.YELLOW}Processing statistics:{Style.RESET_ALL}")
            click.echo(f"  Strings processed: {stats.get('strings_processed', 0)}")
            click.echo(f"  Nested structures: {stats.get('nested_structures', 0)}")
        
        # Save or output result
        if output:
            save_json_file(anonymized, output, indent=2 if pretty else None)
            click.echo(f"\n{Fore.GREEN}✓ Saved to {output}{Style.RESET_ALL}")
        else:
            # Output to stdout
            if pretty:
                click.echo(json.dumps(anonymized, indent=2))
            else:
                click.echo(json.dumps(anonymized))
        
        click.echo(f"\n{Fore.GREEN}✓ Anonymization complete!{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False))
@click.argument('output_dir', type=click.Path())
@click.option('-k', '--keys', multiple=True, help='Specific keys to anonymize')
@click.option('-c', '--config', type=click.Path(exists=True), help='Configuration file path')
@click.option('--pattern', default='*.json', help='File pattern to match')
@click.option('--recursive', is_flag=True, help='Process files recursively')
def batch(input_dir, output_dir, keys, config, pattern, recursive):
    """Batch process multiple JSON files."""
    
    try:
        # Load configuration
        if config:
            anonymizer_config = AnonymizerConfig.from_yaml(config)
        else:
            anonymizer_config = AnonymizerConfig()
        
        # Initialize anonymizer
        anonymizer = JSONAnonymizer(config=anonymizer_config)
        
        # Find files
        input_path = Path(input_dir)
        if recursive:
            files = list(input_path.rglob(pattern))
        else:
            files = list(input_path.glob(pattern))
        
        if not files:
            click.echo(f"{Fore.YELLOW}No files found matching pattern: {pattern}{Style.RESET_ALL}")
            return
        
        click.echo(f"Found {len(files)} files to process")
        
        # Process files
        keys_to_anonymize = list(keys) if keys else None
        stats = anonymizer.anonymize_batch(files, output_dir, keys_to_anonymize)
        
        # Display results
        click.echo(f"\n{Fore.GREEN}Batch processing complete!{Style.RESET_ALL}")
        click.echo(f"  Files processed: {stats['files_processed']}")
        click.echo(f"  Files failed: {stats['files_failed']}")
        click.echo(f"  Total entities: {stats['total_entities']}")
        
        if stats['errors']:
            click.echo(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
            for error in stats['errors']:
                click.echo(f"  {error['file']}: {error['error']}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-c', '--config', type=click.Path(exists=True), help='Configuration file path')
@click.option('--detailed', is_flag=True, help='Show detailed analysis')
def analyze(input_file, config, detailed):
    """Analyze a JSON file for bias and PII without anonymizing."""
    
    try:
        # Load configuration
        if config:
            anonymizer_config = AnonymizerConfig.from_yaml(config)
        else:
            anonymizer_config = AnonymizerConfig()
        
        # Initialize anonymizer
        anonymizer = JSONAnonymizer(config=anonymizer_config)
        
        # Load and analyze file
        data = load_json_file(input_file)
        analysis = anonymizer.analyze(data)
        
        # Display results
        click.echo(f"\n{Fore.CYAN}=== ANALYSIS RESULTS ==={Style.RESET_ALL}")
        click.echo(f"\nFile: {input_file}")
        click.echo(f"Total entities found: {analysis['total_entities']}")
        
        if analysis['bias_categories']:
            click.echo(f"\n{Fore.YELLOW}Bias Categories Detected:{Style.RESET_ALL}")
            for category in analysis['bias_categories']:
                click.echo(f"  • {category}")
        
        if analysis['pii_types']:
            click.echo(f"\n{Fore.YELLOW}PII Types Detected:{Style.RESET_ALL}")
            for pii_type in analysis['pii_types']:
                click.echo(f"  • {pii_type}")
        
        if analysis['entities_by_type']:
            click.echo(f"\n{Fore.YELLOW}Entity Counts:{Style.RESET_ALL}")
            for entity_type, count in sorted(analysis['entities_by_type'].items()):
                click.echo(f"  {entity_type}: {count}")
        
        if detailed and analysis['detailed_findings']:
            click.echo(f"\n{Fore.YELLOW}Detailed Findings:{Style.RESET_ALL}")
            for finding in analysis['detailed_findings'][:20]:  # Show first 20
                click.echo(f"\n  Path: {finding['path']}")
                click.echo(f"  Type: {finding['entity_type']}")
                click.echo(f"  Text: '{finding['text']}'")
                click.echo(f"  Confidence: {finding['confidence']:.2f}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', type=click.Path(), help='Output file path')
def generate_config(output):
    """Generate a sample configuration file."""
    
    try:
        config = AnonymizerConfig()
        
        if output:
            config.to_yaml(output)
            click.echo(f"{Fore.GREEN}✓ Configuration saved to {output}{Style.RESET_ALL}")
        else:
            # Output to stdout
            import yaml
            click.echo(yaml.dump(config.__dict__, default_flow_style=False))
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
