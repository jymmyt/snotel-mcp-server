#!/bin/bash
cd /Users/jym/dev/weather/snotel-mcp-server
source .venv/bin/activate
LOGLEVEL=INFO python -m snotel_mcp_server
