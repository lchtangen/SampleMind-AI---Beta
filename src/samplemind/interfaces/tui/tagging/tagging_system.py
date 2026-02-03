"""
Comprehensive Tagging System for SampleMind TUI
Multi-file tagging, categories, and AI-powered suggestions
"""

import logging
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TagCategory(Enum):
    """Tag categories"""
    INSTRUMENT = "instrument"
    GENRE = "genre"
    MOOD = "mood"
    ENERGY = "energy"
    PRODUCTION = "production"
    USAGE = "usage"
    CUSTOM = "custom"


# Predefined tags by category
TAG_CATEGORIES = {
    TagCategory.INSTRUMENT: [
        "kick", "snare", "hi-hat", "clap", "crash", "tom", "cowbell",
        "bass", "guitar", "piano", "synth", "pad", "lead", "strings",
        "brass", "woodwind", "vocal", "drums", "percussion", "effect"
    ],
    TagCategory.GENRE: [
        "techno", "house", "electro", "deep-house", "minimal",
        "dubstep", "drum-and-bass", "trap", "dnb", "uk-garage",
        "ambient", "downtempo", "trip-hop", "experimental",
        "pop", "rock", "hip-hop", "r-and-b", "reggae", "folk", "jazz"
    ],
    TagCategory.MOOD: [
        "dark", "bright", "aggressive", "mellow", "chill", "energetic",
        "melancholic", "happy", "sad", "mysterious", "peaceful",
        "intense", "calm", "uplifting", "moody", "dreamy"
    ],
    TagCategory.ENERGY: [
        "low", "low-medium", "medium", "medium-high", "high", "very-high"
    ],
    TagCategory.PRODUCTION: [
        "clean", "dirty", "lo-fi", "polished", "raw", "distorted",
        "compressed", "layered", "minimal", "complex", "warm", "cold",
        "bright", "dark", "dry", "wet", "analog", "digital"
    ],
    TagCategory.USAGE: [
        "intro", "drop", "break", "breakdown", "build", "outro",
        "fill", "transition", "ambient", "background", "loop",
        "one-shot", "sample", "loop-ready"
    ],
}


@dataclass
class Tag:
    """Individual tag"""
    name: str
    category: TagCategory
    description: Optional[str] = None
    color: Optional[str] = None  # For UI rendering
    frequency: int = field(default=0)  # How many times used
    created_at: Optional[str] = None


@dataclass
class TaggingProfile:
    """Profile of tags for an analysis"""
    analysis_id: str
    tags: Set[str] = field(default_factory=set)
    custom_tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    notes: Optional[str] = None


class TaggingSystem:
    """Comprehensive tagging system for analyses"""

    def __init__(self) -> None:
        """Initialize tagging system"""
        self.profiles: Dict[str, TaggingProfile] = {}
        self.all_tags: Dict[str, Tag] = {}
        self.tag_index: Dict[str, Set[str]] = {}  # Tag name -> analysis IDs

        # Initialize predefined tags
        self._initialize_predefined_tags()

    def _initialize_predefined_tags(self) -> None:
        """Initialize predefined tags"""
        for category, tag_names in TAG_CATEGORIES.items():
            for tag_name in tag_names:
                tag_key = f"{category.value}:{tag_name}"
                self.all_tags[tag_key] = Tag(
                    name=tag_name,
                    category=category,
                    color=self._get_category_color(category),
                )

    @staticmethod
    def _get_category_color(category: TagCategory) -> str:
        """Get color for tag category"""
        colors = {
            TagCategory.INSTRUMENT: "cyan",
            TagCategory.GENRE: "green",
            TagCategory.MOOD: "magenta",
            TagCategory.ENERGY: "yellow",
            TagCategory.PRODUCTION: "blue",
            TagCategory.USAGE: "red",
            TagCategory.CUSTOM: "white",
        }
        return colors.get(category, "white")

    def create_profile(self, analysis_id: str) -> TaggingProfile:
        """Create new tagging profile"""
        if analysis_id not in self.profiles:
            self.profiles[analysis_id] = TaggingProfile(analysis_id=analysis_id)
            logger.debug(f"Created tagging profile: {analysis_id}")

        return self.profiles[analysis_id]

    def get_profile(self, analysis_id: str) -> Optional[TaggingProfile]:
        """Get tagging profile"""
        return self.profiles.get(analysis_id)

    def add_tag(
        self, analysis_id: str, tag_name: str, category: TagCategory = TagCategory.CUSTOM
    ) -> bool:
        """Add tag to analysis"""
        profile = self.create_profile(analysis_id)

        if category == TagCategory.CUSTOM:
            profile.custom_tags.add(tag_name)
        else:
            tag_key = f"{category.value}:{tag_name}"
            if tag_key in self.all_tags:
                profile.tags.add(tag_key)
                self.all_tags[tag_key].frequency += 1
            else:
                logger.warning(f"Unknown tag: {tag_key}")
                return False

        # Update tag index
        if tag_name not in self.tag_index:
            self.tag_index[tag_name] = set()
        self.tag_index[tag_name].add(analysis_id)

        logger.debug(f"Added tag '{tag_name}' to {analysis_id}")
        return True

    def remove_tag(
        self, analysis_id: str, tag_name: str
    ) -> bool:
        """Remove tag from analysis"""
        profile = self.get_profile(analysis_id)
        if not profile:
            return False

        removed = False

        if tag_name in profile.custom_tags:
            profile.custom_tags.remove(tag_name)
            removed = True

        # Check predefined tags
        for category in TagCategory:
            if category == TagCategory.CUSTOM:
                continue
            tag_key = f"{category.value}:{tag_name}"
            if tag_key in profile.tags:
                profile.tags.remove(tag_key)
                if tag_key in self.all_tags:
                    self.all_tags[tag_key].frequency = max(
                        0, self.all_tags[tag_key].frequency - 1
                    )
                removed = True

        # Update index
        if tag_name in self.tag_index and analysis_id in self.tag_index[tag_name]:
            self.tag_index[tag_name].remove(analysis_id)

        if removed:
            logger.debug(f"Removed tag '{tag_name}' from {analysis_id}")

        return removed

    def add_tags_batch(
        self, analysis_id: str, tags: List[str], category: TagCategory = TagCategory.CUSTOM
    ) -> int:
        """Add multiple tags at once"""
        count = 0
        for tag in tags:
            if self.add_tag(analysis_id, tag, category):
                count += 1

        logger.info(f"Added {count} tags to {analysis_id}")
        return count

    def get_all_tags(self, analysis_id: str) -> Set[str]:
        """Get all tags for analysis"""
        profile = self.get_profile(analysis_id)
        if not profile:
            return set()

        return profile.tags | profile.custom_tags

    def get_tags_by_category(
        self, analysis_id: str, category: TagCategory
    ) -> List[str]:
        """Get tags for specific category"""
        profile = self.get_profile(analysis_id)
        if not profile:
            return []

        if category == TagCategory.CUSTOM:
            return list(profile.custom_tags)

        tags = []
        prefix = f"{category.value}:"
        for tag_key in profile.tags:
            if tag_key.startswith(prefix):
                tags.append(tag_key[len(prefix) :])

        return tags

    def search_by_tag(self, tag_name: str) -> List[str]:
        """Find all analyses with a specific tag"""
        return list(self.tag_index.get(tag_name, set()))

    def search_by_tags(
        self, tags: List[str], match_all: bool = False
    ) -> List[str]:
        """Find analyses with tags (AND or OR logic)"""
        if not tags:
            return []

        if match_all:
            # AND: Find analyses with all tags
            result = self.tag_index.get(tags[0], set()).copy()
            for tag in tags[1:]:
                result &= self.tag_index.get(tag, set())
            return list(result)
        else:
            # OR: Find analyses with any tag
            result = set()
            for tag in tags:
                result |= self.tag_index.get(tag, set())
            return list(result)

    def suggest_tags(self, keywords: str) -> List[str]:
        """Suggest tags based on keywords"""
        keywords_lower = keywords.lower().split()
        suggestions = []

        # Search through all tags
        for tag_key, tag in self.all_tags.items():
            tag_name = tag.name
            for keyword in keywords_lower:
                if keyword in tag_name:
                    suggestions.append((tag_name, tag.frequency))
                    break

        # Sort by frequency and name
        suggestions.sort(key=lambda x: (-x[1], x[0]))
        return [tag[0] for tag in suggestions]

    def get_tag_statistics(self) -> Dict[str, Any]:
        """Get tagging statistics"""
        total_tags = len(self.all_tags)
        total_custom_tags = sum(
            len(p.custom_tags) for p in self.profiles.values()
        )
        total_taggings = sum(
            len(p.tags) + len(p.custom_tags) for p in self.profiles.values()
        )

        most_used = sorted(
            self.all_tags.items(), key=lambda x: -x[1].frequency
        )[:10]

        return {
            "total_predefined_tags": total_tags,
            "total_custom_tags": total_custom_tags,
            "total_taggings": total_taggings,
            "analyses_tagged": len(self.profiles),
            "most_used_tags": [(tag.name, tag.frequency) for _, tag in most_used],
        }

    def get_tag_list(
        self, category: Optional[TagCategory] = None
    ) -> List[str]:
        """Get list of available tags"""
        if category:
            return TAG_CATEGORIES.get(category, [])
        else:
            all_tags = []
            for tags in TAG_CATEGORIES.values():
                all_tags.extend(tags)
            return all_tags

    def export_tags(self, analysis_id: str) -> Dict[str, Any]:
        """Export tags for analysis"""
        profile = self.get_profile(analysis_id)
        if not profile:
            return {}

        return {
            "analysis_id": analysis_id,
            "predefined_tags": list(profile.tags),
            "custom_tags": list(profile.custom_tags),
            "notes": profile.notes,
            "metadata": profile.metadata,
        }

    def import_tags(self, analysis_id: str, data: Dict[str, Any]) -> bool:
        """Import tags for analysis"""
        profile = self.create_profile(analysis_id)

        # Import predefined tags
        for tag_key in data.get("predefined_tags", []):
            if tag_key in self.all_tags:
                profile.tags.add(tag_key)

        # Import custom tags
        for tag_name in data.get("custom_tags", []):
            profile.custom_tags.add(tag_name)

        # Import notes and metadata
        if "notes" in data:
            profile.notes = data["notes"]

        if "metadata" in data:
            profile.metadata = data["metadata"]

        logger.info(f"Imported tags for {analysis_id}")
        return True


# Global singleton instance
_tagging_system: Optional[TaggingSystem] = None


def get_tagging_system() -> TaggingSystem:
    """Get or create tagging system singleton"""
    global _tagging_system
    if _tagging_system is None:
        _tagging_system = TaggingSystem()
    return _tagging_system
