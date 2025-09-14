#!/usr/bin/env python3
import argparse
import logging
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from constants import (
    DEFAULT_IDE, DEFAULT_OS_TYPE, DEFAULT_OS_VERSION, DEFAULT_ARCH,
    DEFAULT_VSCODE_VERSION, DEFAULT_HOSTNAME, DEFAULT_USERNAME, DEFAULT_UID,
    DEFAULT_PORT, DEFAULT_BASE_ECR_REPO, BASE_DOCKERFILE_TEMPLATE,
    BASE_DOCKERFILE_GENERATED, LOGGING_FORMAT, LOGGING_LEVEL
)

logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL),
    format=LOGGING_FORMAT,
)

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


def make_tag(args: argparse.Namespace) -> str:
    """Generate a consistent Docker tag."""
    return f"{args.ide}-{args.os_type}-{args.os_version}-base"


def generate_dockerfile(args: argparse.Namespace) -> None:
    """Generate Dockerfile from Jinja2 template."""
    template_path = Path(BASE_DOCKERFILE_TEMPLATE)
    if not template_path.exists():
        logging.error("base.dockerfile.j2 template not found!")
        raise FileNotFoundError("base.dockerfile.j2 template not found.")

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('base'))
    template = env.get_template('base.dockerfile.j2')

    # Render template with variables
    dockerfile_content = template.render(
        os_type=args.os_type,
        os_version=args.os_version,
        openvscode_arch=args.arch,
        openvscode_version=args.vscode_version,
        hostname=args.hostname,
        username=args.username,
        user_uid=args.uid,
        port=args.port,
    )
    
    Path(BASE_DOCKERFILE_GENERATED).write_text(dockerfile_content)
    logging.info("Dockerfile generated successfully")


def build_image(args: argparse.Namespace) -> str:
    """Build the Docker image and return the tag."""
    tag = make_tag(args)
    run_command(["docker", "build", "-t", tag, ".", "-f", BASE_DOCKERFILE_GENERATED], dry_run=args.dry_run)
    logging.info("Image built: %s", tag)
    return tag


def push_ecr(args: argparse.Namespace, tag: str) -> str:
    """Push Docker image to ECR and return the full image URL."""
    ecr_url = f"{args.ecr_repo}:{tag}"
    run_command(["docker", "tag", tag, ecr_url], dry_run=args.dry_run)
    run_command(["docker", "push", ecr_url], dry_run=args.dry_run)
    logging.info("Image pushed: %s", ecr_url)
    return ecr_url


def create_ecr_repo_if_not_exists(args: argparse.Namespace, tag: str) -> None:
    """Create ECR repository if it does not exist."""
    repo_name = "framelab/templates/" + tag.removesuffix("-base")
    try:
        run_command(
            ["aws", "ecr", "describe-repositories", "--repository-names", repo_name],
            dry_run=args.dry_run,
        )
        logging.info("ECR repository %s already exists.", repo_name)
    except subprocess.CalledProcessError:
        logging.info("ECR repository %s does not exist. Creating...", repo_name)
        run_command(
            ["aws", "ecr", "create-repository", "--repository-name", repo_name],
            dry_run=args.dry_run,
        )
        logging.info("ECR repository %s created successfully.", repo_name)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Dockerfile, build image, and push to ECR."
    )
    parser.add_argument("--ide", default=DEFAULT_IDE, help=f"IDE to use (default: {DEFAULT_IDE})")
    parser.add_argument(
        "--os-type", default=DEFAULT_OS_TYPE, help=f"Base OS type (default: {DEFAULT_OS_TYPE})"
    )
    parser.add_argument(
        "--os-version", default=DEFAULT_OS_VERSION, help=f"Base OS version (default: {DEFAULT_OS_VERSION})"
    )
    parser.add_argument(
        "--arch", default=DEFAULT_ARCH, help=f"OpenVSCode architecture (default: {DEFAULT_ARCH})"
    )
    parser.add_argument(
        "--vscode-version",
        default=DEFAULT_VSCODE_VERSION,
        help=f"OpenVSCode version (default: {DEFAULT_VSCODE_VERSION})",
    )
    parser.add_argument(
        "--hostname", default=DEFAULT_HOSTNAME, help=f"Container hostname (default: {DEFAULT_HOSTNAME})"
    )
    parser.add_argument(
        "--username", default=DEFAULT_USERNAME, help=f"Non-root username (default: {DEFAULT_USERNAME})"
    )
    parser.add_argument("--uid", default=DEFAULT_UID, help=f"User UID (default: {DEFAULT_UID})")
    parser.add_argument("--port", default=DEFAULT_PORT, help=f"Expose port (default: {DEFAULT_PORT})")
    parser.add_argument(
        "--ecr-repo",
        default=DEFAULT_BASE_ECR_REPO,
        help=f"ECR Repo URL for pushing the image (default: {DEFAULT_BASE_ECR_REPO})",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Only generate Dockerfile, skip build and push",
    )
    parser.add_argument(
        "--skip-push", action="store_true", help="Skip pushing image to ECR"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate commands without executing them",
    )

    args = parser.parse_args()

    generate_dockerfile(args)

    if args.skip_build:
        logging.info("Skipping build and push as requested.")
        return

    tag = build_image(args)

    if not args.skip_push:
        push_ecr(args, tag)
        create_ecr_repo_if_not_exists(args, tag)


if __name__ == "__main__":
    main()
