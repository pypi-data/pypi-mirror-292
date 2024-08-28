import aiofiles
import asyncio
import grpc
import json
from google.protobuf import json_format
from pathlib import Path
from resemble.aio.headers import AUTHORIZATION_HEADER
from resemble.aio.types import ConsensusId
from resemble.v1alpha1.admin import export_import_pb2_grpc
from resemble.v1alpha1.admin.export_import_pb2 import (
    ExportImportItem,
    ExportRequest,
    ListConsensusesRequest,
)
from typing import AsyncIterator


def _with_admin_auth_metadata(token: str) -> tuple[tuple[str, str]]:
    """Syntactic sugar for creating a metadata tuple with a bearer token."""
    assert token and len(token) > 0, "admin token must not be empty"
    return ((AUTHORIZATION_HEADER, f'Bearer {token}'),)


async def _export(
    export_import: export_import_pb2_grpc.ExportImportStub,
    consensus_id: ConsensusId,
    dest_path: Path,
    *,
    admin_token: str,
) -> None:
    while True:
        try:
            async with aiofiles.open(dest_path, 'w') as output:
                async for item in export_import.Export(
                    ExportRequest(consensus_id=consensus_id),
                    metadata=_with_admin_auth_metadata(admin_token),
                ):
                    await output.write(
                        # NOTE: We use `MessageToDict` followed by `json.dumps`
                        # because protobuf's JSON encoding always inserts
                        # newlines, even when `indent=0`.
                        json.dumps(
                            json_format.MessageToDict(
                                item,
                                preserving_proto_field_name=True,
                            )
                        )
                    )
                    await output.write("\n")
            return
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                # We were sent to the incorrect consensus: try again until
                # we get the right one.
                continue
            raise


async def do_export(
    export_import: export_import_pb2_grpc.ExportImportStub,
    dest_directory: Path,
    *,
    admin_token: str,
) -> None:
    """Export one JSON-lines file per consensus to the given directory."""
    dest_directory.mkdir(parents=True, exist_ok=True)

    response = await export_import.ListConsensuses(
        ListConsensusesRequest(),
        metadata=_with_admin_auth_metadata(admin_token),
    )
    # TODO: Throttle the total number of outstanding requests.
    await asyncio.gather(
        *(
            _export(
                export_import,
                consensus_id,
                dest_directory / f"{consensus_id}.json",
                admin_token=admin_token,
            ) for consensus_id in response.consensus_ids
        )
    )


async def _import(
    export_import: export_import_pb2_grpc.ExportImportStub,
    src_path: Path,
    *,
    admin_token: str,
) -> None:

    async def import_stream() -> AsyncIterator[ExportImportItem]:
        async with aiofiles.open(src_path, 'r') as infile:
            async for line in infile:
                yield json_format.Parse(
                    line,
                    ExportImportItem(),
                )

    await export_import.Import(
        import_stream(),
        metadata=_with_admin_auth_metadata(admin_token),
    )


async def do_import(
    export_import: export_import_pb2_grpc.ExportImportStub,
    src_directory: Path,
    *,
    admin_token: str,
) -> None:
    """Import all JSON-lines files in the given directory to the server."""
    # TODO: Throttle the number of requests and/or make a best effort to
    # direct items at the "correct" nodes using a placement client.
    await asyncio.gather(
        *(
            _import(export_import, path, admin_token=admin_token)
            for path in src_directory.iterdir()
        )
    )
