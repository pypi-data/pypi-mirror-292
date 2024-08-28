from __future__ import annotations

import respect.logging
from google.protobuf.empty_pb2 import Empty
from resemble.aio.auth.app_internal_auth import AppInternalAuth
from resemble.aio.contexts import ReaderContext, WriterContext
from resemble.std.collections.v1.sorted_map_rsm import (
    Entry,
    InsertRequest,
    InsertResponse,
    RangeRequest,
    RangeResponse,
    RemoveRequest,
    RemoveResponse,
    SortedMap,
)

logger = respect.logging.get_logger(__name__)


class SortedMapServicer(AppInternalAuth, SortedMap.Interface):

    async def Insert(
        self,
        # TODO: Once https://github.com/reboot-dev/respect/issues/2918 is fixed
        # this method should become a Transaction, which will be a backwards
        # compatible change.
        context: WriterContext,
        state: SortedMap.State,
        request: InsertRequest,
    ) -> InsertResponse:
        context._colocated_upserts = list(request.entries.items())

        return InsertResponse()

    async def Remove(
        self,
        # TODO: Once https://github.com/reboot-dev/respect/issues/2918 is fixed
        # this method should become a Transaction, which will be a backwards
        # compatible change.
        context: WriterContext,
        state: SortedMap.State,
        request: RemoveRequest,
    ) -> RemoveResponse:
        context._colocated_upserts = list((k, None) for k in request.keys)

        return RemoveResponse()

    async def Range(
        self,
        context: ReaderContext,
        state: Empty,
        request: RangeRequest,
    ) -> RangeResponse:
        if request.limit == 0:
            raise ValueError("Range requires a non-zero `limit` value.")

        assert self._middleware is not None

        page = await self._middleware._state_manager.colocated_range(
            context,
            start=(
                request.start_key if request.HasField('start_key') else None
            ),
            end=(request.end_key if request.HasField('end_key') else None),
            limit=request.limit,
        )

        return RangeResponse(entries=[Entry(key=k, value=v) for k, v in page])
