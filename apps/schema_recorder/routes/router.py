# apps/schema_recorder/routes/router.py

from fastapi import APIRouter, HTTPException, status

from apps.schema_recorder import service
from schemas import A3CPMessage

router = APIRouter(prefix="/schema-recorder", tags=["schema-recorder"])


@router.post(
    "/append",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
)
def append_schema_event(event: A3CPMessage) -> dict:
    # Route-level enforcement (even if schema allows optional)

    if event.session_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="session_id is required for schema recording",
        )
    if event.source is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="source is required for schema recording",
        )
    assert event.session_id is not None  # type narrowing for static analysis

    try:
        result = service.append_event(
            user_id=event.user_id,
            session_id=event.session_id,
            message=event,
        )
        return {"record_id": result.record_id, "recorded_at": result.recorded_at}

    except service.MissingSessionPath as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except service.EventTooLarge as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e)
        ) from e
    except service.PayloadNotAllowed as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e

    except service.RecorderIOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
