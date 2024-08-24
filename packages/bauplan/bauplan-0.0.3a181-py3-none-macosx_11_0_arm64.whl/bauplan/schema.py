from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel


class _BauplanData(BaseModel):
    def __str__(self) -> str:
        return self.__repr__()


class APIMetadata(_BauplanData):
    error: str | None
    pagination_token: str | None
    request_id: str | None
    request_ts: int | None
    request_ms: int | None


class APIResponse(_BauplanData):
    data: Any
    metadata: APIMetadata


class RefMetadata(_BauplanData):
    """
    Some metadata about a reference.
    """

    message: str
    committer: str
    authors: list[str]
    commit_time: str
    author_time: str
    parent_commit_hashes: list[str]
    num_commits_ahead: int | None
    num_commits_behind: int | None
    common_ancestor_hash: str | None
    num_total_commits: int

    @classmethod
    def from_dict(cls, metadata: dict | None = None) -> RefMetadata | None:
        """Convert a dictionary of reference metadata to a DataCatalogRefMetadata object."""
        if metadata is None:
            return None
        return cls(
            message=metadata['commitMetaOfHEAD']['message'],
            committer=metadata['commitMetaOfHEAD']['committer'],
            authors=metadata['commitMetaOfHEAD']['authors'],
            commit_time=metadata['commitMetaOfHEAD']['commitTime'],
            author_time=metadata['commitMetaOfHEAD']['authorTime'],
            parent_commit_hashes=metadata['commitMetaOfHEAD']['parentCommitHashes'],
            num_commits_ahead=metadata['numCommitsAhead'],
            num_commits_behind=metadata['numCommitsBehind'],
            common_ancestor_hash=metadata['commonAncestorHash'],
            num_total_commits=metadata['numTotalCommits'],
        )


class Ref(_BauplanData):
    """
    A branch or a tag
    """

    name: str
    hash: str
    metadata: RefMetadata | None = None

    @classmethod
    def from_dict(cls, data: Dict) -> Ref:
        return cls(
            name=data.get('name'),
            hash=data.get('hash'),
            metadata=RefMetadata.from_dict(data.get('metadata')),
        )


class APIBranch(Ref):
    pass


class Entry(_BauplanData):
    name: str
    kind: str


class TableMetadata(_BauplanData):
    type: str
    id: str
    metadata_location: str
    snapshot_id: int
    schema_id: int
    spec_id: int
    sort_order_id: int


class TableField(_BauplanData):
    id: int
    name: str
    required: bool
    type: str


class Table(Entry):
    pass


class TableWithMetadata(Entry):
    id: str
    name: str
    records: int | None
    size: int | None
    last_updated_ms: int
    fields: List[TableField]
    snapshots: int | None
    raw: Dict | None
