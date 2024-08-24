from __future__ import annotations

import datetime
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import func_timeout
import grpc
import pyarrow  # type: ignore
import yaml  # type: ignore

from ._protobufs.bauplan_pb2 import CancelJobRequest, JobId
from ._protobufs.bauplan_pb2_grpc import CommanderServiceStub
from .bpln_proto.commander.service.v2 import service_pb2_grpc as v2


class Constants:
    METADATA_HEADER_API_KEY: str = 'x-bauplan-api-key'
    METADATA_FEATURE_FLAGS: str = 'x-bauplan-feature-flags'
    METADATA_PYPI_VERSION_KEY: str = 'x-bauplan-pypi-version'
    PORT: int = 35432
    ENV_API_KEY: str = 'BAUPLAN_API_KEY'
    ENV_PROFILE: str = 'BAUPLAN_PROFILE'
    FEATURE_FLAG_CHECK_PYPI_VERSION: str = 'check-pypi-version'
    FLIGHT_INTIAL_TIMEOUT_SECONDS: int = 30
    FLIGHT_QUERY_TIMEOUT_SECONDS: int = 600
    FLIGHT_HEADER_AUTH: tuple[bytes, bytes] = (
        b'authorization',
        'Bearer my_special_token'.encode(),
    )
    FLIGHT_ACTION_SHUTDOWN_QUERY_SERVER: bytes = b'shutdown'
    DEFAULT_TIMEOUT: int = 60 * 60 * 24 * 7
    JOB_STATUS_FAILED = 'FAILED'
    JOB_STATUS_SUCCESS = 'SUCCESS'
    JOB_STATUS_CANCELLED = 'CANCELLED'
    JOB_STATUS_TIMEOUT = 'TIMEOUT'
    JOB_STATUS_REJECTED = 'REJECTED'
    JOB_STATUS_UNKNOWN = 'UNKNOWN'


@dataclass
class JobStatus:
    canceled: str = Constants.JOB_STATUS_CANCELLED
    cancelled: str = Constants.JOB_STATUS_CANCELLED
    failed: str = Constants.JOB_STATUS_FAILED
    rejected: str = Constants.JOB_STATUS_REJECTED
    success: str = Constants.JOB_STATUS_SUCCESS
    timeout: str = Constants.JOB_STATUS_TIMEOUT
    unknown: str = Constants.JOB_STATUS_UNKNOWN


if sys.version_info[:2] >= (3, 8):
    from importlib import metadata
else:
    import importlib.metadata as metadata  # type: ignore


def get_metadata_version() -> None:
    return metadata.version(__package__ or 'bauplan')


BAUPLAN_VERSION: Optional[str] = None
try:
    BAUPLAN_VERSION = get_metadata_version()
except Exception:
    print('`bauplan` package not found')


class _OperationContainerBase:
    api_key: str
    profile: str

    def __init__(self, api_key: str, profile: str) -> None:
        self.api_key = api_key
        self.profile = profile


class _OperationContainer(_OperationContainerBase):
    """
    Base class for operation utilities that need to share authentication state.
    """

    def __init__(self, api_key: str, profile: str) -> None:
        super().__init__(api_key, profile)
        self._common = _Common(self.api_key, self.profile)


class _Common(_OperationContainerBase):
    def dial_commander(self) -> grpc.Channel:
        addr: str = ''
        env: Optional[str] = _get_env(self.profile)
        if env == 'local':
            addr = 'localhost:2758'
        elif env == 'dev':
            addr = 'commander-poc.use1.adev.bauplanlabs.com:443'
        elif env == 'qa':
            addr = 'commander-poc.use1.aqa.bauplanlabs.com:443'
        else:
            addr = 'commander-poc.use1.aprod.bauplanlabs.com:443'
        creds: grpc.ChannelCredentials = grpc.ssl_channel_credentials()
        conn: grpc.Channel = grpc.secure_channel(addr, creds)
        return conn

    def get_commander_and_metadata(
        self, args: Dict | None = None
    ) -> Tuple[CommanderServiceStub, List[Tuple[str, str]]]:
        conn: grpc.Channel = self.dial_commander()
        client: CommanderServiceStub = CommanderServiceStub(conn)
        metadata = self._make_grpc_metadata(args)
        return client, metadata

    def get_commander_v2_and_metadata(
        self, args: Dict | None
    ) -> Tuple[v2.V2CommanderServiceStub, List[Tuple[str, str]]]:
        conn: grpc.Channel = self.dial_commander()
        client = v2.V2CommanderServiceStub(conn)
        metadata = self._make_grpc_metadata(args)
        return client, metadata

    def get_lifecycle_handler(self) -> _JobLifeCycleHandler:
        return _JobLifeCycleHandler(self.api_key, self.profile)

    def _make_grpc_metadata(self, args: Dict | None) -> List[Tuple]:
        """
        This validates and extracts feature flags from args.
        This also optionally adds a feature flag to ignore the pypi version check in commander for local runs.
        """
        # api key
        metadata = [
            (Constants.METADATA_HEADER_API_KEY, self.api_key),
            (Constants.METADATA_PYPI_VERSION_KEY, BAUPLAN_VERSION),
        ]

        # feature flags
        feature_flags = (args or {}).get('feature_flags')
        if isinstance(feature_flags, dict) and feature_flags:
            if BAUPLAN_VERSION in ('local', 'bauplan'):
                feature_flags[Constants.FEATURE_FLAG_CHECK_PYPI_VERSION] = 'false'
            metadata.append((Constants.METADATA_FEATURE_FLAGS, json.dumps(feature_flags)))
            del args['feature_flags']

        return metadata


def _get_catalog_host(profile: str) -> str:
    addr: str = ''
    env = os.getenv('BPLN_ENV', '')
    if env == '':
        env = _load_config_profile(profile).get('env')
    if env == 'local':
        addr = f'http://localhost:{Constants.PORT}'
    elif env == 'dev':
        addr = 'https://catalog.use1.adev.bauplanlabs.com'
    elif env == 'qa':
        addr = 'https://catalog.use1.aqa.bauplanlabs.com'
    else:
        addr = 'https://catalog.use1.aprod.bauplanlabs.com'
    return addr


def _get_or_validate_branch(profile: str, branch_name: str | None = None) -> str:
    """
    Default branch is the local active branch, or 'main'.
    """
    if branch_name is not None:
        if not isinstance(branch_name, str) or branch_name == '':
            raise ValueError('branch_name must be a non-empty string')
    else:
        branch_name = _load_config_profile(profile).get('active_branch', 'main')
    return branch_name


def _get_api_key(profile: str, api_key: str | None = None, user_session_token: str | None = None) -> str:
    if user_session_token is not None:
        return None
    if api_key is None:
        api_key = ''
    if api_key == '':
        api_key = os.getenv(Constants.ENV_API_KEY, '')
    if api_key == '':
        api_key = _load_config_profile(profile).get('api_key', '')
    if api_key == '':
        raise EnvironmentError(
            f'No API key found in environment. Please update your ~/.bauplan/config.yml or set {Constants.ENV_API_KEY} or set profile in {Constants.ENV_PROFILE}.'  # noqa: S608
        )
    return api_key


def _get_env(profile: str) -> str:
    env = os.getenv('BPLN_ENV', '')
    if env == '':
        env = _load_config_profile(profile).get('env', '')
    else:
        return env
    if env == '':
        raise EnvironmentError('No Bauplan environment specified. Please update your ~/.bauplan/config.yml.')
    return env


def _get_log_ts_str(val: int) -> str:
    """
    Output ISO timestamp to the decisecond from a nanosecond integer timestamp input.
    """
    return str(datetime.datetime.fromtimestamp(round(val / 1000000000, 2)))[:21]


def _get_config_path() -> Path | None:
    home_dir = Path.home()
    config_path = home_dir / '.bauplan' / 'config.yml'
    if not config_path.is_file():
        return None
    return config_path


def _load_config_profile(profile: str = 'default') -> dict:
    _print_debug(f'loading config profile: {profile}')
    config_path = _get_config_path()
    if config_path is None:
        return {}
    with open(config_path, 'r') as config_file:
        config_data = yaml.safe_load(config_file)
    return config_data.get('profiles', {}).get(profile, {})


def _get_profile_and_api_key(
    profile: str | None, api_key: str | None, user_session_token: str | None = None, **kwargs
) -> Tuple[str, str | None]:
    """
    Load the user's api key and profile from the environment,
    the provided profile or api key, and the user's config file.

    user_session_token can be passed with profile

    Precedence:
        0. passed user session token/default env
        1. passed api key/default env
        2. passed profile/passed env
        3. BAUPLAN_API_KEY/default env
        4. BAUPLAN_PROFILE api key/BAUPLAN_PROFILE env
        5. config.yml api key/config.yml env

    Returns: profile, api_key
    """
    if profile and api_key:
        raise ValueError('only one of `profile` and `api_key` may be specified')
    if profile is not None and (not isinstance(profile, str) or not profile):
        raise ValueError('profile must be a valid string')
    if api_key is not None and (not isinstance(api_key, str) or not api_key):
        raise ValueError('profile must be a valid string')

    pro = None
    key = None

    if api_key is not None or user_session_token is not None:
        return pro or 'default', _get_api_key(None, api_key, user_session_token)

    if os.getenv(Constants.ENV_API_KEY):
        return pro or 'default', _get_api_key(None, api_key=os.getenv(Constants.ENV_API_KEY))

    # get auth from profile
    if profile is not None:
        pro = profile
    elif os.getenv(Constants.ENV_PROFILE):
        pro = os.getenv(Constants.ENV_PROFILE)
    # profile not provided
    if pro is None:
        if _get_config_path() is None:
            raise EnvironmentError(
                f'No API key found in arguments, environment, or config. Please pass credentials, update your ~/.bauplan/config.yml or set {Constants.ENV_API_KEY} or {Constants.ENV_PROFILE}.'  # noqa: S608
            )
    if pro is None:
        pro = 'default'

    config = _load_config_profile(pro)
    if not config:
        raise ValueError(f'profile "{pro}" not found')
    if 'api_key' not in config:
        raise ValueError(f'profile "{pro}" is missing field `api_key`')
    key = config['api_key']
    if not key or not isinstance(key, str):
        raise ValueError(f'profile "{pro}" field `api_key` is invalid')
    return pro, key


class _JobLifeCycleHandler(_OperationContainer):
    """
    Cancels an interrupted Bauplan run and closes the flight client and GRPC log stream connections.
    Currently supports TimeoutError.
    Future support: KeyboardInterrupt.
    """

    def __init__(self, api_key: Optional[str] = None, profile: Optional[str] = None) -> None:
        super().__init__(api_key, profile)
        self.job_id = None
        self.flight_client = None
        self.log_stream = None

    @property
    def is_authenticated(self) -> bool:
        # note - user session tokens are not supported for job operations
        return not (self.api_key is None and self.profile is None)

    def register_job_id(self, job_id: JobId) -> None:
        _print_debug(f'Registering job id in lifecycle handler: {job_id.id}')
        self.job_id = job_id

    def register_log_stream(self, log_stream: grpc.Call) -> None:
        if not self.job_id:
            raise ValueError('cannot call register_log_stream without first calling register_job_id')
        _print_debug('Registering log_stream in lifecycle handler')
        self.log_stream = log_stream

    def register_flight_client(self, flight_client: pyarrow.flight.FlightClient) -> None:
        if not self.job_id:
            raise ValueError('cannot call register_flight_client without first calling register_job_id')
        _print_debug('Registering flight client in lifecycle handler')
        self.flight_client = flight_client

    def shutdown_bauplan_job_on_timeout(self) -> None:
        """
        Cancel the job upon timeout.
        Try for 5 seconds to cancel the job, using another 5 seconds timeout.
        """
        if not self.is_authenticated:
            return
        if self.job_id:
            _print_debug(f'Canceling job: {self.job_id.id}')
            if self.log_stream:
                self.log_stream.cancel()
            if self.flight_client:
                self.flight_client.close()

            def cancel_job_with_timeout() -> None:
                client, metadata = self._common.get_commander_and_metadata()
                response = client.CancelJob(CancelJobRequest(job_id=self.job_id), metadata=metadata)
                _print_debug('Canceled job:')
                _print_debug(f'    id: {self.job_id.id}')
                _print_debug(f'    status: {response.status}')
                _print_debug(f'    message: {response.message}')

            func_timeout.func_timeout(5, cancel_job_with_timeout)


def _print_debug(*args, **kwargs) -> None:
    if os.getenv('BPLN_DEBUG'):
        print(*args, **kwargs)


def _lifecycle(operation: Callable) -> Callable:
    """
    Decorator to manage operation lifecycle including client timeout and graceful shutdown.
    Decorate internal funcations with this to allow users to pass timeouts.

    It's designed to decorate class methods of an _OperationContainer subclass (e.g. _Query)
    so it can pass credentials downstream.
    This means that the decorated method expects
    to receive a `self` arg of type _OperationContainer as the first arg.

    If you just want timeout capability on an arbitrary function,
    then the function needs to accept some first arg first.

    The decorated function must accept a `lifecycle_handler` kwarg of type _JobLifecycleHandler,
    or accept arbitrary **kwargs.

    Example:
    ```
    # a decorated class method of _OperationContainer subclass
    class _Fly(_OperationContainer):
        @_lifecycle
        def jump(self, lifecycle_handler):
            # this function now accepts a `client_timeout` arg
            do_stuff()

    this = _Fly()
    # this times out now
    this.jump(client_timeout=2)

    # some function that times out
    @_lifecycle
    def timeout_func(_=None, otherarg=None, **kwargs):
        # this function now accepts a `client_timeout` arg
        do_stuff()

    # this times out now
    timeout_func(client_timeout=2)
    ```

    Future TODO: use this to manage lifecycle events like Cmd-C / Ctrl-C.
    """

    def operation_with_client_timeout(
        *args, client_timeout: Optional[int] = Constants.DEFAULT_TIMEOUT, **kwargs
    ) -> Any:
        # if the operation function has self as the first arg, then it's a _OperationContainer method
        # ...and we can attempt to do a graceful shutdown
        if args and _OperationContainer in type(args[0]).__mro__:
            operation_container: _OperationContainer = args[0]
            lifecycle_handler = operation_container._common.get_lifecycle_handler()
        else:
            # this will handle timeouts without trying to do graceful shutdown
            lifecycle_handler = _JobLifeCycleHandler()

        if client_timeout is None:
            pass
        elif not (isinstance(client_timeout, int) or isinstance(client_timeout, float)):
            raise ValueError('timeout must be int|float > 0')
        elif client_timeout <= 0:
            raise ValueError('timeout must be int|float > 0')

        if client_timeout:
            try:
                # Don't pass the lifecycle handler downstream if it's not authenticated,
                # i.e. this is not an _OperationContainer class method
                if lifecycle_handler.is_authenticated:
                    kwargs['lifecycle_handler'] = lifecycle_handler
                return func_timeout.func_timeout(client_timeout, operation, args=args, kwargs=kwargs)
            except func_timeout.FunctionTimedOut as e:
                # when there's a timeout error, attempt to cancel any attached flight stream, log stream, and/or Job
                # if this isn't an authenticated _OperationContainer, we can't do any graceful shutdown
                lifecycle_handler.shutdown_bauplan_job_on_timeout()
                raise TimeoutError(f'task timed out after {client_timeout} seconds') from e

        return operation(*args, lifecycle_handler=lifecycle_handler, **kwargs)

    return operation_with_client_timeout
