import os
import openai
import logging

logger = logging.getLogger(__name__)

def get_fix_for_check(failed_check: dict) -> str:
    """
    Uses OpenAI API to suggest a fix for a failed check with aggressive security hardening.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. Cannot fetch fix.")
        return "Comparison unavailable: OPENAI_API_KEY not set."

    client = openai.OpenAI(api_key=api_key)

    # ZMIANA 1: System Message definiujący "Zero Trust Mindset"
    system_msg = (
        "You are a Senior DevSecOps Architect with a Zero Trust mindset. "
        "Your goal is not just to fix the reported issue, but to ensure the resulting "
        "code is fully hardened according to CIS Benchmarks. "
        "Never allow public access, even if the original code had it."
    )

    # ZMIANA 2: Instrukcje wymuszające naprawę "przy okazji"
    prompt = f"""
    An IaC security scan has identified a vulnerability:
    Check ID: {failed_check.get('check_id')}
    Check Name: {failed_check.get('check_name')}
    Resource: {failed_check.get('resource')}
    File: {failed_check.get('file_path')}
    
    Original Code Snippet:
    ```hcl
    {failed_check.get('code_block')}
    ```
    
    CRITICAL INSTRUCTIONS FOR THE FIX:
    1. Fix the specific vulnerability reported above.
    2. OVERRIDE INSECURE DEFAULTS: If you see 'acl = "public-read"', YOU MUST CHANGE IT to 'private'.
    3. HARDEN THE RESOURCE: Ensure encryption (KMS/SSE) and Public Access Blocks are present if applicable to this resource type.
    4. Do not remove essential logic, but wrap it in security controls.
    
    Format your response as follows:
    
    ### Risk Analysis
    [Clear business and security explanation]
    
    ### Corrected Code
    ```hcl
    [The fixed Terraform code block]
    ```
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error fetching fix from OpenAI: {e}")
        return "Error fetching fix."

def get_fix_for_container_issue(issue: dict) -> str:
    """
    Uses OpenAI API to suggest a fix for a Dockerfile vulnerability with hardening.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. Cannot fetch fix.")
        return "Comparison unavailable: OPENAI_API_KEY not set."

    client = openai.OpenAI(api_key=api_key)

    # ZMIANA 1: Promowanie minimalizmu i bezpieczeństwa kontenerów
    system_msg = (
        "You are a Senior DevSecOps Architect specializing in container hardening. "
        "You prioritize minimalist images (Distroless/Alpine) and non-root execution."
    )

    # ZMIANA 2: Wymuszenie dodania użytkownika non-root
    prompt = f"""
    A container security scan (Trivy) found: {issue.get('Title', issue.get('PkgName'))}
    Severity: {issue.get('Severity', 'UNKNOWN')}
    Description: {issue.get('Description')}
    
    INSTRUCTIONS:
    1. Provide the specific fix (e.g., upgrade package, change base image).
    2. ALWAYS ENFORCE LEAST PRIVILEGE: If the Dockerfile context implies running as root, include instructions to create a non-root USER.
    3. Suggest pinning specific versions for base images if 'latest' is used.
    
    Format your response as follows:
    
    ### Risk Analysis
    [Explanation here]
    
    ### Remediation
    ```dockerfile
    [Corrected Dockerfile snippet or instructions]
    ```
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error fetching fix from OpenAI: {e}")
        return "Error fetching fix."