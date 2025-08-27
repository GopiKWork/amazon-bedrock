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

### AWS Access Requirements
- AWS account with appropriate permissions
- Access to Amazon Bedrock in us-west-2 region
- Access to Amazon SageMaker (for notebook 1)
- AWS CLI configured or environment credentials set up

### Required IAM Permissions

Your AWS user or role needs the following permissions:

#### For Amazon Bedrock (Notebooks 2 & 3):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2::foundation-model/openai.gpt-oss-20b-1:0"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

#### For Amazon SageMaker (Notebook 1):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sagemaker:CreateNotebookInstance",
                "sagemaker:DescribeNotebookInstance",
                "sagemaker:StartNotebookInstance",
                "sagemaker:StopNotebookInstance"
            ],
            "Resource": "*"
        }
    ]
}
```

#### Environment-Specific Configurations

**For SageMaker Execution Role:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

**For Local Development:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

#### Model Access Requirements:
- Navigate to Amazon Bedrock Console
- Go to Model Access in the left navigation
- Request Access for "OpenAI GPT OSS 20B"
- Wait for Approval (usually immediate for most accounts)
- Ensure you're using the us-west-2 region

#### Verifying Model Access:
```python
import boto3

bedrock = boto3.client('bedrock', region_name='us-west-2')
models = bedrock.list_foundation_models()
gpt_oss_models = [model for model in models['modelSummaries'] if 'gpt-oss' in model['modelId']]

if gpt_oss_models:
    print("GPT OSS models available:")
    for model in gpt_oss_models:
        print(f"  - {model['modelId']}")
else:
    print("No GPT OSS models found. Check model access in Bedrock console.")
```

## Environment Setup

You can run these notebooks in several environments. Choose the one that best fits your needs:

### Option 1: Amazon SageMaker Notebook Instance (Recommended for Notebook 1)

1. **Create a SageMaker Notebook Instance:**
   ```bash
   aws sagemaker create-notebook-instance \
       --notebook-instance-name gpt-oss-exploration \
       --instance-type ml.g4dn.xlarge \
       --role-arn arn:aws:iam::YOUR-ACCOUNT:role/SageMakerExecutionRole
   ```

2. **Clone this repository in the SageMaker environment:**
   ```bash
   git clone https://github.com/your-repo/gpt-oss-blog.git
   cd gpt-oss-blog
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Local Jupyter Environment

1. **Create and activate virtual environment:**
   ```bash
   # Using uv (recommended)
   uv venv gpt-oss-demo
   source gpt-oss-demo/bin/activate  # On macOS/Linux
   # or
   gpt-oss-demo\Scripts\activate  # On Windows
   
   # Using conda
   conda create -n gpt-oss-demo python=3.9
   conda activate gpt-oss-demo
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Jupyter:**
   ```bash
   jupyter lab
   # or
   jupyter notebook
   ```

### Option 3: Cloud Environments (Google Colab, AWS Cloud9, etc.)

1. **Upload the notebooks to your preferred cloud environment**
2. **Install dependencies in the first cell:**
   ```python
   !pip install boto3 openai aws-bedrock-token-generator langgraph langchain langchain-aws strands-agents
   ```

### AWS Credentials Configuration

Configure your AWS credentials using one of these methods:

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2

# Option 3: IAM role (if running on EC2/SageMaker)
# No additional configuration needed - uses instance profile
```

## Coding Style and Approach

This project follows a **proof-of-concept** approach designed for educational clarity:

### Design Principles
- **Simple and Direct**: Code uses straightforward implementations without complex abstractions
- **Educational Focus**: Each example is designed to demonstrate concepts clearly
- **Minimal Dependencies**: Uses only essential libraries to reduce setup complexity
- **Clear Examples**: Automotive diagnostic scenarios provide consistent, relatable context

### Code Characteristics
- Functions are simple and focused on single responsibilities
- Variable names are descriptive and self-documenting
- Minimal error handling to maintain code clarity
- Direct API calls without unnecessary wrapper layers
- Comments explain the "why" rather than the "what"

### Not Production-Ready
This code is intentionally simplified for learning purposes. For production use, you would want to add:
- Comprehensive error handling and retry logic
- Input validation and sanitization
- Logging and monitoring
- Configuration management
- Security best practices
- Performance optimizations

## Getting Started

### Recommended Learning Path

1. **Start with Model Exploration** (`00_gpt-oss-20B-explore.ipynb`)
   - Best run in SageMaker AI Studio for optimal performance
   - Learn about GPT OSS 20B architecture and capabilities
   - Understand Harmony format and reasoning levels

2. **Basic Bedrock Integration** (`01_basic_openai_bedrock_demo.ipynb`)
   - Can run in any Jupyter environment
   - Learn different ways to access Bedrock models
   - Understand authentication patterns and API approaches

3. **Advanced Agent Development** (`02_advanced_agents_demo.ipynb`)
   - Requires agent framework dependencies
   - Build sophisticated AI agents with tools
   - Compare different agent architectures

### Running the Notebooks

1. **Open your Jupyter environment** (SageMaker, local, or cloud)

2. **Navigate to the notebook directory**

3. **Start with the first notebook:**
   ```
   00_gpt-oss-20B-explore.ipynb
   ```

4. **Execute cells sequentially** - each notebook is designed to be run from top to bottom

5. **Follow the embedded explanations** - markdown cells provide context and learning objectives

### Quick Validation

Test your setup with this simple validation:

```python
import boto3
import openai

# Test AWS connection
sts = boto3.client('sts', region_name='us-west-2')
identity = sts.get_caller_identity()
print(f"AWS Identity: {identity['Arn']}")

# Test Bedrock access
bedrock = boto3.client('bedrock', region_name='us-west-2')
models = bedrock.list_foundation_models()
print("Bedrock connection successful")
```

## Automotive Use Cases

All scripts demonstrate vehicle diagnostic scenarios:
- Engine error code analysis (P0171, P0174)
- Multi-symptom diagnostics (noise + fuel efficiency)
- Preventive maintenance recommendations
- Emergency safety diagnostics

## Sample Output

### API Key Generation
```
Current role ARN: arn:aws:sts::123456789012:assumed-role/MyRole/session
Generated API Key (expires in 60 minutes):
sk-bedrock-abc123def456...
Bedrock endpoint: https://bedrock-runtime.us-west-2.amazonaws.com
```

### Diagnostic Analysis Example
```
=== Diagnostic Analysis ===
Based on the error codes P0171 and P0174, your 2020 Toyota Camry is experiencing a lean fuel mixture condition in both engine banks.

Analysis of the problem:
The engine is running lean, meaning there's too much air relative to fuel in the combustion mixture.

Possible causes:
1. Vacuum leak in intake system
2. Faulty Mass Air Flow (MAF) sensor
3. Clogged fuel injectors
4. Weak fuel pump

Recommended actions:
1. Inspect vacuum lines and intake manifold for leaks
2. Clean or replace MAF sensor
3. Test fuel pressure
4. Consider fuel system cleaning

Urgency level: Medium - Address within 1-2 weeks to prevent engine damage
```

### Multi-turn Conversation Example
```
=== Initial Diagnostic Analysis ===
[Detailed diagnostic response]

=== Follow-up Question ===
User: What would be the estimated cost to fix these issues?

=== Cost Estimate ===
Estimated repair costs:
- Vacuum leak repair: $150-300
- MAF sensor replacement: $200-400
- Fuel injector cleaning: $100-200
- Fuel pump replacement: $400-800 (if needed)

Total estimated range: $250-800 depending on root cause
```

## Troubleshooting

### Common Setup Issues

#### AWS Credentials Not Found
```bash
# Check if credentials are configured
aws sts get-caller-identity

# If not configured, set up credentials
aws configure
```

#### Bedrock Access Denied
- Verify you have the required IAM permissions (see Prerequisites section)
- Ensure you're using the us-west-2 region
- Check if the GPT OSS 20B model is available in your account
- You may need to request model access through the Bedrock console

#### Common Permission Errors

**Error: "AccessDeniedException"**
- Cause: Missing Bedrock permissions
- Solution: Ensure your user/role has `bedrock:InvokeModel` permission for the specific model ARN

**Error: "ValidationException: The model ID is not supported"**
- Cause: Model not available in your region or account
- Solution: Check model availability in Bedrock console, request access if needed

**Error: "UnauthorizedOperation"**
- Cause: Missing STS permissions for API key generation
- Solution: Add `sts:GetCallerIdentity` permission to your policy

#### Dependency Installation Issues
```bash
# If using conda and pip conflicts occur
conda install pip
pip install -r requirements.txt

# If using uv and packages not found
uv pip install --upgrade pip
uv pip install -r requirements.txt
```

#### Jupyter Kernel Issues
```bash
# Install kernel in virtual environment
python -m ipykernel install --user --name gpt-oss-demo --display-name "GPT OSS Demo"
```

### Performance Considerations

- **Notebook 1**: Requires significant compute resources (GPU recommended)
- **Notebooks 2 & 3**: Can run on standard CPU instances
- **API Rate Limits**: Bedrock has rate limits; add delays between requests if needed
- **Token Limits**: GPT OSS 20B has a 128K token context window

### Cost Considerations

**Bedrock Pricing:**
- Model invocation charged per 1,000 input/output tokens
- API key generation uses STS (no additional charge)

**SageMaker Pricing:**
- Notebook instances charged per hour while running
- GPU instances required for notebook 1 (higher cost)

**Cost Optimization Tips:**
- Stop SageMaker instances when not in use
- Use CPU-only instances for notebooks 2 & 3
- Monitor token usage in Bedrock
- Set up billing alerts for unexpected usage

### Getting Help

If you encounter issues:

1. Check AWS CloudTrail for detailed error messages
2. Use AWS Policy Simulator to test permissions
3. Review Bedrock documentation for latest requirements
4. Contact AWS Support for account-specific issues

### Known Limitations

- **Model Availability**: GPT OSS 20B availability may vary by region and account
- **SageMaker Costs**: Running notebook 1 on GPU instances incurs compute costs
- **API Keys**: Generated API keys expire after 60 minutes for security
## File 
Structure

```
openai-bedrock-demo/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── config.py                          # Configuration and utilities
├── generate_api_key.py                # API key generation
├── openai_chat_demo.py                # OpenAI SDK demonstration
├── bedrock_invoke_demo.py             # Bedrock InvokeModel demo
├── bedrock_converse_demo.py           # Bedrock Converse API demo
├── scenario_demo.py                   # Comprehensive scenarios
├── automotive_scenarios.py            # Additional use case data
├── strands_agent_demo.py              # Strands agent framework demo
├── langgraph_agent_demo.py            # LangGraph agent framework demo
├── test_all_scripts.py                # Automated testing suite
├── sample_diagnostic_report.txt       # Sample automotive diagnostic report
├── 01_basic_openai_bedrock_demo.ipynb # Basic demonstrations notebook
├── 02_advanced_agents_demo.ipynb      # Advanced agents notebook
└── openai-bedrock-demo/               # Virtual environment (created by uv)
```

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

## Model Information

- **Model**: OpenAI gpt-oss-20b (openai.gpt-oss-20b-1:0)
- **Context Window**: 128,000 tokens
- **Region**: us-west-2
- **Capabilities**: Text input/output, chat completion, conversation

## Next Steps

After testing these scripts, you can:
1. Adapt the automotive scenarios to your specific use case
2. Integrate the authentication patterns into your applications
3. Explore other OpenAI models available on Bedrock
4. Implement streaming responses for real-time applications