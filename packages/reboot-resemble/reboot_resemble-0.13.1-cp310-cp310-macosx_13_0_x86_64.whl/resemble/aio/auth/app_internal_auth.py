from __future__ import annotations

import resemble.aio.auth.token_verifiers
import respect.logging
from google.protobuf.message import Message
from resemble.aio.auth import Auth, Token, authorizers, token_verifiers
from resemble.aio.contexts import ReaderContext
from resemble.run_environments import on_cloud
from resemble.v1alpha1.errors_pb2 import Ok, PermissionDenied, Unauthenticated
from typing import Optional

logger = respect.logging.get_logger(__name__)

_APP_INTERNAL_API_KEY_VERIFIED = 'APP_INTERNAL_API_KEY_VERIFIED'


class AppInternalAuth:
    """A Servicer mixin which only allows other Servicers in the same app."""

    def __init__(self):
        super().__init__()

        # TODO: We are currently checking for kubernetes as proxy for checking
        # for cloud.
        if on_cloud():
            logger.warning(
                "App-internal traffic identification is not yet supported on the cloud!",
            )

    def token_verifier(
        self,
    ) -> Optional[resemble.aio.auth.token_verifiers.TokenVerifier]:
        return TokenVerifier()

    def authorizer(self) -> Optional[authorizers.Authorizer]:
        return Authorizer()


class TokenVerifier(token_verifiers.TokenVerifier):

    async def verify_token(
        self,
        context: ReaderContext,
        token: str,
    ) -> Optional[Auth]:
        if token == context._app_internal_api_key_secret:
            return Auth(
                # No user ID, the secret _is_ the API key.
                user_id=None,
                bearer_token=Token(
                    raw=token,
                    decoded={_APP_INTERNAL_API_KEY_VERIFIED: True},
                ),
            )
        else:
            return None


class Authorizer(authorizers.Authorizer[Message, Message]):

    def can_authorize(self, method_name: str) -> bool:
        return True

    async def authorize(
        self,
        *,
        method_name: str,
        context: ReaderContext,
        state: Optional[Message] = None,
        request: Optional[Message] = None,
    ) -> authorizers.Authorizer.Decision:
        if context.auth is None:
            return Unauthenticated()
        # We assume the TokenVerifier has run and populated
        # `auth.bearer_token.decoded`.
        assert context.auth.bearer_token is not None
        assert context.auth.bearer_token.decoded is not None
        if _APP_INTERNAL_API_KEY_VERIFIED in context.auth.bearer_token.decoded:
            return Ok()

        return PermissionDenied()
