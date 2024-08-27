"""The fermioniq.emulator_message module handles messages from the EmulatorJob.

The module contains the :py:meth:`EmulatorMessage` class, which represents a message
containing information about an EmulatorJob's events and status.
"""

from typing import Literal

from pydantic import BaseModel


class EmulatorMessage(BaseModel):
    """EmulatorMessage represents a message containing information about an EmulatorJob's events and status.

    Attributes
    ----------
    message_type
        The type of the message, always "event" for EmulatorMessage.
    event_type
        The type of event associated with the message.

        - 'LOG': A log message from the job.
        - 'STARTED': The job has started.
        - 'FINISHED': The job has finished.
    ts
        The timestamp of the event in UTC (ISO 8601 format).
    job_id
        The unique ID of the EmulatorJob.
    job_output
        The output associated with the event (e.g., log content).
    job_status_code
        The status code of the job execution.

        - 0: The job completed successfully.
        - -1: The job has not finished yet.
        - Non-zero values: The job encountered an error during execution.
    """

    message_type: Literal["event"]
    event_type: Literal["LOG", "STARTED", "FINISHED", "PING"]
    ts: str
    job_id: str
    job_output: str
    job_status_code: int | None = -1
