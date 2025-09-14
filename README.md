# Framelab Docker Templates

This repository contains a Jinja2 template and build script for generating Docker images with OpenVSCode Server.

## Files

### Templates
- `base/Dockerfile.j2` - Advanced Jinja2 template with conditional logic for different OS types

### Build Scripts
- `buildbase.py` - Build script using Jinja2 templating for base images
- `build_template.py` - Build script for framework-specific template images

### Configuration
- `constants.py` - Centralized default values and configurations
- `requirements.txt` - Python dependencies

## Usage

### Basic Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Generate Dockerfile and build image
python buildbase.py

# Generate Dockerfile only (skip build)
python buildbase.py --skip-build

# Dry run (simulate commands)
python buildbase.py --dry-run
```

### Different OS Types

```bash
# Build for Amazon Linux
python buildbase.py --os-type amazonlinux --os-version 2

# Build for Ubuntu (default)
python buildbase.py --os-type ubuntu --os-version 22.04
```

### Command Line Options

- `--ide` - IDE to use (default: vscode)
- `--os-type` - Base OS type (default: ubuntu)
- `--os-version` - Base OS version (default: 22.04)
- `--arch` - OpenVSCode architecture (default: x64)
- `--vscode-version` - OpenVSCode version (default: 1.103.1)
- `--hostname` - Container hostname (default: framelab)
- `--username` - Non-root username (default: framelab)
- `--uid` - User UID (default: 1000)
- `--port` - Expose port (default: 3000)
- `--skip-build` - Only generate Dockerfile, skip build and push
- `--skip-push` - Skip pushing image to ECR
- `--dry-run` - Simulate commands without executing them

## Advanced Template Features

The Jinja2 template automatically handles different OS types with conditional logic built into the template itself:

- **Ubuntu/Debian**: Uses `apt-get` package manager
- **Amazon Linux**: Uses `dnf` package manager  
- **Other OS types**: Falls back to apt-get

No need to specify install commands in the Python script - the template handles everything automatically!

## Jinja2 Template Features

The Jinja2 templates support:

- Variable substitution: `{{ variable_name }}`
- Conditional logic: `{% if condition %}...{% endif %}`
- Comments: `{# This is a comment #}`
- Filters and functions

### Example Template Usage

```dockerfile
# Base OS and configuration
FROM {{ os_type }}:{{ os_version }}

# Install dependencies (conditional logic built-in)
{% if os_type.lower() == 'amazonlinux' %}
RUN dnf install -y --setopt=install_weak_deps=False \
    curl wget git sudo bash ca-certificates shadow-utils hostname && dnf clean all
{% else %}
RUN apt-get update && apt-get install -y \
    curl wget git sudo bash locales ca-certificates \
    && rm -rf /var/lib/apt/lists/*
{% endif %}

# Set hostname
RUN echo {{ hostname }} > /etc/hostname
```

## Generated Files

- `base/Dockerfile.generated` - The generated Dockerfile from the Jinja2 template

## Configuration Management

The repository uses a centralized `constants.py` file for all default values:

- **Base Image Defaults**: IDE, OS type/version, architecture, VSCode version, user settings
- **ECR Repository Defaults**: Separate defaults for base and template repositories
- **Template Defaults**: Version, runtime, framework-specific configurations
- **File Paths**: Centralized path constants for templates and generated files
- **Logging Configuration**: Standardized logging format and level

This approach ensures consistency across all build scripts and makes maintenance easier.

## Dependencies

- Python 3.7+
- Jinja2 >= 3.1.0
- PyYAML >= 6.0
- Docker (for building images)
- AWS CLI (for ECR operations)