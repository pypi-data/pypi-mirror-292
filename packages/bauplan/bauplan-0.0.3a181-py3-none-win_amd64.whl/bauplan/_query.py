"""
The module contains functions to launch SQL queries on Bauplan and retrieve
the result sets in a variety of formats (arrow Table, generator, file).
"""

import json
from datetime import datetime
from typing import Any, Dict, Generator, Optional

import grpc
import pyarrow as pa
import pyarrow.flight as flight

from . import exceptions
from ._common import (
    BAUPLAN_VERSION,
    Constants,
    _get_or_validate_branch,
    _JobLifeCycleHandler,
    _lifecycle,
    _OperationContainer,
    _print_debug,
)
from ._protobufs.bauplan_pb2 import TriggerRunRequest


def _iterate_flight_stream_batches(
    reader: flight.FlightStreamReader, max_rows: Optional[int] = None
) -> Generator[pa.lib.RecordBatch, None, None]:
    rows = 0
    try:
        if reader is None:
            raise exceptions.NoResultsFoundError('No results found')
        chunk: Optional[pa.lib.RecordBatch] = reader.read_chunk()
        if chunk is not None:
            batch: pa.lib.RecordBatch = chunk.data
            yield batch
            if max_rows:
                rows += batch.num_rows
                if rows >= max_rows:
                    raise StopIteration
        else:
            raise StopIteration
    except StopIteration:
        pass


def _add_connector_strings_to_query(
    query: str,
    connector: Optional[str] = None,
    connector_config_key: Optional[str] = None,
    connector_config_uri: Optional[str] = None,
) -> str:
    """

    Add the connector strings to the query to allow the backend to direct the query to the correct engine.
    We assume that if the connector is not specified we use Bauplan as is; the other properties default to
    sensible values (check the docs for the details!).

    """
    if not connector:
        return query

    connector_string = f'-- bauplan: connector={connector}'
    connector_config_key_string = (
        f'-- bauplan: connector.config_key={connector_config_key}' if connector_config_key else ''
    )
    connector_config_uri_string = (
        f'-- bauplan: connector.config_uri={connector_config_uri}' if connector_config_uri else ''
    )

    return f'{connector_string}\n{connector_config_key_string}\n{connector_config_uri_string}\n{query}'


def _build_query_from_scan(
    table_name: str,
    columns: Optional[list] = None,
    filters: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Take as input the arguments of the scan function and build a SQL query
    using SQLGlot.

    :meta private:

    """
    from sqlglot import select

    cols = columns or ['*']
    q = select(*cols).from_(table_name).where(filters)
    if limit:
        q = q.limit(limit)

    return q.sql()


def _row_to_dict(
    batch: pa.lib.RecordBatch, row_index: int, schema: pa.lib.Schema, as_json: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Convert a row of a ``pyarrow.RecordBatch`` to a dictionary.

    :meta private:

    :param batch: The ``pyarrow.RecordBatch`` containing the row.
    :param row_index: The index of the row to convert.
    :param schema: The schema of the ``RecordBatch``.
    :param as_json: Whether or not to cast to JSON-compatible types (i.e. datetime -> ISO format string).
    :return: A dictionary representing the row.
    """
    row: Dict[str, Any] = {}
    for j, name in enumerate(schema.names):
        column: pa.lib.ChunkedArray = batch.column(j)
        value = column[row_index].as_py()
        if as_json:
            if isinstance(value, datetime):
                value = value.isoformat()
        row[name] = value
    return row


class _Query(_OperationContainer):
    @_lifecycle
    def query(
        self,
        query: str,
        max_rows: Optional[int] = None,
        no_cache: bool = False,
        branch_name: str = 'main',
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        return_flight_stream: Optional[bool] = None,
        args: Optional[Dict[str, Any]] = None,
        client_timeout: Optional[int | float | None] = None,
        lifecycle_handler: _JobLifeCycleHandler = None,
    ) -> pa.Table:
        """
        Execute a SQL query and return the results as a pyarrow.Table.

        If you prefer to return the raw FlightStreamReader, pass `return_flight_stream=True`.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """
        if max_rows is not None:
            # max_rows limits
            if not isinstance(max_rows, int) or not (0 < max_rows < 100000000):
                raise ValueError('max_rows must be positive integer 1-100000000')
        branch_name = _get_or_validate_branch(profile=self.profile, branch_name=branch_name)

        if args is not None and not isinstance(args, dict):
            raise ValueError('args must be a dict or None')
        if args:
            if branch_name is not None and 'read-branch' in args:
                raise ValueError('can only pass one of branch_name and args["read-branch"]')
            if 'read-branch' in args:
                branch_name = _get_or_validate_branch(profile=self.profile, branch_name=args['read-branch'])

        client, metadata = self._common.get_commander_and_metadata(args)

        # rebuild a query with the connector strings if specified
        # note that if the connector is not specified we get back the query as is
        query = _add_connector_strings_to_query(query, connector, connector_config_key, connector_config_uri)
        trigger_run_request: TriggerRunRequest = TriggerRunRequest(
            module_version=BAUPLAN_VERSION,
            args=args or {},
            query_for_flight=query,
            is_flight_query=True,
        )
        trigger_run_request.args['read-branch'] = branch_name
        if no_cache:
            trigger_run_request.args['runner-cache'] = 'off'
        job_id: TriggerRunRequest = client.TriggerRun(trigger_run_request, metadata=metadata)
        lifecycle_handler.register_job_id(job_id)
        log_stream: grpc.Call = client.SubscribeLogs(job_id, metadata=metadata)
        lifecycle_handler.register_log_stream(log_stream)
        flight_endpoint: Optional[str] = None
        for log in log_stream:
            _print_debug(log)
            ev = log.runner_event
            if ev and ev.WhichOneof('event') == 'flight_server_start':
                flight_endpoint = log.runner_event.flight_server_start.endpoint
                use_tls = log.runner_event.flight_server_start.use_tls
                break
        if not flight_endpoint:
            return None
        flight_protocol = 'grpc+tls' if use_tls else 'grpc'
        flight_client: flight.FlightClient = flight.FlightClient(
            f'{flight_protocol}://{flight_endpoint}',
        )
        lifecycle_handler.register_flight_client(flight_client)
        initial_options = flight.FlightCallOptions(
            headers=[Constants.FLIGHT_HEADER_AUTH],
            timeout=Constants.FLIGHT_INTIAL_TIMEOUT_SECONDS,
        )
        query_options = flight.FlightCallOptions(
            headers=[Constants.FLIGHT_HEADER_AUTH],
            timeout=Constants.FLIGHT_QUERY_TIMEOUT_SECONDS,
        )
        try:
            ticket: flight.Ticket = (
                next(flight_client.list_flights(options=initial_options)).endpoints[0].ticket
            )
        except grpc.RpcError as e:
            is_call_error = isinstance(e, grpc.CallError)
            is_deadline_exceeded = e.code() == grpc.StatusCode.DEADLINE_EXCEEDED
            if is_call_error and is_deadline_exceeded:
                raise TimeoutError(
                    'Initial Flight connection timed out after 1 second',
                ) from e
            raise e
        reader: flight.FlightStreamReader = flight_client.do_get(
            ticket,
            options=query_options,
        )
        if return_flight_stream:
            return reader
        if reader is None:
            raise exceptions.NoResultsFoundError('No results found')
        if max_rows:
            num_rows = 0
            data = None
            try:
                for batch in _iterate_flight_stream_batches(reader, max_rows):
                    for i in range(batch.num_rows):
                        row = _row_to_dict(batch, i, batch.schema)
                        if not data:
                            data = {k: [v] for k, v in row.items()}
                        else:
                            for k, v in row.items():
                                data[k].append(v)
                        if max_rows:
                            num_rows += 1
                            if num_rows >= max_rows:
                                raise StopIteration
            except StopIteration:
                pass
            return pa.table({k: v[:max_rows] for k, v in data.items()}, schema=batch.schema)
        results = reader.read_all()
        shutdown_results = flight_client.do_action(
            Constants.FLIGHT_ACTION_SHUTDOWN_QUERY_SERVER,
            query_options,
        )
        for _ in shutdown_results:
            pass

        return results

    def query_to_generator(
        self,
        query: str,
        branch_name: Optional[str] | None = None,
        no_cache: Optional[bool] = False,
        max_rows: Optional[int] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        client_timeout: Optional[int | float | None] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a SQL query and return the results as a generator, where each row is
        a Python dictionary.
        """
        as_json = False
        if args and args.get('as_json'):
            as_json = True
            del args['as_json']
        reader: flight.FlightStreamReader = self.query(
            query=query,
            max_rows=max_rows,
            no_cache=no_cache,
            branch_name=branch_name,
            connector=connector,
            connector_config_key=connector_config_key,
            connector_config_uri=connector_config_uri,
            return_flight_stream=True,
            args=args,
            client_timeout=client_timeout,
        )
        if reader is None:
            raise exceptions.NoResultsFoundError('No results found')
        as_json = False
        if args and args.get('as_json'):
            as_json = True
        num_rows = 0
        try:
            for batch in _iterate_flight_stream_batches(reader, max_rows):
                for i in range(batch.num_rows):
                    yield _row_to_dict(batch, i, batch.schema, as_json=as_json)
                    if max_rows:
                        num_rows += 1
                        if num_rows >= max_rows:
                            raise StopIteration
        except StopIteration:
            pass

    def query_to_file(
        self,
        filename: str,
        query: str,
        max_rows: Optional[int] = None,
        no_cache: Optional[bool] = False,
        branch_name: str = 'main',
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        client_timeout: Optional[int | float | None] = None,
    ) -> None:
        """
        Execute a SQL query and write the results to a file.
        """
        if filename.endswith('.json'):
            if not args:
                args = {}
            args['as_json'] = True
            with open(filename, 'w') as outfile:
                outfile.write('[\n')
                first_row: bool = True
                for row in self.query_to_generator(
                    query=query,
                    max_rows=max_rows,
                    no_cache=no_cache,
                    branch_name=branch_name,
                    connector=connector,
                    connector_config_key=connector_config_key,
                    connector_config_uri=connector_config_uri,
                    args=args,
                    client_timeout=client_timeout,
                ):
                    if not first_row:
                        outfile.write(',\n')
                        first_row = False
                    outfile.write(json.dumps(row))
                outfile.write('\n]')
        else:
            raise ValueError('Only .json extension is supported for filename')

    def scan(
        self,
        table_name: str,
        columns: Optional[list] = None,
        filters: Optional[str] = None,
        limit: Optional[int] = None,
        branch_name: str = 'main',
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        args: Optional[Dict] | None = None,
        client_timeout: Optional[int | float | None] = None,
        **kwargs: Any,
    ) -> pa.Table:
        """
        Execute a table scan (with optional filters) and return the results as an arrow Table.
        Note that this function uses SQLGlot to compose a safe SQL query,
        and then internally defer to the query_to_arrow function for the actual scan.
        """
        q = _build_query_from_scan(table_name, columns, filters, limit)
        return self.query(
            query=q,
            branch_name=branch_name,
            connector=connector,
            connector_config_key=connector_config_key,
            connector_config_uri=connector_config_uri,
            args=args,
            client_timeout=client_timeout,
            **kwargs,
        )
