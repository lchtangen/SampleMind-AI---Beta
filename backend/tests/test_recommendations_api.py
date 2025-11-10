import math

from app.models.audio import Audio, AudioAnalysis, AudioStatus
from app.services.embedding import EmbeddingService
from app.services import vector_store as vector_store_module


def _reset_vector_store():
    vector_store_module._vector_store = None  # type: ignore[attr-defined]


def _create_audio(db_session, user, *, tempo: float | None = None, key: str | None = None):
    audio = Audio(
        user_id=user.id,
        filename="api_sample.wav",
        original_filename="api_sample.wav",
        file_path="/uploads/api_sample.wav",
        file_format="wav",
        file_size=4096,
        status=AudioStatus.COMPLETED,
    )
    db_session.add(audio)
    db_session.commit()
    db_session.refresh(audio)

    if tempo is not None or key is not None:
        analysis = AudioAnalysis(
            audio_id=audio.id,
            tempo=tempo,
            key=key,
            genres=["Electronic"],
            moods=["uplifting"],
        )
        db_session.add(analysis)
        db_session.commit()
        EmbeddingService(db_session).ensure_embedding(audio)

    return audio


def test_recommendations_api_returns_contextual_results(client, db_session, test_user, auth_headers):
    _reset_vector_store()
    primary = _create_audio(db_session, test_user, tempo=126.0, key="C major")
    _create_audio(db_session, test_user, tempo=90.0, key="D minor")

    response = client.post(
        "/api/v1/recommendations/context",
        json={
            "context": {
                "bpm": 126.0,
                "key": "C major",
                "mood_tags": ["uplifting"],
            }
        },
        headers=auth_headers,
    )
    assert response.status_code == 204

    response = client.get("/api/v1/recommendations/top?top_k=3", headers=auth_headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["suggestions"], "Expected at least one suggestion"
    assert payload["mode"] == "fusion"
    top = payload["suggestions"][0]
    assert top["audio_id"] == primary.id
    assert top["score_components"]
    assert math.isclose(top["score_components"].get("tempo", 0.0), 0.25, rel_tol=1e-2)


def test_recommendations_api_fallback_when_no_embeddings(client, db_session, test_user, auth_headers):
    _reset_vector_store()
    fallback_audio = _create_audio(db_session, test_user)

    response = client.post(
        "/api/v1/recommendations/context",
        json={"context": {}},
        headers=auth_headers,
    )
    assert response.status_code == 204

    vector_store_module._vector_store = vector_store_module.VectorStore()  # type: ignore[attr-defined]

    response = client.get("/api/v1/recommendations/top?top_k=1", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["suggestions"], "Fallback should yield at least one suggestion"
    suggestion = payload["suggestions"][0]
    assert suggestion["audio_id"] == fallback_audio.id
    assert suggestion["source"] == "fallback"


def test_recommendations_api_rule_mode(client, db_session, test_user, auth_headers):
    _reset_vector_store()
    contextual = _create_audio(db_session, test_user, tempo=100.0, key="D major")

    response = client.post(
        "/api/v1/recommendations/context",
        json={"context": {"bpm": 100.0, "key": "D major"}},
        headers=auth_headers,
    )
    assert response.status_code == 204

    response = client.get("/api/v1/recommendations/top?mode=rules&top_k=1", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["suggestions"]
    assert payload["mode"] == "rules"
    suggestion = payload["suggestions"][0]
    assert suggestion["audio_id"] == contextual.id
    assert suggestion["source"] == "rules"
