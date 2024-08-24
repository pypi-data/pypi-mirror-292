from __future__ import annotations

import json
import warnings
from typing import Any, Dict, Generator, List, Optional, Union

import grpc._channel
import pyarrow as pa
import requests

from . import exceptions
from ._common import (
    BAUPLAN_VERSION,
    Constants,
    _get_catalog_host,
    _get_profile_and_api_key,
    _lifecycle,
)
from ._import import ApplyPlanState, PlanImportState, _Import
from ._query import _Query
from ._run import RunState, _Run
from .schema import APIBranch, APIResponse, Ref, Table, TableField, TableWithMetadata


class Client:
    """
    A consistent interface to access Bauplan operations.

    **Using the client**

    .. code-block:: python

        import bauplan
        client = bauplan.Client()

        # query the table and return result set as an arrow Table
        my_table = client.query('SELECT sum(trips) trips FROM travel_table', branch_name='main')

        # efficiently cast the table to a pandas DataFrame
        df = mytable.to_pandas()

    **Notes on authentication**

    .. code-block:: python

        # by default, authenticate from BAUPLAN_API_KEY >> BAUPLAN_PROFILE >> ~/.bauplan/config.yml
        client = bauplan.Client()
        # client used ~/.bauplan/config.yml profile 'default'

        os.environ['BAUPLAN_PROFILE'] = "someprofile"
        client = bauplan.Client()
        # >> client now uses profile 'someprofile'

        os.environ['BAUPLAN_API_KEY'] = "mykey"
        client = bauplan.Client()
        # >> client now authenticates with api_key value "mykey", because api key > profile

        # specify authentication directly - this supercedes BAUPLAN_API_KEY in the environment
        client = bauplan.Client(api_key='MY_KEY')

        # specify a profile from ~/.bauplan/config.yml - this supercedes BAUPLAN_PROFILE in the environment
        client = bauplan.Client(profile='default')

    **Handling Exceptions**

    Catalog operations (branch/table methods) raise a subclass of ``bauplan.exceptions.BauplanError`` that mirror HTTP status codes.

        * 400: InvalidDataError
        * 401: UnauthorizedError
        * 403: AccessDeniedError
        * 404: ResourceNotFoundError e.g .ID doesn't match any records
        * 404: ApiRouteError e.g. the given route doesn't exist
        * 405: ApiMethodError e.g. POST on a route with only GET defined
        * 409: UpdateConflictError e.g. creating a record with a name that already exists
        * 429: TooManyRequestsError

    Run/Query/Scan/Import operations raise a subclass of ``bauplan.exceptions.BauplanError`` that represents, and also return a ``RunState`` object containing details and logs:

        * ``JobError`` e.g. something went wrong in a run/query/import/scan; includes error details

    Run/import operations also return a state object that includes a ``job_status`` and other details.
    There are two ways to check status for run/import operations:
        1. try/except the JobError exception
        2. check the ``state.job_status`` attribute

    Examples:
    .. code-block:: python

        try:
            state = client.run(...)
            state = client.scan(...)
            state = client.plan_import(...)
            state = client.apply_import(...)
            state = client.query(...)
        except bauplan.exceptions.JobError as e:
            ...

        state = client.run(...)
        if state.job_status != "success":
            ...

    ```

    :param api_key: (optional) Your unique Bauplan API key; mutually exclusive with ``profile``. If not provided, fetch precedence is 1) environment BAUPLAN_API_KEY 2) .bauplan/config.yml
    :param profile: (optional) The Bauplan config profile name to use to determine api_key; mutually exclusive with ``api_key``
    """

    def __init__(
        self,
        api_key: str | None = None,
        profile: str | None = None,
        **kwargs,
    ) -> None:
        pro, key = _get_profile_and_api_key(profile, api_key, **kwargs)
        self._private_profile = pro
        self._private_api_key = key

        _set_from_args(self, kwargs)

        # instantiate interfaces to authenticated modules
        self._query = _Query(self._private_api_key, self._private_profile)
        self._run = _Run(self._private_api_key, self._private_profile)
        self._import = _Import(self._private_api_key, self._private_profile)

    # Query

    def query(
        self,
        query: str,
        branch_name: str = 'main',
        max_rows: Optional[int] = None,
        no_cache: Optional[bool] = False,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        client_timeout: Optional[int | float | None] = None,
    ) -> pa.Table:
        """
        Execute a SQL query and return the results as a pyarrow.Table.
        Note that this function uses Arrow also internally, resulting
        in a fast data transfer.

        If you prefer to return the results as a pandas DataFrame, use
        the ``to_pandas`` function of pyarrow.Table.

        .. code-block:: python

            import bauplan

            client = bauplan.Client()

            # query the table and return result set as an arrow Table
            my_table = client.query('SELECT c1 FROM my_table', branch_name='main')

            # efficiently cast the table to a pandas DataFrame
            df = mytable.to_pandas()

        :param query: The Bauplan query to execute.
        :param branch_name: The branch to read from and write to (default: your local active branch, else 'main').
        :param max_rows: The maximum number of rows to return; default: ``None`` (no limit).
        :param no_cache: Whether to disable caching for the query (default: ``False``).
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param args: Additional arguments to pass to the query (default: None).
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.
        :return: The query results as a ``pyarrow.Table``.
        """
        try:
            return self._query.query(
                query=query,
                branch_name=branch_name,
                max_rows=max_rows,
                no_cache=no_cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                args=self._massage_run_args(args),
                client_timeout=client_timeout,
            )

        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_generator(
        self,
        query: str,
        branch_name: Optional[str] | None = None,
        max_rows: Optional[int] = None,
        no_cache: Optional[bool] = False,
        connector: Optional[str] | None = None,
        connector_config_key: Optional[str] | None = None,
        connector_config_uri: Optional[str] | None = None,
        args: Optional[Dict[str, Any]] = None,
        client_timeout: Optional[int | float | None] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a SQL query and return the results as a generator, where each row is
        a Python dictionary.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # query the table and iterate through the results one row at a time
            for row in client.query_to_generator('SELECT c1 FROM my_table', branch_name='main'):
                # do logic

        :param query: The Bauplan query to execute.
        :param branch_name: The branch to read from and write to (default: your local active branch, else 'main').
        :param max_rows: The maximum number of rows to return; default: ``None`` (no limit).
        :param no_cache: Whether to disable caching for the query (default: ``False``).
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param args: Additional arguments to pass to the query (default: ``None``).
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.
        :yield: A dictionary representing a row of query results.
        """
        try:
            return self._query.query_to_generator(
                query=query,
                max_rows=max_rows,
                no_cache=no_cache,
                branch_name=branch_name,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                args=self._massage_run_args(args),
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_file(
        self,
        filename: str,
        query: str,
        branch_name: str = 'main',
        max_rows: Optional[int] = None,
        no_cache: Optional[bool] = False,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        client_timeout: Optional[int | float | None] = None,
    ) -> None:
        """
        Execute a SQL query and write the results to a file.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # query the table and iterate through the results one row at a time
            for row in client.query_to_generator('SELECT c1 FROM my_table', branch_name='main'):
                # do logic

        :param filename: The name of the file to write the results to.
        :param query: The Bauplan query to execute.
        :param max_rows: The maximum number of rows to return; default: ``None`` (no limit).
        :param no_cache: Whether to disable caching for the query (default: ``False``).
        :param branch_name: The branch to read from and write to (default: your local active branch, else 'main').
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param args: Additional arguments to pass to the query (default: None).
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.
        """
        try:
            return self._query.query_to_file(
                filename=filename,
                query=query,
                max_rows=max_rows,
                no_cache=no_cache,
                branch_name=branch_name,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                args=self._massage_run_args(args),
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Run

    def run(
        self,
        project_dir: str = '.',
        branch_name: Optional[str] | None = None,
        id: Optional[str] = None,
        parameters: Optional[Dict[str, Union[str, int, float, bool]]] = None,
        args: Optional[Dict[str, Any]] = None,
        client_timeout: Optional[int | float | None] = None,
    ) -> RunState:
        """
        Run a Bauplan project and return the state of the run. This is the equivalent of
        running through the CLI the ``bauplan run`` command.

        :param project_dir: The directory of the project (where the ``bauplan_project.yml`` file is located).
        :param branch_name: The branch to read from and write to (default: your local active branch, else 'main').
        :param id: The ID of the run (optional). This can be used to re-run a previous run, e.g., on a different branch.
        :param parameters: Parameters for templating into SQL or Python models.
        :param args: Additional arguments (optional).
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The state of the run.
        """
        try:
            return self._run.run(
                project_dir=project_dir,
                id=id,
                parameters=parameters,
                branch_name=branch_name,
                args=self._massage_run_args(args),
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Scan

    def scan(
        self,
        table_name: str,
        branch_name: Optional[str] | None = None,
        columns: Optional[list] = None,
        filters: Optional[str] = None,
        limit: Optional[int] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        args: Optional[Dict[str, str]] | None = None,
        client_timeout: Optional[int | float | None] = None,
        **kwargs: Any,
    ) -> pa.Table:
        """
        Execute a table scan (with optional filters) and return the results as an arrow Table.

        Note that this function uses SQLGlot to compose a safe SQL query,
        and then internally defer to the query_to_arrow function for the actual
        scan.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # run a table scan over the data lake
            # filters are passed as a string
            my_table = client.scan(
                table_name='my_table',
                columns=['c1'],
                filter='c2 > 10'
                branch_name='main'
            )

        :param table_name: The table to scan.
        :param branch_name: The branch to read from and write to (default: your local active branch, else 'main').
        :param columns: The columns to return (default: ``None``).
        :param filters: The filters to apply (default: ``None``).
        :param args: dict of arbitrary args to pass to the backend.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The scan results as a ``pyarrow.Table``.
        """
        try:
            return self._query.scan(
                table_name=table_name,
                columns=columns,
                filters=filters,
                limit=limit,
                branch_name=branch_name,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                args=self._massage_run_args(args),
                client_timeout=client_timeout,
                **kwargs,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Catalog

    def get_branches(
        self,
        itersize: Optional[str] | None = None,
        limit: Optional[str] | None = None,
        name: str | None = None,
        user: str | None = None,
    ) -> Generator[APIBranch, None, None]:
        """
        Get the available data branches in the Bauplan catalog.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            for branch in client.get_branches():
                print(branch.name, branch.hash)

        :param itersize: int 1-500
        :param limit: int > 0
        :return: a list of Ref objects, each having attributes: "name", "hash"
        """
        path = '/v0/branches'
        params = {}
        if name:
            params['name'] = name.strip()
        if user:
            params['user'] = user.strip()
        for record in self._paginate_api(path, limit=limit, itersize=itersize, params=params):
            yield APIBranch.model_validate(record)

    def get_branch(
        self,
        branch_name: str,
        limit: Optional[int] = None,
        itersize: Optional[int] = None,
    ) -> Generator[Table, None, None]:
        """
        Get the tables and views in the target branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # retrieve only the tables as tuples of (name, kind)
            tables = [(b.name, b.kind) for b in client.get_branch('main')]

        :param branch_name: The name of the branch to retrieve.
        :return: A list of Table objects, each having "name", "kind" (e.g. TABLE)
        """
        warnings.warn(  # noqa: B028
            'In a future release, `get_branch` will return a APIBranch instance instead of a list of Table instances. The list of tables is be available in `get_tables`; please migrate to `get_tables`',
            DeprecationWarning,
        )
        for record in self._paginate_api(f'/v0/refs/{branch_name}/tables', limit=limit, itersize=itersize):
            yield Table.model_validate(record)

    def get_tables(
        self,
        branch_name: str,
        limit: Optional[int] = None,
        itersize: Optional[int] = None,
    ) -> Generator[Table, None, None]:
        """
        Get the tables and views in the target branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # retrieve only the tables as tuples of (name, kind)
            tables = client.get_tables('main')
            for table in tables:
                print(table.name, table.kind)

        :param branch_name: The name of the branch to retrieve.
        :return: A list of tables, each having "name", "kind" (e.g. TABLE)
        """
        for record in self._paginate_api(f'/v0/refs/{branch_name}/tables', limit=limit, itersize=itersize):
            yield Table.model_validate(record)

    def get_branch_metadata(self, branch_name: str) -> Ref:
        """
        Get the data and metadata for a branch.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            data = get_branch_metadata('main')
            # print the number of total commits on the branch
            print(data.num_total_commits)

        :param branch_name: The name of the branch to retrieve.
        :return: A dictionary of metadata of type RefMetadata
        """
        warnings.warn(  # noqa: B028
            'In a future release, `get_branch_metadata` will be named `get_branch`',
            DeprecationWarning,
        )
        out: APIResponse = self._make_api_call('get', f'/v0/refs/{branch_name}')
        return Ref.model_validate(out.data)

    def merge_branch(self, onto_branch: str, from_ref: str) -> bool:
        """
        Merge one branch into another.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert merge_branch(
                onto_branch='myzone.somebranch',
                from_ref='myzone.oldbranch'
            )

        :param onto_branch: The name of the merge target
        :param from_ref: The name of the merge source; either a branch like "main" or ref like "main@[sha]"
        :return: a boolean for whether the merge worked
        """
        self._make_api_call('post', f'/v0/refs/{from_ref}/merge/{onto_branch}')
        return True

    def create_branch(self, branch_name: str, from_ref: str) -> APIBranch:
        """
        Create a new branch at a given ref.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.create_branch(
                branch_name='myzone.newbranch',
                from_ref='main'
            )

        :param branch_name: The name of the new branch
        :param ref: The name of the base branch; either a branch like "main" or ref like "main@[sha]"
        :return: a boolean for whether the new branch was created
        """
        body = {'branch_name': branch_name, 'from_ref': from_ref}
        out: APIResponse = self._make_api_call('post', '/v0/branches', body=body)
        return APIBranch.model_validate(out.data)

    def delete_branch(self, branch_name: str) -> bool:
        """
        Delete a branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.delete_branch(branch_name='mybranch')

        :param branch_name: The name of the branch to delete.
        :return: A boolean for if the branch was deleted
        """
        self._make_api_call('delete', f'/v0/branches/{branch_name}')
        return True

    def get_table_with_metadata(
        self, branch_name: str, table_name: str, include_raw: bool = False
    ) -> TableWithMetadata:
        """
        Get the table data and metadata for a table in the target branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # get the fields and metadata for the taxi_zones table in the main branch
            table = client.get_table_with_metadata(branch_name='main', table_name='taxi_zones')

            # loop through the fields and print their name, required, and type
            for c in table.fields:
                print(c.name, c.required, c.type)

            # show the number of records in the table
            print(table.records)

        :param branch_name: The name of the branch to get the table from.
        :param table_name: The name of the table to retrieve.
        :param include_raw: Whether or not to include the raw metadata.json object as a nested dict
        :return: a TableWithMetadata object, optionally including the raw metadata.json object
        """
        warnings.warn(  # noqa: B028
            'In a future release, `get_table` will return a TableWithMetadata instance rather than a list of fields. The list of fields will be accessible in TableWithMetadata(...).fields',
            DeprecationWarning,
        )
        params = {'raw': 1 if include_raw else 0}
        out: APIResponse = self._make_api_call(
            'get', f'/v0/refs/{branch_name}/tables/{table_name}', params=params
        )
        return TableWithMetadata.model_validate(out.data)

    def get_table(self, branch_name: str, table_name: str) -> List[TableField]:
        """
        Get the fields metadata for a table in the target branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # get the fields and metadata for the taxi_zones table in the main branch
            fields = get_table(branch_name='main', table_name='taxi_zones')

            # loop through the fields and print their name, required, and type
            for c in fields:
                print(c.name, c.required, c.type)

        :param branch_name: The name of the branch to get the table from.
        :param table_name: The name of the table to retrieve.
        :return: a list of fields, each having "name", "required", "type"
        """
        warnings.warn(  # noqa: B028
            'In a future release, `get_table` will return a TableWithMetadata instance rather than a list of fields. The list of fields will be accessible in TableWithMetadata(...).fields',
            DeprecationWarning,
        )
        out: APIResponse = self._make_api_call('get', f'/v0/refs/{branch_name}/tables/{table_name}')
        return TableWithMetadata.model_validate(out.data).fields

    def drop_table(self, table_name: str, branch_name: str) -> bool:
        """
        Drop a table.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.drop_table(table_name='mytable', branch_name='mybranch')

        :param table_name: The name of the table to delete
        :param branch_name: The name of the branch on which the table is stored
        :return: A boolean for if the table was deleted
        """
        self._make_api_call('delete', f'/v0/branches/{branch_name}/tables/{table_name}')
        return True

    # Import Files to tables in Bauplan

    def plan_import(
        self,
        table_name: str,
        search_string: str,
        from_ref: str = 'main',
        append: bool = False,
        replace: bool = False,
        args: Optional[Dict] | None = None,
        client_timeout: Optional[int | float | None] = None,
    ) -> PlanImportState:
        """
        Create a table import plan from an S3 location.

        An **import** is an operation to create a table in Bauplan from a file in the cloud.
        This is the equivalent of running through the CLI the ``bauplan import plan`` command.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            s3_path = 's3://path/to/my/files/*.parquet'
            plan_state = client.plan_import(
                from_ref='main', # optional
                table_name='newtablename',
                search_string=s3_path,
            )
            if plan_state.error:
                plan_error_action(...)
            success_action(plan_state.plan)

        If you want to save the plan object output for record-keeping or future processing,
        you can use the `plan` object attribute to do something like:

        .. code-block:: python

            plan_state = client.plan_import(...)

            import yaml
            plan_dict = plan_state.plan
            yaml.safe_dump(plan_dict, open('path/to/file.yaml','w'))

        :param search_string: The filepath of the plan to import.
        :param table_name: The name of the table to import into.
        :param append: Append the data to an existing table. Mutually exclusive with `replace`.
        :param replace: Replace the data in an existing table. Mutually exclusive with `append`.
        :param table_name: The name of the table to import into.
        :param from_ref: The name of the branch to import from.
        :param args: dict of arbitrary args to pass to the backend
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.
        """
        try:
            return self._import.plan(
                search_string=search_string,
                table_name=table_name,
                from_ref=from_ref,
                replace=replace,
                append=append,
                args=args,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def apply_import(
        self,
        plan: Dict,
        onto_branch: str,
        args: Optional[Dict] | None = None,
        client_timeout: Optional[int | float | None] = None,
    ) -> ApplyPlanState:
        """
        Apply a Bauplan table import plan for a given branch and table.

        An **import** is an operation to create a table in Bauplan from a file in the cloud.
        This is the equivalent of running through the CLI the ``bauplan import apply`` command.

        .. code-block:: python

            import bauplan

            # get the object representing the table import plan
            s3_path = 's3://path/to/my/files/*.parquet'
            plan_state = client.plan_import(
                from_ref='main',
                table_name='newtablename',
                search_string=s3_path
            )
            if plan_state.error:
                plan_error_action(...)

            # apply the table import plan to create/replace a table on this branch
            apply_state = client.apply_import(
                plan=plan_state.plan,
                onto_branch='myname.mybranch',
            )
            if apply_state.error:
                apply_error_action(...)

        :param plan: dict representation of an import plan, generated by `client.plan_import`
        :param onto_branch: name of the branch on which to apply the plan
        :param args: dict of arbitrary args to pass to the backend
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.
        """
        try:
            return self._import.apply(
                plan=plan,
                onto_branch=onto_branch,
                args=self._massage_run_args(args),
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Helpers

    def _massage_run_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not args:
            args = {}
        if not isinstance(args, dict):
            raise ValueError('args must be a dict of {string: Any}}')
        if self._private_feature_flags:
            args['feature_flags'] = self._private_feature_flags
        return args

    @_lifecycle
    def _make_api_call(
        self,
        method: str,
        path: str,
        params: Dict | None = None,
        body: Dict | None = None,
        pagination_token: str | None = None,
    ) -> APIResponse:
        """
        Helper to make a request to the API.

        :meta private:
        """
        url = _get_catalog_host(self._private_profile) + path
        headers = {Constants.METADATA_PYPI_VERSION_KEY: BAUPLAN_VERSION}
        if self._private_user_session_token:
            headers = {'x-bauplan-user-session-token': self._private_user_session_token}
        elif self._private_api_key:
            headers = {'x-bauplan-api-key': self._private_api_key}
        if self._private_feature_flags:
            headers['x-bauplan-feature-flags'] = json.dumps(self._private_feature_flags)
        if pagination_token:
            params['pagination_token'] = pagination_token
        if body:
            if not isinstance(body, dict):
                raise exceptions.BauplanError(
                    f'SDK INTERNAL ERROR: API request body must be dict, not {type(body)}'
                )
            res = requests.request(method, url, headers=headers, timeout=5, params=params or {}, json=body)
        else:
            res = requests.request(method, url, headers=headers, timeout=5, params=params or {})
        out = APIResponse.model_validate(res.json())
        if out.metadata.error or res.status_code != 200:
            if res.status_code == 400:
                raise exceptions.InvalidDataError(out.metadata.error)
            if res.status_code == 401:
                raise exceptions.UnauthorizedError(out.metadata.error)
            if res.status_code == 403:
                raise exceptions.AccessDeniedError(out.metadata.error)
            if res.status_code == 404:
                if out.metadata.error == 'path method not found':
                    raise exceptions.ApiMethodError(out.metadata.error)
                raise exceptions.ResourceNotFoundError(out.metadata.error)
            if res.status_code == 409:
                raise exceptions.UpdateConflictError(out.metadata.error)
            if res.status_code == 429:
                raise exceptions.TooManyRequestsError(out.metadata.error)
            raise exceptions.BauplanError(f'unhandled API exception {res.status_code}: {out.metadata.error}')
        return out

    def _paginate_api(
        self,
        path: str,
        limit: int | None = None,
        itersize: int | None = None,
        params: Dict | None = None,
    ) -> Any | Generator[Any, None, None]:
        """
        Helper to paginate through a Bauplan API or only fetch a limited number of records.

        Works if the route returns lists of records and accepts a pagination token.

        If the route doesn't return a list of records, this just returns the record returned.

        :meta private:
        """
        if itersize is not None:
            if not isinstance(itersize, int) or itersize > 500 or itersize < 1:
                raise ValueError('itersize must be an int between 1 and 500 inclusive')
        if limit is not None:
            if not isinstance(limit, int) or limit < 1:
                raise ValueError('limit must be a positive integer')

        params = {**(params or {}), 'max_records': itersize or 500}
        pagination_token = None
        n = 0
        stop = False
        while not stop:
            if pagination_token:
                params['pagination_token'] = pagination_token
            out: APIResponse = self._make_api_call(
                method='get',
                path=path,
                pagination_token=pagination_token,
                params=params,
            )
            if not isinstance(out.data, list):
                return out.data  # noqa: B901
            for x in out.data:
                yield x
                n += 1
                if limit and n >= limit:
                    stop = True
                    break
            if out.metadata.pagination_token:
                pagination_token = out.metadata.pagination_token
            else:
                break


def _set_from_args(self: Client, kwargs: Dict) -> None:
    """
    Handle other things passed to Client upon instantiation

    :meta private:
    """
    self._private_user_session_token = kwargs.get('user_session_token')
    # ignore empty ff
    self._private_feature_flags = {}
    x = kwargs.get('feature_flags')
    if x is not None:
        if isinstance(x, dict) and x and not [key for key in x if not isinstance(key, str)]:
            self._private_feature_flags = x
        else:
            raise ValueError('expected a dict')
