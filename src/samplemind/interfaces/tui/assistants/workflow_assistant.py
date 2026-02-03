"""
Smart Workflow Assistant for SampleMind TUI
Learn user patterns, suggest next steps, auto-organize
"""

import logging
from typing import Optional, List, Dict, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class UsagePattern:
    """Pattern of sample usage"""
    sample_pair: Tuple[str, str]  # (sample1, sample2)
    frequency: int = 0
    last_used: Optional[datetime] = None
    co_occurrence_count: int = 0
    confidence_score: float = 0.0  # 0-1


@dataclass
class WorkflowSuggestion:
    """Suggested next step in workflow"""
    action: str  # "analyze_next", "organize", "export", etc.
    reason: str
    suggested_samples: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 0-1


@dataclass
class WorkflowTemplate:
    """Template workflow for common tasks"""
    name: str
    description: str
    steps: List[Dict[str, Any]]  # Ordered workflow steps
    tags: List[str] = field(default_factory=list)
    usage_count: int = 0


class WorkflowAssistant:
    """Smart workflow assistant"""

    def __init__(self) -> None:
        """Initialize workflow assistant"""
        self.usage_patterns: Dict[Tuple[str, str], UsagePattern] = {}
        self.sample_usage_history: List[Tuple[str, datetime]] = []
        self.workflow_history: List[Dict[str, Any]] = []
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.user_skill_level = "intermediate"
        self.min_pattern_frequency = 3  # Minimum times pair seen

    def learn_sample_usage(self, current_sample: str, previous_samples: List[str]) -> None:
        """
        Learn sample pairing patterns

        Args:
            current_sample: Currently analyzed sample
            previous_samples: Previously analyzed samples in session
        """
        now = datetime.now()

        # Record current sample usage
        self.sample_usage_history.append((current_sample, now))

        # Learn pairings from previous samples
        for prev_sample in previous_samples[-3:]:  # Consider recent 3 samples
            pair = tuple(sorted([current_sample, prev_sample]))

            if pair not in self.usage_patterns:
                self.usage_patterns[pair] = UsagePattern(sample_pair=pair)

            pattern = self.usage_patterns[pair]
            pattern.frequency += 1
            pattern.last_used = now
            pattern.co_occurrence_count += 1
            pattern.confidence_score = self._calculate_confidence(pattern)

        logger.debug(f"Learned usage: {current_sample} with {len(previous_samples)} previous samples")

    def get_workflow_suggestions(
        self,
        current_samples: List[str],
        analyzed_count: int,
        context: Dict[str, Any] = None,
    ) -> List[WorkflowSuggestion]:
        """
        Get workflow suggestions

        Args:
            current_samples: Currently analyzed samples
            analyzed_count: Total samples analyzed in session
            context: Optional context (genre, tempo, etc.)

        Returns:
            List of suggestions
        """
        suggestions: List[WorkflowSuggestion] = []

        if context is None:
            context = {}

        # Progressive suggestions based on session progress
        if analyzed_count == 1:
            suggestions.append(
                WorkflowSuggestion(
                    action="analyze_complementary",
                    reason="You've analyzed 1 sample. Try analyzing a complementary sample.",
                    confidence=0.8,
                )
            )

        elif analyzed_count == 3:
            suggestions.append(
                WorkflowSuggestion(
                    action="compare_samples",
                    reason="You have 3 samples now. Compare them to see differences.",
                    confidence=0.85,
                )
            )

        elif analyzed_count == 5:
            suggestions.append(
                WorkflowSuggestion(
                    action="tag_and_organize",
                    reason="Tag your samples for better organization.",
                    confidence=0.9,
                )
            )

        # Pattern-based suggestions
        pattern_suggestions = self._get_pattern_based_suggestions(current_samples)
        suggestions.extend(pattern_suggestions)

        # Context-based suggestions
        if context.get("genre"):
            suggestions.append(
                WorkflowSuggestion(
                    action="genre_workflow",
                    reason=f"Follow best practices for {context['genre']} production",
                    confidence=0.7,
                )
            )

        return suggestions[:3]  # Return top 3

    def suggest_next_samples(self, current_samples: List[str], limit: int = 5) -> List[Tuple[str, float]]:
        """
        Suggest next samples to analyze based on patterns

        Args:
            current_samples: Currently analyzed samples
            limit: Max suggestions

        Returns:
            List of (sample, score) tuples
        """
        suggestions: Dict[str, float] = {}

        for current in current_samples[-2:]:  # Check recent samples
            for pair, pattern in self.usage_patterns.items():
                if current in pair and pattern.confidence_score > 0.6:
                    suggested = pair[1] if pair[0] == current else pair[0]

                    if suggested not in current_samples:
                        suggestions[suggested] = max(
                            suggestions.get(suggested, 0),
                            pattern.confidence_score,
                        )

        # Sort by score
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        return sorted_suggestions[:limit]

    def auto_organize_samples(
        self, samples: List[str]
    ) -> Dict[str, List[str]]:
        """
        Auto-organize samples by detected patterns

        Args:
            samples: List of sample paths

        Returns:
            Dictionary of organization (category -> samples)
        """
        organization: Dict[str, List[str]] = defaultdict(list)

        # Group by detected pairs/clusters
        placed = set()
        for pair, pattern in sorted(
            self.usage_patterns.items(),
            key=lambda x: x[1].confidence_score,
            reverse=True,
        ):
            if pattern.confidence_score > 0.7:
                cluster_name = f"Cluster_{pattern.sample_pair[0][:8]}"

                for sample in pair:
                    if sample in samples and sample not in placed:
                        organization[cluster_name].append(sample)
                        placed.add(sample)

        # Place remaining in default
        for sample in samples:
            if sample not in placed:
                organization["Other"].append(sample)

        return dict(organization)

    def get_smart_template(self, workflow_type: str) -> Optional[WorkflowTemplate]:
        """
        Get smart template for workflow type

        Args:
            workflow_type: Type of workflow

        Returns:
            WorkflowTemplate or None
        """
        templates = {
            "drum_production": WorkflowTemplate(
                name="Drum Production",
                description="Complete drum kit production workflow",
                steps=[
                    {"step": 1, "action": "analyze_kick", "description": "Analyze kick drums"},
                    {"step": 2, "action": "analyze_snare", "description": "Analyze snare"},
                    {"step": 3, "action": "compare_drums", "description": "Compare drum hits"},
                    {"step": 4, "action": "tag_drums", "description": "Tag drum elements"},
                    {"step": 5, "action": "export_drum_kit", "description": "Export drum kit"},
                ],
                tags=["drums", "percussion", "production"],
            ),
            "sample_exploration": WorkflowTemplate(
                name="Sample Exploration",
                description="Exploratory sample analysis workflow",
                steps=[
                    {"step": 1, "action": "browse_library", "description": "Browse audio library"},
                    {"step": 2, "action": "analyze_batch", "description": "Batch analyze samples"},
                    {"step": 3, "action": "search_similar", "description": "Search similar samples"},
                    {"step": 4, "action": "save_favorites", "description": "Save favorites"},
                    {"step": 5, "action": "create_collection", "description": "Create collection"},
                ],
                tags=["exploration", "discovery", "sampling"],
            ),
            "remix_production": WorkflowTemplate(
                name="Remix Production",
                description="Remix and recontextualization workflow",
                steps=[
                    {
                        "step": 1,
                        "action": "import_acapella",
                        "description": "Import vocal acapella",
                    },
                    {"step": 2, "action": "analyze_acapella", "description": "Analyze acapella"},
                    {"step": 3, "action": "find_drums", "description": "Find matching drums"},
                    {"step": 4, "action": "find_bass", "description": "Find matching bass"},
                    {"step": 5, "action": "arrange_remix", "description": "Arrange remix"},
                ],
                tags=["remix", "arrangement", "production"],
            ),
        }

        return templates.get(workflow_type)

    def record_workflow_step(self, step_type: str, data: Dict[str, Any]) -> None:
        """
        Record a workflow step

        Args:
            step_type: Type of step
            data: Step data
        """
        workflow_entry = {
            "step": step_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        self.workflow_history.append(workflow_entry)

    def replay_workflow(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent workflow steps for replay

        Args:
            limit: Max steps to return

        Returns:
            List of workflow steps
        """
        return self.workflow_history[-limit:]

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        if not self.usage_patterns:
            return {}

        confident_patterns = [
            p for p in self.usage_patterns.values() if p.confidence_score > 0.7
        ]

        return {
            "total_patterns": len(self.usage_patterns),
            "confident_patterns": len(confident_patterns),
            "avg_confidence": sum(p.confidence_score for p in self.usage_patterns.values())
            / len(self.usage_patterns)
            if self.usage_patterns
            else 0,
            "workflow_steps_recorded": len(self.workflow_history),
            "samples_analyzed": len(self.sample_usage_history),
        }

    def _get_pattern_based_suggestions(
        self, current_samples: List[str]
    ) -> List[WorkflowSuggestion]:
        """Get suggestions based on learned patterns"""
        suggestions: List[WorkflowSuggestion] = []

        if not current_samples or not self.usage_patterns:
            return suggestions

        # Find samples commonly used together
        common_partners: Dict[str, float] = {}
        for current in current_samples:
            for pair, pattern in self.usage_patterns.items():
                if current in pair and pattern.frequency >= self.min_pattern_frequency:
                    partner = pair[1] if pair[0] == current else pair[0]
                    common_partners[partner] = max(
                        common_partners.get(partner, 0), pattern.confidence_score
                    )

        if common_partners:
            top_partner = max(common_partners.items(), key=lambda x: x[1])
            suggestions.append(
                WorkflowSuggestion(
                    action="analyze_partner",
                    reason=f"You often use samples together. Try {top_partner[0]}",
                    suggested_samples=[top_partner[0]],
                    confidence=top_partner[1],
                )
            )

        return suggestions

    def _calculate_confidence(self, pattern: UsagePattern) -> float:
        """Calculate confidence score for pattern"""
        # Frequency-based
        freq_score = min(pattern.frequency / 5, 1.0)

        # Recency-based
        if pattern.last_used:
            days_old = (datetime.now() - pattern.last_used).days
            recency_score = 1.0 / (1 + (days_old * 0.1))
        else:
            recency_score = 0.0

        # Combined
        confidence = (freq_score * 0.7) + (recency_score * 0.3)
        return min(confidence, 1.0)


# Global singleton instance
_workflow_assistant: Optional[WorkflowAssistant] = None


def get_workflow_assistant() -> WorkflowAssistant:
    """Get or create workflow assistant singleton"""
    global _workflow_assistant
    if _workflow_assistant is None:
        _workflow_assistant = WorkflowAssistant()
    return _workflow_assistant
