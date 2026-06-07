"""
Data Models for Smart Backlog Assistant
Using Pydantic for validation and serialization
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority levels for backlog items"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class StoryCategory(str, Enum):
    """Categories for user stories"""
    FEATURE = "Feature"
    BUG_FIX = "Bug Fix"
    IMPROVEMENT = "Improvement"
    TECHNICAL_DEBT = "Technical Debt"
    INFRASTRUCTURE = "Infrastructure"
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    UNKNOWN = "Unknown"


@dataclass
class UserStory:
    """Represents a single user story"""
    title: str
    description: str
    acceptance_criteria: List[str]
    priority: PriorityLevel
    category: StoryCategory
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "priority": self.priority.value,
            "category": self.category.value,
            "dependencies": self.dependencies,
            "estimated_effort": self.estimated_effort
        }


@dataclass
class ProcessingResult:
    """Result of processing input requirements"""
    summary: str
    user_stories: List[UserStory]
    key_requirements: List[str]
    input_length: int
    model_used: str
    processing_time_ms: float = 0.0
    
    def get_story_count(self) -> int:
        """Get total number of user stories"""
        return len(self.user_stories)
    
    def get_stories_by_priority(self, priority: PriorityLevel) -> List[UserStory]:
        """Get stories filtered by priority"""
        return [s for s in self.user_stories if s.priority == priority]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "summary": self.summary,
            "key_requirements": self.key_requirements,
            "user_stories": [story.to_dict() for story in self.user_stories],
            "statistics": {
                "total_stories": self.get_story_count(),
                "input_length": self.input_length,
                "processing_time_ms": self.processing_time_ms,
                "model_used": self.model_used,
                "by_priority": {
                    "high": len(self.get_stories_by_priority(PriorityLevel.HIGH)),
                    "medium": len(self.get_stories_by_priority(PriorityLevel.MEDIUM)),
                    "low": len(self.get_stories_by_priority(PriorityLevel.LOW))
                }
            }
        }


@dataclass
class ValidationError:
    """Represents a validation error"""
    field: str
    message: str
    value: Optional[str] = None