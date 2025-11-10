"""Telemetry endpoints"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token, verify_token_type
from app.schemas import RecommendationTelemetryBatch

router = APIRouter(prefix="/telemetry", tags=["telemetry"])
security = HTTPBearer()
logger = logging.getLogger("telemetry")


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials

    if not verify_token_type(token, "access"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    payload = decode_token(token)
    if payload is None or payload.get("sub") is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    return int(payload["sub"])


@router.post("/recommendations", status_code=status.HTTP_202_ACCEPTED)
def track_recommendations(
    batch: RecommendationTelemetryBatch,
    user_id: int = Depends(get_current_user_id),
) -> Any:
    if not batch.events:
        return {"accepted": 0}

    for event in batch.events:
        logger.info(
            "recommendation_event",
            extra={
                "event": event.event,
                "audio_id": event.audio_id,
                "score": event.score,
                "rank": event.rank,
                "source": event.source,
                "metadata": event.metadata,
                "user_id": user_id,
                "session_id": batch.session_id,
            },
        )

    return {"accepted": len(batch.events)}
