#!/bin/bash

# Determine the .env file location from CONFIG_FILE, or default to "./.env"
ENV_FILE="${CONFIG_FILE:-./.env}"

# Warn if the file does not exist, but continue (defaults will be used if needed)
if [ ! -f "$ENV_FILE" ]; then
  echo "Warning: $ENV_FILE not found. Defaults will be used if environment variables are missing."
fi

# Log arguments from container:
echo "Launching vLMM with the following arguments from container: $@"

# Helper function to extract a key's value from the env file. It strips surrounding quotes if present.
extract_value() {
  local key="$1"
  local file="$2"
  grep "^${key}=" "$file" 2>/dev/null | head -n 1 | cut -d '=' -f2- | sed -e 's/^["'\'']//g' -e 's/["'\'']$//g'
}

# For API_KEY: check environment first, then file, then default.
if [ -z "$API_KEY" ]; then
  if [ -f "$ENV_FILE" ]; then
    API_KEY=$(extract_value "API_KEY" "$ENV_FILE")
  fi
  if [ -z "$API_KEY" ]; then
    API_KEY="helloworld"
  fi
fi

# For MODEL_ID: check file first, then environment, then default.
# By default we will always look in the .env file, that's where the administrator
# will write the model_id. 
# In order to handle configuration through environment variables we try to load
# only if .env file is not present

if [ -f "$ENV_FILE" ]; then
  MODEL_ID=$(extract_value "MODEL_ID" "$ENV_FILE")
elif [ -z "$MODEL_ID" ]; then
  MODEL_ID="Qwen/Qwen2.5-0.5B-Instruct"
fi

# Output the final values
echo "Using API_KEY: $API_KEY"
echo "Using MODEL_ID: $MODEL_ID"

# Check if we need to start with api_key
if [ "$API_KEY" == "EMPTY" ]; then
    echo "API_KEY is <EMPTY>, no api key will be used"
    exec vllm serve $MODEL_ID "$@"
else
    echo "API key is not <EMPTY> setting api_key for vllm"
    # we exit 0 so supervisor does not crash
    exec vllm serve $MODEL_ID --api-key $API_KEY "$@"
fi

