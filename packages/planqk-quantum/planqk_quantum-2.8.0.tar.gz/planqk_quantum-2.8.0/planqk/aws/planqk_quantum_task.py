from __future__ import annotations

import json
from typing import Any, Union, Optional

from braket.ahs.analog_hamiltonian_simulation import AnalogHamiltonianSimulation
from braket.annealing.problem import Problem
from braket.aws import AwsQuantumTask
from braket.aws.aws_session import AwsSession
from braket.aws.queue_information import QuantumTaskQueueInfo
from braket.circuits.circuit import Circuit, Gate, QubitSet
from braket.ir.blackbird import Program as BlackbirdProgram
from braket.ir.openqasm import Program as OpenQASMProgram
from braket.pulse.pulse_sequence import PulseSequence
from braket.tasks import AnnealingQuantumTaskResult, AnalogHamiltonianSimulationQuantumTaskResult
from planqk.client.client import _PlanqkClient
from planqk.client.job_dtos import JOB_STATUS, JobDto
from planqk.decorators import not_implemented
from planqk.job import PlanqkBaseJob


class PlanqkAwsQuantumTask(PlanqkBaseJob, AwsQuantumTask):

    def __init__(self,
                 task_id: Optional[str] = None,
                 job_details: Optional[JobDto] = None,
                 backend: Optional = None,
                 access_token: Optional[str] = None,
                 organization_id: Optional[str] = None,
                 planqk_client: _PlanqkClient = None):
        client = planqk_client if planqk_client else _PlanqkClient(access_token=access_token, organization_id=organization_id)
        PlanqkBaseJob.__init__(self, backend=backend, job_id=task_id, job_details=job_details, planqk_client=client)

    @staticmethod
    @not_implemented
    def create(
            aws_session: AwsSession,
            device_arn: str,
            task_specification: Union[
                Circuit,
                Problem,
                OpenQASMProgram,
                BlackbirdProgram,
                PulseSequence,
                AnalogHamiltonianSimulation,
            ],
            s3_destination_folder: AwsSession.S3DestinationFolder,
            shots: int,
            device_parameters: dict[str, Any] | None = None,
            disable_qubit_rewiring: bool = False,
            tags: dict[str, str] | None = None,
            inputs: dict[str, float] | None = None,
            gate_definitions: dict[tuple[Gate, QubitSet], PulseSequence] | None = None,
            quiet: bool = False,
            reservation_arn: str | None = None,
            *args,
            **kwargs,
    ) -> AwsQuantumTask:
        pass

    @not_implemented
    def metadata(self, use_cached_value: bool = False) -> dict[str, Any]:
        """Get quantum task metadata defined in Amazon Braket.

        Args:
            use_cached_value (bool): If `True`, uses the value most recently retrieved
                from the Amazon Braket `GetQuantumTask` operation, if it exists; if not,
                `GetQuantumTask` will be called to retrieve the metadata. If `False`, always calls
                `GetQuantumTask`, which also updates the cached value. Default: `False`.

        Returns:
            dict[str, Any]: The response from the Amazon Braket `GetQuantumTask` operation.
            If `use_cached_value` is `True`, Amazon Braket is not called and the most recently
            retrieved value is used, unless `GetQuantumTask` was never called, in which case
            it will still be called to populate the metadata for the first time.
        """
        pass

    def state(self, use_cached_value: bool = False) -> str:
        """The state of the quantum task.

        Args:
            use_cached_value (bool): If `True`, uses the value most recently retrieved
                from PlanQK.

        Returns:
            str: the job execution state.
        """
        state = PlanqkBaseJob._status(self, use_cached_value)
        return 'QUEUED' if state == JOB_STATUS.PENDING else state.value
        status = self.status()
        if status == JOB_STATUS.PENDING:
            return 'QUEUED'
        elif status == JOB_STATUS.ABORTED:
            return 'FAILED'
        else:
            return status.value

    @not_implemented
    def queue_position(self) -> QuantumTaskQueueInfo:
        """The queue position details for the quantum task."""
        pass

    @property
    def id(self) -> str:
        """Get the quantum task ID.

        Returns:
            str: The quantum task ID.
        """
        return super().id

    def cancel(self) -> None:
        """Cancel the quantum task."""
        super().cancel()

    @not_implemented
    def async_result(self):
        """Get the quantum task result asynchronously.

        Returns:
            asyncio.Task: Get the quantum task result asynchronously.
        """
        pass

    def result(
            self,
    ) -> AnalogHamiltonianSimulationQuantumTaskResult:
        """Get the quantum task result by polling PlanQK to see if the task is completed.
        Once the quantum task is completed, the result is returned as a `AnnealingQuantumTaskResult`

        This method is a blocking thread call and synchronously returns a result.
        Call `async_result()` if you require an asynchronous invocation.
        Consecutive calls to this method return a cached result from the preceding request.

        Returns:
            AnnealingQuantumTaskResult: The
            result of the quantum task, if the quantum task completed successfully; returns
            `None` if the quantum task did not complete successfully or the future timed out.
        """
        result = super()._result()
        return AnalogHamiltonianSimulationQuantumTaskResult.from_string(json.dumps(result))




