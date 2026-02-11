import subprocess
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)

def run_checkov(directory: str) -> list:
    """
    Runs checkov on the specified directory and returns a list of failed checks.
    """
    if not os.path.exists(directory):
        logger.error(f"Directory not found: {directory}")
        return []

    logger.info(f"Running checkov on {directory}...")
    try:
        # Determine checkov path relative to the current python executable
        # This handles venv execution properly
        checkov_path = os.path.join(os.path.dirname(sys.executable), "checkov")
        
        # Fallback to just "checkov" if the specific path doesn't exist (e.g. system install)
        if not os.path.exists(checkov_path):
            checkov_path = "checkov"

        # Run checkov and capture JSON output
        # Using --quiet to reduce noise, and -o json for structured output
        # Also using --soft-fail to ensure exit code 0 even if checks fail (we parse JSON)
        result = subprocess.run(
            [checkov_path, "-d", directory, "-o", "json", "--soft-fail", "--quiet"],
            capture_output=True,
            text=True,
            check=False 
        )

        if result.returncode != 0:
            logger.error(f"Checkov failed with return code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            return []
            
        try:
             output_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Checkov might output multiple JSON objects if multiple frameworks are scanned
            # or if there is some other output mixed in.
            # Simplified approach: return empty list on parse error for now.
            logger.error("Failed to parse checkov JSON output")
            logger.debug(f"Stdout was: {result.stdout}")
            return []

        failed_checks = []
        
        # Checkov output structure varies. It can be a list (if multiple frameworks) or a dict.
        results_list = output_data if isinstance(output_data, list) else [output_data]
        
        for res in results_list:
            # We are interested in 'results' -> 'failed_checks'
            if 'results' in res and 'failed_checks' in res['results']:
                for check in res['results']['failed_checks']:
                    failed_checks.append({
                        'check_id': check.get('check_id'),
                        'check_name': check.get('check_name'),
                        'file_path': check.get('file_path'),
                        'resource': check.get('resource'),
                        'start_line': check.get('file_line_range', [0, 0])[0],
                        'end_line': check.get('file_line_range', [0, 0])[1],
                        'code_block': check.get('code_block', []),
                        'severity': check.get('severity') or 'LOW'
                    })

        return failed_checks

    except FileNotFoundError:
        logger.error("Checkov not found. Please ensure it is installed and in your PATH.")
        return []
    except Exception as e:
        logger.error(f"An error occurred while running checkov: {e}")
        return []
