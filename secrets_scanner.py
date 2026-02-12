import subprocess
import json
import logging
import os

logger = logging.getLogger(__name__)

def run_gitleaks_scan(directory: str) -> list:
    """
    Runs gitleaks on the specified directory and returns a list of findings.
    """
    report_path = os.path.join(directory, "gitleaks-report.json")
    
    # Ensure gitleaks is installed
    try:
        subprocess.run(["gitleaks", "version"], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.warning("Gitleaks not found. Skipping secrets scan.")
        return []

    logger.info(f"Running Gitleaks on {directory}...")
    
    try:
        # Run gitleaks
        # --exit-code=0 ensures we don't crash if secrets are found (we parse the report)
        # --no-git treats the source as a plain directory (useful for docker mounts without .git)
        cmd = [
            "gitleaks", "detect",
            "--source", directory,
            "--report-path", report_path,
            "--exit-code", "0",
            "--no-git",
            "--verbose"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Gitleaks failed: {result.stderr}")
            return []

        if not os.path.exists(report_path):
            logger.info("No secrets found (no report generated).")
            return []

        with open(report_path, 'r') as f:
            data = json.load(f)
            
        # Clean up report file
        os.remove(report_path)
        
        return data

    except json.JSONDecodeError:
        logger.error("Failed to parse Gitleaks JSON output.")
        return []
    except Exception as e:
        logger.error(f"An error occurred while running Gitleaks: {e}")
        return []
