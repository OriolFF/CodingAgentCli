#!/bin/bash
# Quick switcher for .env configurations

case "$1" in
  "granite")
    echo "Switching to Granite 3.3 configuration..."
    cp .env.granite .env
    echo "✅ Using Granite 3.3 for tool calling"
    ;;
  "optimized")
    echo "Switching to optimized configuration..."
    cp .env.optimized .env
    echo "✅ Using mixed models (qwen/gpt-oss/mistral)"
    ;;
  "generic")
    echo "Switching to generic configuration..."
    cp .env.generic .env
    echo "✅ Using default mistral for all"
    ;;
  *)
    echo "Usage: ./switch_env.sh [granite|optimized|generic]"
    echo ""
    echo "Available configurations:"
    echo "  granite    - Granite 3.3 for tool calling (recommended)"
    echo "  optimized  - Mixed models for specific tasks"
    echo "  generic    - All agents use mistral"
    echo ""
    echo "Current model: $(grep '^FILE_EDITOR_MODEL=' .env | cut -d= -f2)"
    ;;
esac
