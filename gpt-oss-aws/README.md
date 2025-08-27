# GPT OSS 20B Model Exploration and Amazon Bedrock Integration

This project demonstrates how to explore and use OpenAI's GPT OSS 20B model through Amazon SageMaker and Amazon Bedrock. The solution includes three comprehensive Jupyter notebooks that walk through model exploration, basic Bedrock integration patterns, and advanced agent frameworks.

## Project Overview

This repository contains three educational notebooks designed for developers and researchers interested in working with OpenAI's open-source GPT OSS 20B model:

### 📚 Notebook 1: `00_gpt-oss-20B-explore.ipynb`
**Model Exploration with SageMaker AI Studio**
- Deep dive into GPT OSS 20B model architecture and characteristics
- Model parameter analysis and technical specifications
- Harmony format demonstration with different reasoning levels
- SageMaker AI Studio Jupyter space integration
- Performance metrics and benchmarks

### 🔧 Notebook 2: `01_basic_openai_bedrock_demo.ipynb`
**Basic Bedrock Integration Patterns**
- Generate short-term API keys for OpenAI compatibility with Bedrock
- Multiple authentication methods (API keys, AWS credentials)
- OpenAI SDK integration with Bedrock endpoints
- Direct Bedrock InvokeModel and Converse API usage
- Automotive diagnostic use cases throughout

### 🤖 Notebook 3: `02_advanced_agents_demo.ipynb`
**Advanced Agent Frameworks**
- Strands agent framework with tool integration
- LangGraph workflow agents with state management
- Real-world automotive diagnostic scenarios
- Tool-enabled agents with file reading and analysis capabilities
- Framework comparison and selection guidance

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Jupyter Lab or Jupyter Notebook environment
- Sufficient compute resources (GPU recommended for notebook 1)


#### Model Access Requirements:
- Navigate to Amazon Bedrock Console
- Go to Model Access in the left navigation
- Request Access for "OpenAI GPT OSS 20B"
- Wait for Approval (usually immediate for most accounts)
- Ensure you're using the us-west-2 region



## Key Features Demonstrated

1. **Multiple Authentication Methods**:
   - Short-term API keys for OpenAI compatibility
   - Direct AWS credential usage

2. **Different API Patterns**:
   - OpenAI SDK with Bedrock endpoints
   - Native AWS Bedrock InvokeModel
   - Bedrock Converse API for conversations

3. **Real-world Use Cases**:
   - Vehicle diagnostic analysis
   - Error code interpretation
   - Preventive maintenance planning
   - Emergency safety assessments
   - Fleet management optimization

4. **Advanced Agent Architectures**:
   - **Multi-Agent Systems (Strands)**: Specialized agents working in parallel
   - **Workflow Agents (LangGraph)**: State-based sequential processing
   - **Complex Prompt Engineering**: Enhanced automotive industry prompts
   - **Agent Orchestration**: Coordinated multi-perspective analysis

5. **Conversation Capabilities**:
   - Single-turn diagnostics
   - Multi-turn follow-up questions
   - Context-aware responses
   - Workflow state management

