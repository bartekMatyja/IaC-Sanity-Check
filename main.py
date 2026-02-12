import argparse
import sys
import os
import logging
from scanner import run_checkov
from secrets_scanner import run_gitleaks_scan
from container_scanner import run_trivy_scan
from ai_fixer import get_fix_for_check, get_fix_for_container_issue
from reporter import generate_report

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SEVERITY_ORDER = {
    "UNKNOWN": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

def main():
    parser = argparse.ArgumentParser(description="IaC Sanity Check Tool - CI/CD Security Shield")
    parser.add_argument("directory", help="Path to the directory to scan.")
    parser.add_argument("--min-severity", default="LOW", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], 
                        help="Minimum severity level for IaC report (default: LOW).")
    parser.add_argument("--generate-report", action="store_true", help="Generate an HTML report.")
    
    args = parser.parse_args()
    target_dir = os.path.abspath(args.directory)
    
    if not os.path.isdir(target_dir):
        logger.error(f"Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)

    logger.info(f"🛡️ Starting Comprehensive Security Scan on: {target_dir}")
    
    # ---------------------------------------------------------
    # 1. IaC Scan (Checkov)
    # ---------------------------------------------------------
    logger.info("--- Phase 1: Infrastructure as Code Scan (Checkov) ---")
    all_checks = run_checkov(target_dir)
    iac_findings = []
    
    min_severity_score = SEVERITY_ORDER.get(args.min_severity, 0)
    
    for c in all_checks:
        severity_val = c.get('severity', 'UNKNOWN').upper()
        if SEVERITY_ORDER.get(severity_val, 0) >= min_severity_score:
            c['severity'] = severity_val
            
            # Get AI Fix for IaC
            print(f"🤖 Analyzing IaC issue: {c['check_id']}...")
            # We need to ensure code_block is a string for the AI prompt
            if isinstance(c.get('code_block'), list):
                 code_str = "".join([line[1] for line in c.get('code_block', [])])
                 c['code_block'] = code_str
            
            fix = get_fix_for_check(c)
            iac_findings.append({'check': c, 'fix': fix})

    logger.info(f"IaC Scan complete. Found {len(iac_findings)} issues.")

    # ---------------------------------------------------------
    # 2. Secrets Scan (Gitleaks)
    # ---------------------------------------------------------
    logger.info("--- Phase 2: Secrets Detection (Gitleaks) ---")
    secrets_data = run_gitleaks_scan(target_dir)
    # Gitleaks output is a list of findings
    secrets_findings = secrets_data if isinstance(secrets_data, list) else []
    logger.info(f"Secrets Scan complete. Found {len(secrets_findings)} secrets.")

    # ---------------------------------------------------------
    # 3. Container Scan (Trivy)
    # ---------------------------------------------------------
    logger.info("--- Phase 3: Container Security Scan (Trivy) ---")
    trivy_data = run_trivy_scan(target_dir)
    container_findings = []
    
    # Process Trivy results
    if 'Results' in trivy_data:
        for result in trivy_data['Results']:
            target = result.get('Target', 'Unknown')
            for vuln in result.get('Vulnerabilities', []):
                vuln['target'] = target
                vuln['severity'] = vuln.get('Severity', 'UNKNOWN')
                vuln['title'] = vuln.get('Title', vuln.get('PkgName', 'Unknown'))
                vuln['vulnerability_id'] = vuln.get('VulnerabilityID', 'Unknown')
                vuln['pkg_name'] = vuln.get('PkgName', 'Unknown')
                vuln['installed_version'] = vuln.get('InstalledVersion', 'Unknown')
                vuln['fixed_version'] = vuln.get('FixedVersion', 'Unknown')
                vuln['description'] = vuln.get('Description', '')

                # AI Fix for Critical Dockerfile issues
                if 'Dockerfile' in target and vuln['severity'] == 'CRITICAL':
                    print(f"🤖 Analyzing Critical Dockerfile vulnerability: {vuln['vulnerability_id']}...")
                    fix = get_fix_for_container_issue(vuln)
                    vuln['fix'] = fix
                else:
                    vuln['fix'] = None
                
                container_findings.append(vuln)
    
    logger.info(f"Container Scan complete. Found {len(container_findings)} vulnerabilities.")

    # ---------------------------------------------------------
    # Consolidated Reporting & Exit Logic
    # ---------------------------------------------------------
    consolidated_findings = {
        'iac': iac_findings,
        'secrets': secrets_findings,
        'containers': container_findings
    }

    if args.generate_report:
        generate_report(consolidated_findings, target_dir)

    # Check for failure conditions (CRITICAL issues in any category)
    fail_pipeline = False
    
    # Check IaC
    if any(item['check']['severity'] == 'CRITICAL' for item in iac_findings):
        logger.error("❌ Pipeline Failed: Critical IaC issues found.")
        fail_pipeline = True
        
    # Check Secrets (Always critical)
    if secrets_findings:
        logger.error("❌ Pipeline Failed: Secrets detected.")
        fail_pipeline = True
        
    # Check Containers
    if any(item['severity'] == 'CRITICAL' for item in container_findings):
        logger.error("❌ Pipeline Failed: Critical Container vulnerabilities found.")
        fail_pipeline = True

    if fail_pipeline:
        sys.exit(1)
        
    logger.info("✅ Security Shield Scan Passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
