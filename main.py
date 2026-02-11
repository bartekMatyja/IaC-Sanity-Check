import argparse
import sys
import os
import logging
from scanner import run_checkov
from ai_fixer import get_fix_for_check
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
    parser = argparse.ArgumentParser(description="IaC Sanity Check Tool - Scan Terraform code and suggest AI fixes.")
    parser.add_argument("directory", help="Path to the directory containing Terraform files to scan.")
    parser.add_argument("--min-severity", default="LOW", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], 
                        help="Minimum severity level to report (default: LOW).")
    parser.add_argument("--generate-report", action="store_true", help="Generate an HTML report.")
    
    args = parser.parse_args()

    target_dir = os.path.abspath(args.directory)
    if not os.path.isdir(target_dir):
        logger.error(f"Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)

    logger.info(f"Starting scan on directory: {target_dir}")
    all_checks = run_checkov(target_dir)

    # Filter by severity
    min_severity_score = SEVERITY_ORDER.get(args.min_severity, 0)
    failed_checks = []
    for c in all_checks:
        severity_val = c.get('severity')
        if severity_val is None:
            severity_val = 'UNKNOWN'
        
        if SEVERITY_ORDER.get(severity_val.upper(), 0) >= min_severity_score:
            c['severity'] = severity_val.upper() # Standardize to upper case
            failed_checks.append(c)
    
    ignored_count = len(all_checks) - len(failed_checks)
    if ignored_count > 0:
        logger.info(f"Ignored {ignored_count} issues below severity {args.min_severity}.")

    if not failed_checks:
        logger.info("No security issues found matching criteria! Great job.")
        sys.exit(0)

    logger.warning(f"Found {len(failed_checks)} security issues. Fetching fixes...")
    
    findings = []
    
    # Process each failed check
    for i, check in enumerate(failed_checks, 1):
        print("\n" + "="*60)
        print(f"Issue #{i}: {check['check_id']} - {check['check_name']}")
        print(f"Severity: {check.get('severity', 'UNKNOWN')}")
        print(f"File: {check['file_path']}")
        print(f"Resource: {check['resource']}")
        print("-"*60)
        
        print("Original Code Snippet:")
        # Checkov code_block is a list of [line_num, line_content]
        try:
             # Extract just the code lines
             code_lines = [line[1] for line in check.get('code_block', [])]
             print("".join(code_lines))
        except Exception:
             print("(Code snippet unavailable)")

        print("-" * 60)
        print("🤖 AI Analysis & Fix:")
        
        # We need to construct a string representation of the code block for the AI prompt
        code_str = "".join([line[1] for line in check.get('code_block', [])])
        # Update the check dict with the string representation for the AI fixer
        check['code_block'] = code_str
        
        fix = get_fix_for_check(check)
        print(fix)
        print("="*60 + "\n")
        
        findings.append({
            'check': check,
            'fix': fix
        })

    if args.generate_report:
        generate_report(findings, target_dir)

    logger.info("Scan complete.")

if __name__ == "__main__":
    main()
