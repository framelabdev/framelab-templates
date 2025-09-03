#!/usr/bin/env python3
import argparse
import logging
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
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
    """Generate Dockerfile from external template."""
    template_path = Path("base/Dockerfile.base")
    if not template_path.exists():
        logging.error("Dockerfile.base not found!")
        raise FileNotFoundError("Dockerfile.base not found.")

    dockerfile_content = template_path.read_text()

    # Select install command based on OS
    if args.os_type.lower() == "amazonlinux":
        install_cmd = (
            "dnf install -y --setopt=install_weak_deps=False \\"
            "curl wget git sudo bash ca-certificates shadow-utils hostname && dnf clean all"
        )
    else:
        install_cmd = (
            "apt-get update && apt-get install -y curl wget git sudo bash locales ca-certificates && rm -rf /var/lib/apt/lists/*"
        )

    # Replace placeholders
    dockerfile_content = dockerfile_content.format(
        os_type=args.os_type,
        os_version=args.os_version,
        openvscode_arch=args.arch,
        openvscode_version=args.vscode_version,
        hostname=args.hostname,
        username=args.username,
        user_uid=args.uid,
        port=args.port,
        install_cmd=install_cmd,
    )
    Path("base/Dockerfile.generated").write_text(dockerfile_content)
    logging.info("Dockerfile generated successfully ✅")


def build_image(args: argparse.Namespace) -> str:
    """Build the Docker image and return the tag."""
    tag = make_tag(args)
    run_command(["docker", "build", "-t", tag, ".", "-f", "base/Dockerfile.generated"], dry_run=args.dry_run)
    logging.info("Image built: %s ✅", tag)
    return tag


def push_ecr(args: argparse.Namespace, tag: str) -> str:
    """Push Docker image to ECR and return the full image URL."""
    ecr_url = f"{args.ecr_repo}:{tag}"
    run_command(["docker", "tag", tag, ecr_url], dry_run=args.dry_run)
    run_command(["docker", "push", ecr_url], dry_run=args.dry_run)
    logging.info("Image pushed: %s ✅", ecr_url)
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
    parser.add_argument("--ide", default="vscode", help="IDE to use (default: vscode)")
    parser.add_argument(
        "--os-type", default="ubuntu", help="Base OS type (default: ubuntu)"
    )
    parser.add_argument(
        "--os-version", default="22.04", help="Base OS version (default: 22.04)"
    )
    parser.add_argument(
        "--arch", default="x64", help="OpenVSCode architecture (default: x64)"
    )
    parser.add_argument(
        "--vscode-version",
        default="1.103.1",
        help="OpenVSCode version (default: 1.103.1)",
    )
    parser.add_argument(
        "--hostname", default="framelab", help="Container hostname (default: framelab)"
    )
    parser.add_argument(
        "--username", default="framelab", help="Non-root username (default: framelab)"
    )
    parser.add_argument("--uid", default="1000", help="User UID (default: 1000)")
    parser.add_argument("--port", default="3000", help="Expose port (default: 3000)")
    parser.add_argument(
        "--ecr-repo",
        default="208249468771.dkr.ecr.us-east-1.amazonaws.com/framelab/base-images",
        help="ECR Repo URL for pushing the image",
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
