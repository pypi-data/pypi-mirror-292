from typing import Dict, Optional

import grpc

from . import exceptions
from ._common import (
    JobStatus,
    _JobLifeCycleHandler,
    _lifecycle,
    _OperationContainer,
    _print_debug,
)
from ._protobufs.bauplan_pb2 import (
    JobId,
    RunnerInfo,
)
from .bpln_proto.commander.service.v2.service_pb2 import (
    ApplyImportPlanRequest,
    ApplyImportPlanResponse,
    CreateImportPlanRequest,
    CreateImportPlanResponse,
)
from .state import ApplyPlanState, PlanImportState


def _validate_plan(plan: Dict) -> None:
    """
    Placeholder for proper plan validation.
    Raises exception if the value is not valid.
    """
    if not plan or not isinstance(plan, dict):
        raise exceptions.InvalidPlanError(
            'invalid plan; plan must be a dict representation of an import plan'
        )
    pass


def _dump_plan_to_yaml(plan: Dict) -> str:
    import yaml

    yaml.Dumper.ignore_aliases = lambda *args: True
    return yaml.safe_dump(plan)


def _load_plan_from_yaml(plan: str) -> str:
    import yaml

    yaml.Dumper.ignore_aliases = lambda *args: True
    return yaml.safe_load(plan)


def _handle_apply_import_log(log: RunnerInfo, state: ApplyPlanState) -> bool:
    if log.runner_event.apply_plan_done.error_message:
        state.error = log.runner_event.apply_plan_done.error_message
        state.job_status = JobStatus.failed
        _print_debug(f'Apply plan failed, error is: {state.error}')
        return True
    if log.runner_event.apply_plan_done.success:
        state.job_status = JobStatus.success
        _print_debug('Apply plan successful')
        return True
    return False


def _handle_plan_import_log(log: RunnerInfo, state: PlanImportState) -> bool:
    if log.runner_event.import_plan_created.error_message:
        state.error = log.runner_event.import_plan_created.error_message
        state.job_status = JobStatus.failed
        _print_debug(f'Create import plan failed, error is: {state.error}')
        return True
    if log.runner_event.import_plan_created.success:
        state.job_status = JobStatus.success
        plan_yaml = log.runner_event.import_plan_created.plan_as_yaml
        if plan_yaml is not None:
            state.plan = _load_plan_from_yaml(plan_yaml)
        _print_debug('Create import plan success')
        return True
    return False


class _Import(_OperationContainer):
    @_lifecycle
    def plan(
        self,
        search_string: str,
        table_name: str,
        from_ref: str,
        append: bool = False,
        replace: bool = False,
        no_cache: bool = False,
        args: Optional[Dict[str, str]] = None,
        lifecycle_handler: _JobLifeCycleHandler = None,
    ) -> PlanImportState:
        """
        Create a table import plan from an S3 location.
        This is the equivalent of running through the CLI the ``bauplan import plan`` command.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """
        if not isinstance(table_name, str) or not table_name.strip():
            raise ValueError('table_name is required')
        if not isinstance(search_string, str) or not search_string.strip():
            raise ValueError('search_string is required')
        if not search_string.startswith('s3://'):
            raise ValueError('search_string must be an S3 path, e.g., s3://bucket-name/*.parquet')
        if not isinstance(from_ref, str) or not from_ref.strip():
            raise ValueError('from_ref is required')
        if not isinstance(replace, bool):
            raise ValueError('replace must be a bool')
        if not isinstance(append, bool):
            raise ValueError('append must be a bool')
        if replace and append:
            raise ValueError('only one of (append, replace) can be true')

        client_v1, metadata_v1 = self._common.get_commander_and_metadata(args)
        client_v2, metadata_v2 = self._common.get_commander_v2_and_metadata(args)

        _print_debug(
            'Create import plan',
            'search_string',
            search_string,
            'from_ref',
            from_ref,
            'table_name',
            table_name,
            'append',
            append,
            'replace',
            replace,
            'no_cache',
            no_cache,
        )

        response: CreateImportPlanResponse = client_v2.CreateImportPlan(
            CreateImportPlanRequest(
                search_string=search_string,
                trigger_run_opts={'cache': not no_cache},
                args=args or {},
                branch=from_ref,
                table=table_name,
                append=append,
                replace=replace,
            ),
            metadata=metadata_v2,
        )
        job_id = JobId(id=response.job_id)
        lifecycle_handler.register_job_id(job_id)
        _print_debug('Create import plan job_id', response.job_id)
        log_stream: grpc.Call = client_v1.SubscribeLogs(job_id, metadata=metadata_v1)
        lifecycle_handler.register_log_stream(log_stream)
        state = PlanImportState(job_id=job_id.id)
        for log in log_stream:
            if _handle_plan_import_log(log, state):
                break
        return state

    @_lifecycle
    def apply(
        self,
        onto_branch: str,
        plan: Dict,
        args: Optional[Dict[str, str]] = None,
        no_cache: bool = False,
        lifecycle_handler: _JobLifeCycleHandler = None,
    ) -> ApplyPlanState:
        """
        Apply a Bauplan table import plan for a given branch.
        This is the equivalent of running through the CLI the ``bauplan import apply`` command.

        The user needs to pass a dict of the plan, as generated by the `plan` function defined in this module.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """
        # make sure the inviariants are met
        if not plan or not isinstance(plan, dict):
            raise ValueError('`plan` dict is required')
        if not isinstance(onto_branch, str) or not onto_branch.strip():
            raise ValueError("onto_branch is required, e.g. 'myname.mybranch'")

        # this does basic validation for now
        _validate_plan(plan)
        client_v1, metadata_v1 = self._common.get_commander_and_metadata(args)
        client_v2, metadata_v2 = self._common.get_commander_v2_and_metadata(args)
        _print_debug(
            'Apply import plan',
            'onto_branch',
            onto_branch,
            'no_cache',
            no_cache,
        )
        plan_yaml = _dump_plan_to_yaml(plan)
        response: ApplyImportPlanResponse = client_v2.ApplyImportPlan(
            ApplyImportPlanRequest(
                plan_yaml=plan_yaml,
                trigger_run_opts={'cache': not no_cache},
                args=args or {},
                write_branch=onto_branch,
                merge=False,
            ),
            metadata=metadata_v2,
        )
        job_id = JobId(id=response.job_id)
        lifecycle_handler.register_job_id(job_id)
        _print_debug('Apply import plan job_id', response.job_id)
        log_stream: grpc.Call = client_v1.SubscribeLogs(
            job_id,
            metadata=metadata_v1,
        )
        lifecycle_handler.register_log_stream(log_stream)
        state = ApplyPlanState(job_id=job_id.id)
        for log in log_stream:
            if _handle_apply_import_log(log, state):
                break
        if not state.job_status:
            raise Exception(state.__repr__)
        return state
