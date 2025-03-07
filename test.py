from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Print ALL environment variables
print("ALL ENVIRONMENT VARIABLES:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

# Specifically check LLM_PROVIDER
print("\nSpecific LLM_PROVIDER checks:")
print("os.getenv('LLM_PROVIDER'):", repr(os.getenv('LLM_PROVIDER')))
print("os.environ.get('LLM_PROVIDER'):", repr(os.environ.get('LLM_PROVIDER')))