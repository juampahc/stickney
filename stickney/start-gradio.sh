#!/bin/bash
# Launcher for the init 
GRADIO_VALUE="${RUN_GRADIO:-false}"

# Check if the environment variable is set to "true"
if [ "$GRADIO_VALUE" == "true" ]; then
    echo "RUN_GRADIO is true. Starting the extra application..."
    exec python3 gradio_app.py
else
    echo "RUN_GRADIO is not true. Exiting extra-app-init.sh."
    # we exit 0 so supervisor does not crash
    exec sleep infinity
fi