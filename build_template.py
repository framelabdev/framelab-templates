#!/usr/bin/env python3
import argparse
import logging
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from constants import (
    TEMPLATES, DEFAULT_TEMPLATE_VERSION, DEFAULT_TEMPLATE_ECR_REPO,
    LOGGING_FORMAT, LOGGING_LEVEL
)

logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL),
    format=LOGGING_FORMAT,
)

def load_template_config(template_name: str, user_config_file: str = None, version_override: str = None) -> Dict[str, Any]:
    """Load template configuration with optional user overrides."""
    template_info = TEMPLATES[template_name]
    
    # Load default template config
    config_path = Path(template_info["config_file"])
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    # Load user configuration overrides
    if user_config_file and Path(user_config_file).exists():
        with open(user_config_file, 'r') as f:
            user_config = yaml.safe_load(f)
            config.update(user_config)
    
    # Merge with template defaults
    config.update({
        "port": config.get("port", template_info["default_port"]),
        "runtime": template_info["runtime"],
        "framework": template_info["framework"],
        "version": version_override or config.get("version", template_info.get("version", DEFAULT_TEMPLATE_VERSION))
    })
    
    return config

def generate_template_dockerfile(template_name: str, base_image: str, config: Dict[str, Any]) -> str:
    """Generate Dockerfile from Jinja2 template."""
    template_info = TEMPLATES[template_name]
    template_path = Path(template_info["dockerfile_template"])
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_info["dockerfile_template"])
    
    # Process configuration for template
    processed_config = config.copy()
    
    # Handle additional packages installation
    if 'additional_packages' in config and config['additional_packages']:
        processed_config['additional_packages'] = config['additional_packages']
    else:
        processed_config['additional_packages'] = []
    
    # Handle VSCode extensions installation
    if 'vscode_extensions' in config and config['vscode_extensions']:
        processed_config['vscode_extensions'] = config['vscode_extensions']
    else:
        processed_config['vscode_extensions'] = []
    
    # Replace placeholders
    dockerfile_content = template.render(
        base_image=base_image,
        **processed_config
    )
    
    return dockerfile_content

def run_command(cmd: list[str], dry_run: bool = False) -> None:
    """Run or simulate a shell command."""
    logging.info("Running: %s", " ".join(cmd))
    if dry_run:
        logging.info("Dry run mode: command not executed.")
        return
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", e)
        raise

def build_template_image(template_name: str, base_image: str, config: Dict[str, Any], args: argparse.Namespace) -> str:
    """Build template-specific Docker image."""
    # Generate dockerfile
    dockerfile_content = generate_template_dockerfile(template_name, base_image, config)
    
    # Write dockerfile
    dockerfile_path = Path(f"Dockerfile.{template_name}")
    dockerfile_path.write_text(dockerfile_content)
    logging.info(f"Generated {dockerfile_path}")
    
    # Build image with dynamic tag
    template_info = TEMPLATES[template_name]
    version = config.get("version", template_info.get("version", DEFAULT_TEMPLATE_VERSION))
    base_image_name = base_image.split(":")[0].split("/")[-1]  # Extract base image name
    tag = f"{template_name}-{version}"
    build_cmd = ["docker", "build", "-f", str(dockerfile_path), "-t", tag, "."]
    
    run_command(build_cmd, dry_run=args.dry_run)
    logging.info("Template image built: %s ✅", tag)
    
    return tag

def push_template_to_ecr(template_tag: str, template_name: str, base_image: str, config: Dict[str, Any], args: argparse.Namespace) -> str:
    """Push template image to ECR with dynamic repository and tag."""
    # Extract base image name (e.g., "vscode-ubuntu-22.04" from "vscode-ubuntu-22.04-base")
    base_image_name = base_image.replace("-base", "")
    
    # Get version from config or template defaults
    template_info = TEMPLATES[template_name]
    version = config.get("version", template_info.get("version", DEFAULT_TEMPLATE_VERSION))
    
    # Build dynamic ECR URL: base_repo/templates/base_image:template_name-version
    ecr_repo_base = args.ecr_repo.rstrip("/")
    ecr_url = f"{ecr_repo_base}/templates/{base_image_name}:{template_name}-{version}"
    
    run_command(["docker", "tag", template_tag, ecr_url], dry_run=args.dry_run)
    run_command(["docker", "push", ecr_url], dry_run=args.dry_run)
    logging.info("Template image pushed: %s ✅", ecr_url)
    return ecr_url

def build_multiple_templates(templates: list[str], base_image: str, args: argparse.Namespace) -> None:
    """Build multiple template images from base image."""
    for template in templates:
        if template not in TEMPLATES:
            logging.error(f"Unknown template: {template}")
            continue
            
        logging.info(f"Building {template} template from base: {base_image}")
        
        # Load configuration
        config = load_template_config(template, args.config, args.version)
        
        # Build template image
        template_tag = build_template_image(template, base_image, config, args)
        
        # Push to ECR if requested
        if not args.skip_push:
            push_template_to_ecr(template_tag, template, base_image, config, args)

def main():
    parser = argparse.ArgumentParser(description="Build template images from base image")
    
    # Template selection (mutually exclusive with list)
    template_group = parser.add_mutually_exclusive_group(required=True)
    template_group.add_argument("--template", choices=TEMPLATES.keys(), 
                               help="Single template to build")
    template_group.add_argument("--templates", nargs='+', choices=TEMPLATES.keys(),
                               help="Multiple templates to build")
    template_group.add_argument("--list-templates", action="store_true",
                               help="List available templates")
    
    # Base image
    parser.add_argument("--base-image", required=False,
                       help="Base image tag to build from (required if building templates)")
    
    # Configuration
    parser.add_argument("--config", help="Custom configuration file (YAML)")
    parser.add_argument("--version", help="Override template version (e.g., v1.0.0)")
    
    # ECR settings
    parser.add_argument("--ecr-repo", 
                       default=DEFAULT_TEMPLATE_ECR_REPO,
                       help=f"ECR repository base URL for templates (default: {DEFAULT_TEMPLATE_ECR_REPO})")
    parser.add_argument("--skip-push", action="store_true", 
                       help="Skip pushing to ECR")
    
    # Build options
    parser.add_argument("--dry-run", action="store_true",
                       help="Simulate commands without executing")
    parser.add_argument("--skip-build", action="store_true",
                       help="Only generate Dockerfile, skip build and push")
    
    args = parser.parse_args()
    
    if args.list_templates:
        print("Available templates:")
        for name, info in TEMPLATES.items():
            print(f"  {name}: {info['framework']} ({info['runtime']})")
        return
    
    # Validate base image is provided when building templates
    if not args.base_image:
        parser.error("--base-image is required when building templates")
    
    # Determine which templates to build
    if args.template:
        templates_to_build = [args.template]
    elif args.templates:
        templates_to_build = args.templates
    else:
        parser.error("Must specify either --template or --templates")
    
    # Build templates
    build_multiple_templates(templates_to_build, args.base_image, args)

if __name__ == "__main__":
    main()
