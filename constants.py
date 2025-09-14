#!/usr/bin/env python3
"""
Common constants and default values for Framelab Docker Templates.
This file centralizes all default values used across build scripts.
"""

# Base Image Defaults
DEFAULT_IDE = "vscode"
DEFAULT_OS_TYPE = "ubuntu"
DEFAULT_OS_VERSION = "22.04"
DEFAULT_ARCH = "x64"
DEFAULT_VSCODE_VERSION = "1.103.1"
DEFAULT_HOSTNAME = "framelab"
DEFAULT_USERNAME = "framelab"
DEFAULT_UID = "1000"
DEFAULT_PORT = "3000"

# ECR Repository Defaults
DEFAULT_BASE_ECR_REPO = "208249468771.dkr.ecr.us-east-1.amazonaws.com/framelab/base-images"
DEFAULT_TEMPLATE_ECR_REPO = "208249468771.dkr.ecr.us-east-1.amazonaws.com/framelab"

# Template Defaults
DEFAULT_TEMPLATE_VERSION = "v0.0.1"
DEFAULT_RUNTIME = "node"

# Template Configurations
TEMPLATES = {
    "react": {
        "dockerfile_template": "templates/react.dockerfile.j2",
        "config_file": "templates/react/config.yml",
        "default_port": 5173,  # Vite default port
        "runtime": DEFAULT_RUNTIME,
        "framework": "React.js",
        "version": DEFAULT_TEMPLATE_VERSION
    },
    "angular": {
        "dockerfile_template": "templates/angular.dockerfile.j2",
        "config_file": "templates/angular/config.yml",
        "default_port": 4200,  # Angular CLI default port
        "runtime": DEFAULT_RUNTIME,
        "framework": "Angular",
        "version": DEFAULT_TEMPLATE_VERSION
    },
    "vue": {
        "dockerfile_template": "templates/vue.dockerfile.j2",
        "config_file": "templates/vue/config.yml",
        "default_port": 5173,  # Vite default port
        "runtime": DEFAULT_RUNTIME,
        "framework": "Vue.js",
        "version": DEFAULT_TEMPLATE_VERSION
    }
}

# File Paths
BASE_DOCKERFILE_TEMPLATE = "base/base.dockerfile.j2"
BASE_DOCKERFILE_GENERATED = "base/Dockerfile.generated"

# Logging Configuration
LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOGGING_LEVEL = "INFO"
