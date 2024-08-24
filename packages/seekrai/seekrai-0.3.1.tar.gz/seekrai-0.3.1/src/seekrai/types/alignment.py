from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import Field

from seekrai.types.abstract import BaseModel


class AlignmentRequest(BaseModel):
    instructions: str = Field(
        default=..., description="Task description/instructions for the alignment task"
    )
    files: List[str] = Field(
        default=..., description="List of file ids to use for alignment"
    )


class AlignmentJobStatus(str, Enum):
    STATUS_PENDING = "pending"
    STATUS_QUEUED = "queued"
    STATUS_RUNNING = "running"
    STATUS_CANCEL_REQUESTED = "cancel_requested"
    STATUS_CANCELLED = "cancelled"
    STATUS_FAILED = "failed"
    STATUS_COMPLETED = "completed"


class AlignmentResponse(BaseModel):
    id: Optional[str] = Field(default=..., description="Alignment job ID")
    created_at: datetime | None = None
    status: AlignmentJobStatus | None = None


class AlignmentList(BaseModel):
    # object type
    object: Literal["list"] | None = None
    # list of fine-tune job objects
    data: List[AlignmentResponse] | None = None
