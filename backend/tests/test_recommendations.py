import math

from app.models.audio import Audio, AudioAnalysis, AudioStatus
from app.services.embedding import EmbeddingService
from app.services.recommendations import RecommendationService
from app.services import vector_store as vector_store_module
from app.schemas import RecommendationRequest, SessionContext


def _reset_vector_store():
    vector_store_module._vector_store = None  # type: ignore[attr-defined]


def _create_audio(
    db_session,
    user,
    tempo: float,
    key: str,
    moods=None,
    genres=None,
) -> Audio:
    audio = Audio(
        user_id=user.id,
        filename="sample.wav",
        original_filename="sample.wav",
        file_path="/uploads/sample.wav",
        file_format="wav",
        file_size=1024,
        status=AudioStatus.COMPLETED,
    )
    db_session.add(audio)
    db_session.commit()
    db_session.refresh(audio)

    analysis = AudioAnalysis(
        audio_id=audio.id,
        tempo=tempo,
        key=key,
        genres=genres or ["Electronic"],
        moods=moods or ["uplifting"],
    )
    db_session.add(analysis)
    db_session.commit()

    EmbeddingService(db_session).ensure_embedding(audio)
    return audio


def test_recommendation_scoring_matches_context(db_session, test_user):
    _reset_vector_store()
    primary = _create_audio(db_session, test_user, tempo=128.0, key="C major")
    _create_audio(db_session, test_user, tempo=90.0, key="D minor", moods=["moody"], genres=["LoFi"])

    service = RecommendationService()
    context = SessionContext(bpm=128.0, key="C major", mood_tags=["uplifting"])
    service.update_context(test_user.id, context)

    response = service.get_recommendations(
        test_user.id,
        RecommendationRequest(top_k=3),
        db_session,
    )

    assert response.suggestions, "Expected at least one recommendation"
    top = response.suggestions[0]
    assert top.audio_id == primary.id
    assert top.score_components is not None
    assert 'tempo' in top.score_components
    assert math.isclose(top.score_components['tempo'], 0.25, rel_tol=1e-3)
    assert top.source in {'fusion', 'embedding-fusion', 'heuristic'}


def test_recommendation_falls_back_when_no_vector_entries(db_session, test_user):
    _reset_vector_store()

    audio = Audio(
        user_id=test_user.id,
        filename="fallback.wav",
        original_filename="fallback.wav",
        file_path="/uploads/fallback.wav",
        file_format="wav",
        file_size=2048,
        status=AudioStatus.UPLOADED,
    )
    db_session.add(audio)
    db_session.commit()
    db_session.refresh(audio)

    service = RecommendationService()
    context = SessionContext()
    service.update_context(test_user.id, context)

    # Ensure the vector store has no cached entries so fallback path executes
    vector_store_module._vector_store = vector_store_module.VectorStore()  # type: ignore[attr-defined]

    response = service.get_recommendations(
        test_user.id,
        RecommendationRequest(top_k=1),
        db_session,
    )

    assert response.suggestions, "Fallback should return recent tracks"
    item = response.suggestions[0]
    assert item.source == 'fallback'
    assert item.audio_id == audio.id


def test_recommendations_rules_mode_uses_rule_engine(db_session, test_user):
    _reset_vector_store()
    contextual = _create_audio(db_session, test_user, tempo=120.0, key="G minor")
    unrelated = _create_audio(db_session, test_user, tempo=80.0, key="C major")

    service = RecommendationService()
    context = SessionContext(bpm=120.0, key="G minor", mood_tags=["uplifting"])
    service.update_context(test_user.id, context)

    response = service.get_recommendations(
        test_user.id,
        RecommendationRequest(top_k=2, mode='rules'),
        db_session,
    )

    assert response.suggestions
    top = response.suggestions[0]
    assert top.audio_id == contextual.id
    assert top.source == 'rules'
