import datetime
from typing import Dict, List, Optional

from ._protobufs.commander_pb2 import (
    RunnerEvent,
    RuntimeLogEvent,
)


class RunState:
    """
    RunState tracks information about what happened during the course of a Bauplan
    job run (executed DAG).

    It represents the state of a run, including job ID, task lifecycle events, user logs,
    task start and stop times, failed nonfatal task descriptions, project directory,
    job status, and failed fatal task description.
    """

    job_id: str
    runner_events: List[RunnerEvent]
    runtime_logs: List[RuntimeLogEvent]
    tasks_started: Dict[str, datetime.datetime]
    tasks_stopped: Dict[str, datetime.datetime]
    failed_nonfatal_task_descriptions: Dict[str, bool]
    project_dir: str
    job_status: Optional[str]
    failed_fatal_task_description: Optional[str]

    def __init__(
        self,
        job_id: str,
        project_dir: str,
    ) -> None:
        self.runner_events = []
        self.job_id = job_id
        self.task_lifecycle_events = []
        self.user_logs = []
        self.tasks_started = {}
        self.tasks_stopped = {}
        self.failed_nonfatal_task_descriptions = {}
        self.project_dir = project_dir
        self.job_status = None
        self.failed_fatal_task_description = None


class PlanImportState:
    """
    PlanImportState tracks information about what happened during the course of an "plan import" job
    that plans a job to import a table from cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.
    """

    job_id: str
    plan: Optional[Dict] = None
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.runner_events = []


class ApplyPlanState:
    """
    ApplyPlanState tracks information about what happened during the course of an "apply import plan" job
    that executes the plan to import a table from cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.
    """

    job_id: str
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.runner_events = []
