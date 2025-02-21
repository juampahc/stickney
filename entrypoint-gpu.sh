#!/bin/bash
# Entrypoint for container. The goal of this script is to
# capture the arguments passed to the container which should be
# used when launching vLLM
RUNTIME_ARGS="$@"

# Modify dynamically the config file for supervisord replacing the
# $RUNTIME_ARGS pattern.
export RUNTIME_ARGS
envsubst < /vllm-workspace/supervisord.conf | sponge /vllm-workspace/supervisord.conf

# Now launch supervisord
exec supervisord -c ./supervisord.conf
