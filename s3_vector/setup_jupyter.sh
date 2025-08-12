#!/bin/bash

# Setup Jupyter Environment for S3 Vector Demos
# This script ensures Jupyter is properly configured with all dependencies

echo "🔧 Setting up Jupyter environment for S3 Vector demos"
echo "====================================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Creating one with uv..."
    uv venv
    echo "Please activate the virtual environment and run this script again:"
    echo "source .venv/bin/activate  # On macOS/Linux"
    echo ".venv\\Scripts\\activate     # On Windows"
    exit 1
fi

echo ""
echo "📦 Installing/updating requirements including Jupyter..."
uv pip install -r requirements.txt

echo ""
echo "🧪 Testing imports..."
python -c "
try:
    import sentence_transformers
    import boto3
    import jupyter
    import jupyterlab
    import matplotlib
    print('✅ All required packages imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "You can now run Jupyter notebooks with:"
    echo "  uv run jupyter lab simple_demo/simple_demo.ipynb"
    echo "  uv run jupyter lab langchain_demo/langchain_demo.ipynb"
    echo "  uv run jupyter lab multimodal_patterns/multimodal_demo.ipynb"
    echo ""
    echo "Or start Jupyter Lab and navigate to notebooks:"
    echo "  uv run jupyter lab"
else
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi