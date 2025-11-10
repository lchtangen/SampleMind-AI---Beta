"""Recommendation endpoints"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token, verify_token_type
from app.api.v1.websocket import send_recommendations_update
from app.schemas import (
    ContextUpdateRequest,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendations import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
security = HTTPBearer()
service = RecommendationService()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials

    if not verify_token_type(token, "access"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    payload = decode_token(token)
    if payload is None or payload.get("sub") is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    return int(payload["sub"])


@router.post("/context", status_code=status.HTTP_202_ACCEPTED)
def update_context(
    request: ContextUpdateRequest,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Any:
    service.update_context(user_id, request.context)
    response = service.get_recommendations(user_id, RecommendationRequest(), db)
    background_tasks.add_task(send_recommendations_update, user_id, response.dict())
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/top", response_model=RecommendationResponse)
def get_recommendations(
    background_tasks: BackgroundTasks,
    request: RecommendationRequest = Depends(),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Any:
    response = service.get_recommendations(user_id, request, db)
    background_tasks.add_task(send_recommendations_update, user_id, response.dict())
    return response
