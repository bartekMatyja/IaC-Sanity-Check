import os
import openai
import logging

logger = logging.getLogger(__name__)

def get_fix_for_check(failed_check: dict) -> str:
    """
    Uses OpenAI API to suggest a fix for a failed check.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. Cannot fetch fix.")
        return "Comparison unavailable: OPENAI_API_KEY not set."

    client = openai.OpenAI(api_key=api_key)

    prompt = f"""
    You are a Senior DevSecOps Architect.
    An IaC security scan has identified a vulnerability in the following Terraform resource.
    
    Check ID: {failed_check.get('check_id')}
    Check Name: {failed_check.get('check_name')}
    Severity: {failed_check.get('severity', 'UNKNOWN')}
    Resource: {failed_check.get('resource')}
    File: {failed_check.get('file_path')}
    
    Code Snippet:
    ```hcl
    {failed_check.get('code_block')}
    ```
    
    Please provide:
    1. A clear explanation of why this configuration is dangerous from a business and security perspective.
    2. The specific code correction to fix this vulnerability.
    
    Format your response as follows:
    
    ### Risk Analysis
    [Explanation here]
    
    ### Corrected Code
    ```hcl
    [Code here]
    ```
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a Senior DevSecOps Architect who explains security risks clearly to developers and managers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error fetching fix from OpenAI: {e}")
        return "Error fetching fix."
