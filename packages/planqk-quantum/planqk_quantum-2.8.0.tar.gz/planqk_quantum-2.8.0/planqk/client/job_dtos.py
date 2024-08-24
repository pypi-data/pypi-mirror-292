import json
from enum import Enum
from typing import Optional, Dict, Set, Union

from pydantic import BaseModel


class INPUT_FORMAT(str, Enum):
    BRAKET_OPEN_QASM_V3 = "BRAKET_OPEN_QASM_V3"
    BRAKET_AHS_PROGRAM = "BRAKET_AHS_PROGRAM"
    OPEN_QASM_V3 = "OPEN_QASM_V3"
    IONQ_CIRCUIT_V1 = "IONQ_CIRCUIT_V1"
    QISKIT = "QISKIT"
    QOQO = "QOQO"


class JOB_STATUS(str, Enum):
    UNKNOWN = "UNKNOWN"
    ABORTED = "ABORTED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


JOB_FINAL_STATES = (JOB_STATUS.ABORTED, JOB_STATUS.COMPLETED, JOB_STATUS.CANCELLED, JOB_STATUS.FAILED)


class JobDto(BaseModel):
    provider: str
    shots: int = 1
    backend_id: str = None
    id: Optional[str] = None
    provider_job_id: Optional[str] = None
    session_id: Optional[str] = None
    input: Optional[Union[str, Dict]] = None
    input_format: Optional[INPUT_FORMAT] = None
    input_params: Optional[Dict] = None
    error_data: Optional[dict] = None
    started_at: Optional[str] = None
    created_at: Optional[str] = None
    ended_at: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[Set[str]] = None

    def __post_init__(self):
        if self.error_data is not None and isinstance(self.error_data, str):
            self.error_data = json.loads(self.error_data)
        if self.input_params is not None and isinstance(self.input_params, str):
            self.input_params = json.loads(self.input_params)


class RuntimeJobParamsDto(BaseModel):
    program_id: str
    image: Optional[str] = None
    hgp: Optional[str]
    log_level: Optional[str] = None
    session_id: Optional[str] = None
    max_execution_time: Optional[int] = None
    start_session: Optional[bool] = False
    session_time: Optional[int] = None
