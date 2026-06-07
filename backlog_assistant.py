"""
Smart Backlog Assistant - Main Implementation
Integrates with OpenAI to process requirements into user stories
"""

import logging
import os
import time
from typing import List, Optional
import json

from openai import OpenAI, APIError, RateLimitError

from models import UserStory, ProcessingResult, PriorityLevel, StoryCategory
from prompts import SYSTEM_PROMPT, build_user_prompt, validate_prompt_output, PROMPT_CONFIG

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates input before sending to OpenAI"""
    
    MIN_LENGTH = 20  # Minimum characters for meaningful input
    MAX_LENGTH = 10000  # Reasonable limit for single processing
    
    @staticmethod
    def validate(text: str) -> tuple:
        """
        Validate input text
        
        Args:
            text: Input text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Input cannot be empty"
        
        if len(text) < InputValidator.MIN_LENGTH:
            return False, f"Input too short (minimum {InputValidator.MIN_LENGTH} characters)"
        
        if len(text) > InputValidator.MAX_LENGTH:
            return False, f"Input too long (maximum {InputValidator.MAX_LENGTH} characters)"
        
        return True, None


class BacklogAssistant:
    """
    Main class for processing requirements into user stories using OpenAI
    
    This class handles:
    - Input validation
    - Prompt construction
    - OpenAI API calls
    - Response parsing and validation
    - Error handling and retries
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize BacklogAssistant
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (gpt-4o, gpt-4, gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Initialized BacklogAssistant with model: {model}")
    
    def process_requirements(self, input_text: str) -> ProcessingResult:
        """
        Process requirements text and generate user stories
        
        Args:
            input_text: Raw requirements or meeting notes
            
        Returns:
            ProcessingResult with generated user stories
            
        Raises:
            ValueError: If input is invalid
            APIError: If OpenAI API call fails
        """
        logger.info("Starting requirements processing")
        start_time = time.time()
        
        # Validate input
        is_valid, error_msg = InputValidator.validate(input_text)
        if not is_valid:
            logger.error(f"Input validation failed: {error_msg}")
            raise ValueError(error_msg)
        
        logger.debug(f"Input validated ({len(input_text)} chars)")
        
        # Build prompt
        user_prompt = build_user_prompt(input_text)
        
        # Call OpenAI API with retry logic
        max_retries = 3
        response_data = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling OpenAI API (attempt {attempt + 1}/{max_retries})")
                response = self._call_openai_api(user_prompt)
                
                # Validate and parse response
                response_data = validate_prompt_output(response)
                logger.debug("Response validation successful")
                break
                
            except RateLimitError as e:
                logger.warning(f"Rate limited, retrying... (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed on attempt {attempt + 1}, retrying...")
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse OpenAI response after {max_retries} attempts: {e}")
                time.sleep(1)
            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        if response_data is None:
            raise RuntimeError("Failed to get valid response from OpenAI")
        
        # Convert response to ProcessingResult
        result = self._build_processing_result(response_data, input_text)
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Processing completed in {result.processing_time_ms:.2f}ms, "
            f"generated {len(result.user_stories)} stories"
        )
        
        return result
    
    def _call_openai_api(self, user_prompt: str) -> str:
        """
        Call OpenAI API with proper error handling
        
        Args:
            user_prompt: The user message to send
            
        Returns:
            Response text from OpenAI
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=PROMPT_CONFIG["temperature"],
                max_tokens=PROMPT_CONFIG["max_tokens"],
                top_p=PROMPT_CONFIG["top_p"],
                response_format={"type": "json_object"}  # Request JSON format
            )
            
            content = response.choices[0].message.content
            logger.debug(f"OpenAI response received ({len(content)} chars)")
            return content
            
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _build_processing_result(
        self, 
        response_data: dict, 
        input_text: str
    ) -> ProcessingResult:
        """
        Convert OpenAI response to ProcessingResult
        
        Args:
            response_data: Parsed JSON response from OpenAI
            input_text: Original input text
            
        Returns:
            ProcessingResult object
        """
        user_stories = []
        
        # Convert story dictionaries to UserStory objects
        for story_data in response_data.get("user_stories", []):
            try:
                # Parse priority (handle both enum values and strings)
                priority_str = story_data.get("priority", "Medium")
                priority = self._parse_priority(priority_str)
                
                # Parse category (handle both enum values and strings)
                category_str = story_data.get("category", "Feature")
                category = self._parse_category(category_str)
                
                story = UserStory(
                    title=story_data.get("title", ""),
                    description=story_data.get("description", ""),
                    acceptance_criteria=story_data.get("acceptance_criteria", []),
                    priority=priority,
                    category=category,
                    dependencies=story_data.get("dependencies", []),
                    estimated_effort=story_data.get("estimated_effort")
                )
                user_stories.append(story)
                logger.debug(f"Created user story: {story.title}")
                
            except Exception as e:
                logger.warning(f"Error creating user story from response: {e}")
                continue
        
        result = ProcessingResult(
            summary=response_data.get("summary", ""),
            user_stories=user_stories,
            key_requirements=response_data.get("key_requirements", []),
            input_length=len(input_text),
            model_used=self.model
        )
        
        return result
    
    @staticmethod
    def _parse_priority(priority_str: str) -> PriorityLevel:
        """Parse priority string to enum"""
        priority_mapping = {
            "high": PriorityLevel.HIGH,
            "medium": PriorityLevel.MEDIUM,
            "low": PriorityLevel.LOW
        }
        return priority_mapping.get(priority_str.lower(), PriorityLevel.MEDIUM)
    
    @staticmethod
    def _parse_category(category_str: str) -> StoryCategory:
        """Parse category string to enum"""
        category_mapping = {
            "feature": StoryCategory.FEATURE,
            "bug fix": StoryCategory.BUG_FIX,
            "improvement": StoryCategory.IMPROVEMENT,
            "technical debt": StoryCategory.TECHNICAL_DEBT,
            "infrastructure": StoryCategory.INFRASTRUCTURE,
            "security": StoryCategory.SECURITY,
            "performance": StoryCategory.PERFORMANCE
        }
        return category_mapping.get(category_str.lower(), StoryCategory.UNKNOWN)