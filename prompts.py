"""
Prompt templates and engineering for OpenAI integration
Demonstrates prompt engineering best practices with examples
"""

from typing import List, Dict

# System prompt that sets the context and role
SYSTEM_PROMPT = """You are an expert engineering team lead specializing in creating well-structured backlog items from raw requirements and meeting notes.

Your expertise includes:
- Analyzing unstructured text for user needs, features, and technical requirements
- Writing clear, concise user stories following the format: "As a [user type], I want [feature], so that [benefit]"
- Defining measurable acceptance criteria
- Assigning appropriate priority levels
- Categorizing work properly

When processing input:
1. Identify all distinct features, requirements, or improvements mentioned
2. For each item, create a user story with clear description
3. Define 2-3 specific, measurable acceptance criteria
4. Assign a priority (High/Medium/Low) based on business value and urgency
5. Categorize the work (Feature, Bug Fix, Improvement, Technical Debt, etc.)
6. Extract key requirements as a summary list

IMPORTANT: Return ONLY valid JSON with no markdown formatting, no code blocks, and no extra text.
The JSON must be parseable by Python's json.loads() function."""


def get_few_shot_examples() -> str:
    """
    Few-shot examples to guide AI output format
    These examples demonstrate desired output structure and quality
    """
    examples = [
        {
            "input": "Users have been asking for a dark mode. We discussed adding a theme toggle in settings.",
            "expected_output": {
                "summary": "Add dark mode theme support to the application",
                "user_stories": [
                    {
                        "title": "Add dark mode theme toggle",
                        "description": "As a user, I want to toggle between light and dark themes in my settings, so that I can reduce eye strain during nighttime usage.",
                        "acceptance_criteria": [
                            "Dark mode theme is available in user settings",
                            "Theme preference is persisted across sessions",
                            "All UI components render correctly in dark mode",
                            "Contrast ratios meet WCAG AA standards"
                        ],
                        "priority": "High",
                        "category": "Feature"
                    }
                ],
                "key_requirements": [
                    "Dark mode theme implementation",
                    "Theme persistence in user preferences",
                    "Accessibility compliance (WCAG AA)"
                ]
            }
        },
        {
            "input": "We need to improve our login flow. Add two-factor authentication with email and SMS options. Make it optional for now but plan for mandatory later.",
            "expected_output": {
                "summary": "Implement two-factor authentication system with email and SMS support",
                "user_stories": [
                    {
                        "title": "Add optional 2FA with email verification",
                        "description": "As a user, I want to enable optional two-factor authentication via email, so that my account has enhanced security.",
                        "acceptance_criteria": [
                            "Users can enable/disable email 2FA in security settings",
                            "Verification email is sent on login",
                            "Login is blocked until email code is verified",
                            "Codes expire after 10 minutes"
                        ],
                        "priority": "High",
                        "category": "Security"
                    },
                    {
                        "title": "Add optional 2FA with SMS verification",
                        "description": "As a user, I want to receive SMS codes for two-factor authentication, so that I have an alternative to email verification.",
                        "acceptance_criteria": [
                            "Users can enable/disable SMS 2FA in security settings",
                            "SMS is sent on login request",
                            "Login is blocked until SMS code is verified",
                            "SMS integration uses reliable provider (Twilio/etc)"
                        ],
                        "priority": "High",
                        "category": "Security"
                    }
                ],
                "key_requirements": [
                    "Two-factor authentication infrastructure",
                    "Email verification system",
                    "SMS provider integration",
                    "Security settings UI update"
                ]
            }
        }
    ]
    
    return examples


def build_user_prompt(input_text: str) -> str:
    """
    Build the user message with few-shot examples
    
    Args:
        input_text: The raw requirements/meeting notes to process
        
    Returns:
        Formatted prompt for OpenAI
    """
    examples = get_few_shot_examples()
    
    prompt = f"""Process the following requirements and generate structured user stories in JSON format.

EXAMPLES OF GOOD OUTPUT:

Example 1:
Input: "{examples[0]['input']}"
Expected output: {str(examples[0]['expected_output']).replace("'", '"')}

Example 2:
Input: "{examples[1]['input']}"
Expected output: {str(examples[1]['expected_output']).replace("'", '"')}

NOW PROCESS THIS INPUT:

Input: "{input_text}"

Generate a JSON response with this exact structure:
{{
    "summary": "Brief summary of all requirements",
    "key_requirements": ["requirement 1", "requirement 2", ...],
    "user_stories": [
        {{
            "title": "Story title",
            "description": "As a [user], I want [feature], so that [benefit]",
            "acceptance_criteria": ["criteria 1", "criteria 2", "criteria 3"],
            "priority": "High|Medium|Low",
            "category": "Feature|Bug Fix|Improvement|Technical Debt|Infrastructure|Security|Performance",
            "dependencies": []
        }},
        ...
    ]
}}

Return ONLY the JSON object, no additional text."""
    
    return prompt


def validate_prompt_output(response_text: str) -> Dict:
    """
    Validate and parse OpenAI response
    
    Args:
        response_text: Raw response from OpenAI
        
    Returns:
        Parsed and validated JSON
        
    Raises:
        ValueError: If response is not valid JSON or missing required fields
    """
    import json
    
    # Clean the response (remove potential markdown formatting)
    clean_text = response_text.strip()
    if clean_text.startswith("```"):
        # Remove markdown code blocks if present
        clean_text = clean_text.split("```")[1]
        if clean_text.startswith("json"):
            clean_text = clean_text[4:]
    clean_text = clean_text.strip()
    
    # Parse JSON
    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in OpenAI response: {e}")
    
    # Validate required fields
    required_fields = ["summary", "key_requirements", "user_stories"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate user story structure
    if not isinstance(data["user_stories"], list):
        raise ValueError("user_stories must be a list")
    
    for i, story in enumerate(data["user_stories"]):
        required_story_fields = ["title", "description", "acceptance_criteria", "priority", "category"]
        for field in required_story_fields:
            if field not in story:
                raise ValueError(f"Story {i} missing required field: {field}")
    
    return data


# Constants for prompt engineering
PROMPT_CONFIG = {
    "temperature": 0.7,  # Moderate creativity - not too random, not too fixed
    "max_tokens": 2000,  # Sufficient for multiple stories
    "top_p": 0.95,  # Nucleus sampling for diversity
    "frequency_penalty": 0.0,  # No penalty for repeated tokens
    "presence_penalty": 0.0,  # No penalty for new tokens
}

# Model selection strategy
MODEL_SELECTION = {
    "gpt-4o": {
        "cost_per_1k_input": 0.005,
        "cost_per_1k_output": 0.015,
        "best_for": "Best quality, complex requirements",
        "reliability": "Highest"
    },
    "gpt-4": {
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.006,
        "best_for": "Good quality, reasonable cost",
        "reliability": "High"
    },
    "gpt-3.5-turbo": {
        "cost_per_1k_input": 0.0005,
        "cost_per_1k_output": 0.0015,
        "best_for": "Simple requirements, cost-sensitive",
        "reliability": "Good"
    }
}