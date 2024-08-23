from typing import Optional

from qiskit.providers import JobV1, JobStatus, Backend
from qiskit.qobj import QobjExperimentHeader
from qiskit.result import Result
from qiskit.result.models import ExperimentResult, ExperimentResultData

from planqk.client.client import _PlanqkClient
from planqk.client.job_dtos import JobDto
from planqk.job import PlanqkBaseJob

JobStatusMap = {
    "CREATED": JobStatus.INITIALIZING,
    "PENDING": JobStatus.QUEUED,
    "RUNNING": JobStatus.RUNNING,
    "COMPLETED": JobStatus.DONE,
    "FAILED": JobStatus.ERROR,
    "CANCELLING": JobStatus.RUNNING,
    "CANCELLED": JobStatus.CANCELLED,
    "UNKNOWN": JobStatus.INITIALIZING,
}


class PlanqkQiskitJob(PlanqkBaseJob, JobV1):
    def __init__(self, backend: Optional[Backend], job_id: Optional[str] = None, job_details: Optional[JobDto] = None,
                 planqk_client: Optional[_PlanqkClient] = None):

        PlanqkBaseJob.__init__(self, backend=backend, job_id=job_id, job_details=job_details, planqk_client=planqk_client)
        JobV1.__init__(self, backend=backend, job_id=job_id, shots=self._job_details.shots)

    def submit(self):
        super()._submit()

    def result(self) -> Result:
        """
        Return the result of the job.
        """
        result_data = super()._result()

        experiment_result = ExperimentResult(
            shots=self._job_details.shots,
            success=True,
            status=JobStatus.DONE,
            data=ExperimentResultData(
                counts=result_data.get("counts") or {},
                memory=result_data.get("memory") or []
            ),
            # Header required for PennyLane-Qiskit Plugin as it identifies the result based on the circuit name which is always "circ0"
            header=QobjExperimentHeader(name="circ0")
        )

        result = Result(
            backend_name=self._backend.name,
            backend_version=self._backend.version,
            job_id=self._job_id,
            qobj_id=0,
            success=True,
            results=[experiment_result],
            sstatus=JobStatus.DONE,
            date=self._job_details.ended_at,
        )

        return result

    def status(self) -> JobStatus:
        """
        Return the status of the job.
        """
        status = super()._status()
        return JobStatusMap[status]

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of the job.
        """
        return {key: value for key, value in vars(self).items() if not key.startswith('_')}

    def backend(self) -> Backend:
        """Return the backend where this job was executed."""
        if self._backend is None:
            from planqk.qiskit import PlanqkQiskitBackend
            self._backend = PlanqkQiskitBackend(self._job_details.backend_id, planqk_client=self._client)
        return self._backend

    def queue_position(self):
        """
        Return the position of the job in the server queue.
        """
        return None


# Keep for backward compatibility reasons
PlanqkJob = PlanqkQiskitJob
