# Developer Guide (Internal)

## Prerequisites

*   Python 3.8+
*   OpenAI API Key (for AI fixes)

## Installation

1.  Navigate to the project directory:

    ```bash
    cd /Users/bartoszmatyja/.gemini/antigravity/scratch/iac_sanity_checker
    ```

2.  Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Local Usage (Development)

1.  Set your OpenAI API key:

    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    ```

2.  Run the tool against your Terraform directory:

    ```bash
    python main.py /path/to/terraform/code
    ```

## Running Tests

(Instructions for running unit tests if applicable)
