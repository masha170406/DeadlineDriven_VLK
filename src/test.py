import os
import litellm
from dotenv import load_dotenv

# 1. Load the environment variables from .env
load_dotenv()

# 2. Set up the model and a simple message
# Mistral models usually follow the format "mistral/mistral-model-name"
model_name = "mistral/mistral-large-latest"
messages = [
    {
        "role": "user",
        "content": "Hello! If you can read this, the API connection is working. Reply with the word 'SUCCESS'",
    }
]

print(f"Testing connection to {model_name}...")

try:
    # 3. Call the API
    response = litellm.completion(model=model_name, messages=messages)

    # 4. Print the result
    content = response.choices[0].message.content
    print("-" * 30)
    print("AI Response:", content)
    print("-" * 30)

    if "SUCCESS" in content.upper():
        print("✅ API Test Passed!")
    else:
        print("⚠️ API replied, but the response was unexpected.")

except Exception as e:
    print("❌ API Test Failed!")
    print(f"Error details: {e}")
