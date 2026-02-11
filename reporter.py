from jinja2 import Environment, FileSystemLoader
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_report(findings: list, directory: str, output_file: str = "security_audit_report.html"):
    """
    Generates an HTML report from the findings.
    """
    try:
        # Determine the directory of the script to find templates
        script_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(script_dir, 'templates')
        
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template('report_template.html')

        report_content = template.render(
            findings=findings,
            directory=directory,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_issues=len(findings)
        )

        with open(output_file, 'w') as f:
            f.write(report_content)
        
        logger.info(f"Report generated successfully: {output_file}")
        print(f"\n📄 Report generated: {os.path.abspath(output_file)}")

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
