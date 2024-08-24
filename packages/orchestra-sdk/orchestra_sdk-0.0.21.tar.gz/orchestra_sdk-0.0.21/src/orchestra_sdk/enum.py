from enum import Enum


class TaskRunStatus(Enum):
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"


class WebhookEventType(Enum):
    LOG = "LOG"
    UPDATE_STATUS = "UPDATE_STATUS"
