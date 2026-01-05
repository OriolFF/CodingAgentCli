#!/bin/bash
# Script to create extended Ollama models with unlimited token generation

echo "Creating extended Ollama models with unlimited token generation..."
echo ""

# Create cogito-extended
echo "Creating cogito-extended from cogito:14b..."
ollama create cogito-extended <<'EOF'
FROM cogito:14b
PARAMETER num_predict -1
PARAMETER num_ctx 8192
PARAMETER temperature 0.7
EOF

if [ $? -eq 0 ]; then
    echo "✅ Successfully created cogito-extended"
    echo ""
    echo "To use it, update your .env file:"
    echo "CODE_GENERATOR_MODEL=ollama:cogito-extended"
    echo ""
else
    echo "❌ Failed to create cogito-extended"
    echo "Make sure Ollama is running and cogito:14b is pulled"
    exit 1
fi

# Test the extended model
echo "Testing cogito-extended..."
echo "Prompt: Generate a complete Python function to reverse a string"
ollama run cogito-extended "Generate a complete Python function to reverse a string. Include docstring and type hints." --verbose

echo ""
echo "Done! The extended model is ready to use."
echo "It will generate complete code without truncation."
