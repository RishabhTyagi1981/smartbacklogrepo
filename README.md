# Smart Backlog Assistant

An AI-powered tool that transforms unstructured meeting notes and requirements into well-organized, actionable backlog items using OpenAI's GPT models and intelligent prompt engineering.

## Overview

This project demonstrates practical AI application in engineering workflow automation. It takes raw text input (meeting notes, requirements documents) and generates structured user stories with:
- Clear descriptions and acceptance criteria
- Priority suggestions
- Story categorization
- Key requirements summary

## Problem Statement

Engineering teams spend significant time manually converting meeting notes and requirements into properly formatted backlog items. This manual process is error-prone and inconsistent.

### Use Cases Addressed

1. **Post-Meeting Backlog Creation**
   - Input: Raw meeting notes
   - Output: Structured user stories ready for sprint planning
   - Example: "We discussed adding dark mode" → Full user story with AC

2. **Requirements Document Processing**
   - Input: Product requirements document
   - Output: Categorized task list with priorities
   - Example: Bulk processing of feature specifications

3. **Backlog Enhancement**
   - Input: Incomplete backlog items
   - Output: Enhanced items with criteria and clarity
   - Example: "Add login feature" → Complete user story

## Architecture

```
┌─────────────────────┐
│  Input Source       │
│  - Text Notes       │
│  - Requirements     │
│  - JSON Backlog     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Input Validator    │
│  - Format check     │
│  - Length check     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Prompt Engineer    │
│  - Context setup    │
│  - Requirements     │
│  - Few-shot ex.     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  OpenAI GPT API     │
│  - GPT-4o / 4       │
│  - Structured       │
│    output via JSON  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  JSON Parser        │
│  - Validate schema  │
│  - Handle errors    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Output Formatter   │
│  - User stories     │
│  - Summary report   │
│  - Logging          │
└─────────────────────┘
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- OpenAI API key (get one at https://platform.openai.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/RishabhTyagi1981/smartbacklogrepo.git
cd smartbacklogrepo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o
LOG_LEVEL=INFO
```

## Usage

### Basic Usage

```python
from backlog_assistant import BacklogAssistant

# Initialize with OpenAI API key
assistant = BacklogAssistant(api_key="sk-...")

# Process meeting notes
meeting_notes = """
We discussed adding two-factor authentication to our login system.
Users should be able to enable it in their settings.
We want email and SMS options. It should be optional initially.
We're thinking Q2 for this.
"""

result = assistant.process_requirements(meeting_notes)
print(result)
```

### Command Line Usage

```bash
python main.py --input notes.txt --output backlog.json --format json
```

### Example with File Input

```bash
# Process a requirements document
python main.py --input requirements.md --format detailed

# Process and save to JSON
python main.py --input meeting_notes.txt --output output.json
```

## Key Design Decisions

### 1. OpenAI Integration
- Uses **GPT-4o** for best quality (fallback to GPT-4 for cost control)
- Direct API calls via OpenAI Python library
- Structured output mode for reliable JSON responses
- Temperature set to 0.7 for consistency with some creativity

### 2. Prompt Engineering Strategy
- **System Prompt**: Sets AI role as expert backlog specialist
- **Few-Shot Examples**: 2 concrete examples of well-formatted user stories
- **Structured Output**: JSON schema with validation
- **Validation Layer**: Re-parses and validates OpenAI responses

### 3. Error Handling
- Input validation (non-empty, reasonable length)
- JSON parsing fallback with retry logic
- OpenAI API error handling with rate limiting
- Output verification before returning

### 4. Modularity
- Separate concerns: validation, prompt building, API calls, formatting
- Easy to swap OpenAI models or add other providers
- Configurable logging for debugging

## OpenAI Integration Details

### API Usage Pattern
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    temperature=0.7,
    response_format={"type": "json_object"},
    max_tokens=2000
)
```

### Why OpenAI?
- Strong understanding of business/engineering context
- Reliable JSON structured output
- Excellent few-shot learning capabilities
- Well-documented API with good error messages
- Reasonable pricing (~$0.003-0.015 per request)

## Testing

### Sample Test Cases

**Test 1: Simple Feature Request**
```
Input: "Users want dark mode"
Expected: User story with clear AC for dark mode toggle
Criteria: Should mention settings, theme switching, persistence
```

**Test 2: Complex Requirements**
```
Input: Meeting notes about auth system redesign
Expected: Multiple related stories with dependencies
Criteria: Should handle cross-cutting concerns
```

**Test 3: Malformed Input**
```
Input: Incomplete or unclear notes
Expected: Graceful error with suggestions
Criteria: Should not crash, provide helpful feedback
```

Run tests:
```bash
python -m pytest tests/ -v
```

## Project Structure

```
smartbacklogrepo/
├── main.py                    # CLI entry point
├── backlog_assistant.py        # Core BacklogAssistant class
├── prompts.py                 # Prompt templates
├── models.py                  # Data structures
├── requirements.txt            # Dependencies
├── .env.example               # Config template
├── README.md                  # This file
├── IMPLEMENTATION_LOG.md      # Detailed development notes
├── PROMPTS_USED.md           # Prompt engineering documentation
├── tests/
│   ├── test_basic.py
│   ├── test_openai_integration.py
│   ├── test_edge_cases.py
│   └── sample_inputs/
│       ├── meeting_notes.txt
│       ├── requirements.md
│       └── complex_scenario.json
├── examples/
│   ├── example_usage.py
│   ├── output_sample.json
│   └── run_examples.sh
└── docs/
    ├── ARCHITECTURE.md
    ├── PROMPT_ENGINEERING.md
    └── REFLECTION.md
```

## Prompt Engineering Examples

### System Prompt Used
```
You are an expert engineering team lead specializing in creating 
well-structured backlog items from raw requirements and meeting notes. 

Your task is to:
1. Analyze the provided text for user needs and features
2. Create clear, concise user stories following the format:
   As a [user type], I want [feature], so that [benefit]
3. Define 2-3 acceptance criteria for each story
4. Assign priority (High/Medium/Low)
5. Return valid JSON with no markdown formatting
```

### Few-Shot Example Structure
The prompt includes concrete examples showing:
- Properly formatted user story
- Complete acceptance criteria
- Realistic priority assignment
- Proper JSON structure

## Cost Considerations

- Uses GPT-4o (~$0.015 per 1K input tokens)
- Typical cost: ~$0.01-0.03 per backlog item
- Can process ~1000 items for ~$20-30
- Consider using GPT-3.5-turbo ($0.001 per 1K tokens) for lower cost

## Limitations & Future Improvements

### Current Limitations
- Single-file processing (could add batch processing)
- Depends on OpenAI API availability
- No semantic deduplication of generated stories
- Limited context awareness across multiple items

### Future Enhancements
1. Support for PDF input processing
2. Existing backlog comparison and deduplication
3. Integration with Jira/Linear APIs
4. Batch processing for high volume
5. Fine-tuned model for engineering domain
6. Confidence scores for each output
7. Fallback to Claude/other providers for redundancy

## References & AI Usage in Development

### AI Tools Used in This Project
- **ChatGPT/Claude**: Helped refine problem statement and architecture design
- **OpenAI API (GPT-4o)**: Core functionality for generating structured backlog items
- **Prompt Engineering**: Iterative refinement of prompts (documented in PROMPTS_USED.md)

### How AI Assisted Development
- Initial architecture brainstorming
- Prompt template design and iteration
- Error handling strategy discussion
- Code review suggestions

See IMPLEMENTATION_LOG.md for detailed development notes.

---

**Created by**: RishabhTyagi1981  
**OpenAI Integration**: Full  
**Last Updated**: June 2026