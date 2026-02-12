import subprocess
import json
import logging
import os

logger = logging.getLogger(__name__)

def run_trivy_scan(directory: str) -> dict:
    """
    Runs Trivy on the specified directory and returns a dictionary of findings.
    """
    report_path = os.path.join(directory, "container-vulns.json")
    
    # Ensure trivy is installed
    try:
        subprocess.run(["trivy", "--version"], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.warning("Trivy not found. Skipping container scan.")
        return {}

    logger.info(f"Running Trivy on {directory}...")
    
    try:
        # Run trivy fs
        cmd = [
            "trivy", "fs",
            "--format", "json",
            "--output", report_path,
            "--exit-code", "0",
            directory
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Trivy failed: {result.stderr}")
            return {}

        if not os.path.exists(report_path):
            logger.info("No container vulnerabilities found (no report generated).")
            return {}

        with open(report_path, 'r') as f:
            data = json.load(f)
            
        # Clean up report file
        os.remove(report_path)
        
        return data

    except json.JSONDecodeError:
        logger.error("Failed to parse Trivy JSON output.")
        return {}
    except Exception as e:
        logger.error(f"An error occurred while running Trivy: {e}")
        return {}
