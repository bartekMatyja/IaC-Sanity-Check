# IaC Security Shield (SaaS-lite)

**The Ultimate CI/CD Security Shield: IaC + Secrets + Container Scanning.**

This tool provides a comprehensive security scan for your infrastructure and build pipelines. It combines multiple industry-standard tools into a single, AI-enhanced report:

1.  **Infrastructure as Code**: Scans Terraform with `checkov`.
2.  **Secrets Detection**: Scans for hardcoded credentials with `gitleaks`.
3.  **Container Security**: Scans Dockerfiles and filesystems with `trivy`.
4.  **AI Remediation**: Uses OpenAI to suggest fixes for IaC and Dockerfile vulnerabilities.

## Prerequisites

*   **Docker** (or a container runtime like containerd/podman)
*   **OpenAI API Key** (required for AI fixes)

## Usage

### Run via Docker

The easiest way to run the scanner is using Docker. No installation of Python or dependencies is required.

```bash
# 1. Pull the image
docker pull ghcr.io/bartekMatyja/IaC-Sanity-Check/:latest

# 2. Run the scan
# Mount your code to /app/data
# Pass your OpenAI API Key
export OPENAI_API_KEY="your-api-key"

docker run --rm \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd):/app/data \
  ghcr.io/bartekMatyja/IaC-Sanity-Check/:latest /app/data --generate-report
```

### Configuration

| Environment Variable | Description | Required |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | Your OpenAI API Key for generating fix suggestions. | Yes |

| Argument | Description | Default |
| :--- | :--- | :--- |
| `directory` | Path to the directory to scan (mapped volume). | (Required) |
| `--min-severity` | Minimum severity to report (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). | `LOW` |
| `--generate-report` | Generate an HTML report (`security_audit_report.html`). | `False` |

## CI/CD Integration

### GitLab CI

Use the provided template or configure manually:

```yaml
iac_security_scan:
  stage: test
  image: 
    name: ghcr.io/bartekMatyja/IaC-Sanity-Check/:latest
    entrypoint: [""]
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY
  script:
    - python /app/main.pyc . --generate-report --min-severity HIGH
  artifacts:
    paths:
      - security_audit_report.html
    when: always
```

### GitHub Actions

```yaml
steps:
  - uses: actions/checkout@v3
  - name: Run IaC Sanity Check
    uses: docker://ghcr.io/bartekMatyja/IaC-Sanity-Check/:latest
    with:
      args: . --generate-report
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Jenkins

```groovy
stage('AI Security Scan') {
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    steps {
        sh 'docker run --rm -e OPENAI_API_KEY=${OPENAI_API_KEY} -v ${WORKSPACE}:/app/data ghcr.io/bartekMatyja/IaC-Sanity-Check/:latest /app/data --generate-report'
    }
}
```

## Security ("Safe-Stack")

*   **Secret Masking**: Always pass `OPENAI_API_KEY` as an environment variable from your CI/CD secrets.
*   **No-Cloud Storage**: The tool runs entirely within your container. Reports are generated locally.
*   **Read-Only**: The tool scans your code but does not modify it automatically.

---
*For developer instructions (building from source), see [DEVELOPMENT.md](DEVELOPMENT.md).*
