#!/usr/bin/env python3
"""
Smart Backlog Assistant - Main Entry Point
Transforms unstructured requirements into structured backlog items using OpenAI
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from backlog_assistant import BacklogAssistant
from models import ProcessingResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO"):
    """Configure logging level"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    logging.getLogger().setLevel(numeric_level)


def read_input_file(filepath: str) -> str:
    """Read input from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Loaded input from {filepath} ({len(content)} chars)")
        return content
    except FileNotFoundError:
        logger.error(f"Input file not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        sys.exit(1)


def save_output(result: ProcessingResult, output_path: str, output_format: str = "json"):
    """Save processed result to file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            if output_format == "json":
                json_data = {
                    "summary": result.summary,
                    "user_stories": [
                        {
                            "title": story.title,
                            "description": story.description,
                            "acceptance_criteria": story.acceptance_criteria,
                            "priority": story.priority.value,
                            "category": story.category.value
                        }
                        for story in result.user_stories
                    ],
                    "key_requirements": result.key_requirements,
                    "processing_metadata": {
                        "input_length": result.input_length,
                        "stories_generated": len(result.user_stories),
                        "model_used": result.model_used
                    }
                }
                json.dump(json_data, f, indent=2)
            else:  # detailed text format
                f.write(f"SUMMARY\n{'='*60}\n{result.summary}\n\n")
                f.write(f"KEY REQUIREMENTS\n{'='*60}\n")
                for req in result.key_requirements:
                    f.write(f"- {req}\n")
                f.write(f"\n\nUSER STORIES\n{'='*60}\n")
                for i, story in enumerate(result.user_stories, 1):
                    f.write(f"\nStory {i}: {story.title}\n")
                    f.write(f"Priority: {story.priority.value} | Category: {story.category.value}\n")
                    f.write(f"Description: {story.description}\n")
                    f.write(f"Acceptance Criteria:\n")
                    for ac in story.acceptance_criteria:
                        f.write(f"  - {ac}\n")
        
        logger.info(f"Output saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving output: {e}")
        return False


def format_output(result: ProcessingResult) -> str:
    """Format result for console display"""
    output = []
    output.append("=" * 70)
    output.append("SMART BACKLOG ASSISTANT - PROCESSING RESULT")
    output.append("=" * 70)
    
    output.append("\nSUMMARY")
    output.append("-" * 70)
    output.append(result.summary)
    
    output.append("\n\nKEY REQUIREMENTS IDENTIFIED")
    output.append("-" * 70)
    for req in result.key_requirements:
        output.append(f"• {req}")
    
    output.append("\n\nGENERATED USER STORIES")
    output.append("-" * 70)
    for i, story in enumerate(result.user_stories, 1):
        output.append(f"\n[Story {i}] {story.title}")
        output.append(f"Priority: {story.priority.value} | Category: {story.category.value}")
        output.append(f"\nDescription:\n{story.description}")
        output.append(f"\nAcceptance Criteria:")
        for ac in story.acceptance_criteria:
            output.append(f"  ✓ {ac}")
    
    output.append("\n" + "=" * 70)
    output.append(f"Model Used: {result.model_used} | Stories Generated: {len(result.user_stories)}")
    output.append("=" * 70)
    
    return "\n".join(output)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Smart Backlog Assistant - Transform requirements into user stories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process meeting notes and display result
  python main.py --input notes.txt
  
  # Process and save as JSON
  python main.py --input requirements.md --output backlog.json --format json
  
  # Process and save as detailed text
  python main.py --input notes.txt --output backlog.txt --format detailed
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input file path (text or markdown)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (optional, displays to console if omitted)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'detailed'],
        default='detailed',
        help='Output format (default: detailed)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--model',
        choices=['gpt-4o', 'gpt-4', 'gpt-3.5-turbo'],
        default='gpt-4o',
        help='OpenAI model to use (default: gpt-4o)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger.info("Starting Smart Backlog Assistant")
    
    # Read input
    logger.info(f"Reading input from: {args.input}")
    input_text = read_input_file(args.input)
    
    # Process with BacklogAssistant
    try:
        logger.info(f"Processing with model: {args.model}")
        assistant = BacklogAssistant(model=args.model)
        result = assistant.process_requirements(input_text)
        
        # Display result
        formatted_output = format_output(result)
        print(formatted_output)
        
        # Save if output file specified
        if args.output:
            logger.info(f"Saving output to: {args.output}")
            save_output(result, args.output, args.format)
            print(f"\n✓ Output saved to: {args.output}")
        
        logger.info("Processing completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())