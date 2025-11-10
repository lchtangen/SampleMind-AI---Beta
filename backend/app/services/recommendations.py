from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Audio, AudioAnalysis
from app.schemas import (
    SessionContext,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationItem,
)
from app.services.context_cache import get_context_cache
from app.services.vector_store import get_vector_store, VectorMatch


class RecommendationService:
    def __init__(self):
        self.context_cache = get_context_cache()
        self.vector_store = get_vector_store()

    def update_context(self, user_id: int, context: SessionContext) -> None:
        self.context_cache.set_context(user_id, context)

    def get_recommendations(
        self,
        user_id: int,
        request: RecommendationRequest,
        db: Session,
    ) -> RecommendationResponse:
        context = self.context_cache.get_context(user_id) or SessionContext()
        if not self.vector_store.query(context, 1):
            self.vector_store.refresh(db)

        mode = (request.mode or settings.RECS_RECOMMENDATION_MODE).lower()
        suggestions = self._generate_suggestions(user_id, context, request.top_k, db, mode)
        return RecommendationResponse(context=context, suggestions=suggestions, mode=mode)

    def _generate_suggestions(
        self,
        user_id: int,
        context: SessionContext,
        top_k: int,
        db: Session,
        mode: str,
    ) -> List[RecommendationItem]:
        if mode == 'rules':
            return self._generate_rule_suggestions(user_id, context, top_k, db)

        matches: List[VectorMatch] = self.vector_store.query(context, max(top_k * 3, 10))
        suggestions: List[RecommendationItem] = []
        scored_items: List[tuple[float, RecommendationItem]] = []

        now = datetime.utcnow()

        for match in matches:
            entry = match.entry
            if entry.user_id != user_id:
                continue

            score = match.base_score
            components: Dict[str, float] = dict(match.components)
            rationale_parts: List[str] = []

            # Tempo alignment
            if context.bpm and entry.tempo:
                diff = abs(entry.tempo - context.bpm)
                tempo_component = max(0.0, 1.0 - diff / 12.0)
                weighted = 0.25 * tempo_component
                score += weighted
                components['tempo'] = weighted
                rationale_parts.append(f"Tempo within {diff:.1f} BPM")

            # Key alignment
            if context.key and entry.key:
                if context.key == entry.key:
                    score += 0.2
                    components['key'] = 0.2
                    rationale_parts.append("Exact key match")
                elif context.key.split()[0] == entry.key.split()[0]:
                    score += 0.1
                    components['key_relative'] = 0.1
                    rationale_parts.append("Relative key match")

            # Freshness boost (max 0.1)
            age_days = (now - entry.uploaded_at).days if entry.uploaded_at else 0
            freshness = max(0.0, 1.0 - (age_days / 14.0))
            freshness_component = 0.1 * freshness
            if freshness_component:
                score += freshness_component
                components['freshness'] = freshness_component
                rationale_parts.append("Fresh upload")

            tags = list(dict.fromkeys(entry.genres + entry.moods))  # preserve order
            rationale = "; ".join(rationale_parts) or None
            source = 'fusion'
            if 'embedding' in components:
                source = 'embedding-fusion'
            elif match.base_score > 0:
                source = 'heuristic'

            scored_items.append(
                (
                    score,
                    RecommendationItem(
                        audio_id=entry.audio_id,
                        filename=entry.filename,
                        score=max(score, 0.0),
                        rationale=rationale,
                        tags=tags,
                        tempo=entry.tempo,
                        source=source,
                        score_components=components,
                    ),
                )
            )

        scored_items.sort(key=lambda item: item[0], reverse=True)
        for _, item in scored_items[:top_k]:
            suggestions.append(item)

        if suggestions:
            return suggestions

        rule_candidates = self._generate_rule_suggestions(user_id, context, top_k, db)
        if rule_candidates:
            return rule_candidates

        # Fallback if no vector matches
        fallback_ids = self._fallback_candidates(db, user_id, top_k)
        for audio_id in fallback_ids:
            audio = db.query(Audio).filter(Audio.id == audio_id, Audio.user_id == user_id).first()
            if not audio:
                continue
            analysis: Optional[AudioAnalysis] = audio.analysis
            tags = []
            if analysis and analysis.genres:
                tags.extend(analysis.genres)
            if analysis and analysis.moods:
                tags.extend(analysis.moods)
            suggestions.append(
                RecommendationItem(
                    audio_id=audio_id,
                    filename=audio.filename,
                    score=0.1,
                    rationale="Recent addition",
                    tags=tags,
                    tempo=analysis.tempo if analysis else None,
                    source='fallback',
                    score_components={'fallback': 0.1},
                )
            )
        return suggestions

    def _generate_rule_suggestions(
        self,
        user_id: int,
        context: SessionContext,
        top_k: int,
        db: Session,
    ) -> List[RecommendationItem]:
        query = db.query(Audio).filter(Audio.user_id == user_id).outerjoin(AudioAnalysis)
        items: List[RecommendationItem] = []
        results = query.limit(top_k * 3 or 10).all()
        target_tempo = context.bpm
        target_key = context.key
        target_moods = set(context.mood_tags or [])

        for audio in results:
            analysis: Optional[AudioAnalysis] = audio.analysis
            score = 0.0
            components: Dict[str, float] = {}
            rationale_parts: List[str] = []

            if target_tempo and analysis and analysis.tempo:
                diff = abs(analysis.tempo - target_tempo)
                tempo_score = max(0.0, 1.0 - diff / 12.0)
                components['tempo_rules'] = tempo_score
                score += tempo_score
                rationale_parts.append(f"Tempo diff {diff:.1f} BPM")

            if target_key and analysis and analysis.key:
                if target_key == analysis.key:
                    components['key_rules'] = 0.5
                    score += 0.5
                    rationale_parts.append("Exact key match")

            if target_moods and analysis and analysis.moods:
                overlap = target_moods.intersection(analysis.moods)
                if overlap:
                    mood_score = min(len(overlap) * 0.1, 0.3)
                    components['mood_rules'] = mood_score
                    score += mood_score

            tags = []
            if analysis and analysis.genres:
                tags.extend(analysis.genres)
            if analysis and analysis.moods:
                tags.extend(analysis.moods)

            items.append(
                RecommendationItem(
                    audio_id=audio.id,
                    filename=audio.filename,
                    score=max(score, 0.0),
                    rationale="; ".join(rationale_parts) or None,
                    tags=tags,
                    tempo=analysis.tempo if analysis else None,
                    source='rules',
                    score_components=components or None,
                )
            )

        items.sort(key=lambda item: item.score, reverse=True)
        ranked = items[:top_k]
        if ranked:
            return ranked

        fallback_ids = self._fallback_candidates(db, user_id, top_k)
        fallback_items: List[RecommendationItem] = []
        for audio_id in fallback_ids:
            audio = db.query(Audio).filter(Audio.id == audio_id, Audio.user_id == user_id).first()
            if not audio:
                continue
            analysis: Optional[AudioAnalysis] = audio.analysis
            tags = []
            if analysis and analysis.genres:
                tags.extend(analysis.genres)
            if analysis and analysis.moods:
                tags.extend(analysis.moods)
            fallback_items.append(
                RecommendationItem(
                    audio_id=audio_id,
                    filename=audio.filename,
                    score=0.1,
                    rationale="Recent addition",
                    tags=tags,
                    tempo=analysis.tempo if analysis else None,
                    source='fallback',
                    score_components={'fallback': 0.1},
                )
            )
        return fallback_items

    @staticmethod
    def _fallback_candidates(db: Session, user_id: int, top_k: int) -> List[int]:
        query = db.query(Audio.id).filter(Audio.user_id == user_id).order_by(Audio.uploaded_at.desc())
        return [row[0] for row in query.limit(top_k).all()]
