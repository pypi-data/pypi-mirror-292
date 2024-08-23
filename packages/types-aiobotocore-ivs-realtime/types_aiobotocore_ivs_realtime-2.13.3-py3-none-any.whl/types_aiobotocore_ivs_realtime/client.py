"""
Type annotations for ivs-realtime service client.

[Open documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/)

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_ivs_realtime.client import IvsrealtimeClient

    session = get_session()
    async with session.create_client("ivs-realtime") as client:
        client: IvsrealtimeClient
    ```
"""

import sys
from typing import Any, Dict, Mapping, Sequence, Type

from aiobotocore.client import AioBaseClient
from botocore.client import ClientMeta

from .literals import (
    ParticipantRecordingFilterByRecordingStateType,
    ParticipantStateType,
    ParticipantTokenCapabilityType,
)
from .paginator import ListPublicKeysPaginator
from .type_defs import (
    AutoParticipantRecordingConfigurationUnionTypeDef,
    CreateEncoderConfigurationResponseTypeDef,
    CreateParticipantTokenResponseTypeDef,
    CreateStageResponseTypeDef,
    CreateStorageConfigurationResponseTypeDef,
    DestinationConfigurationUnionTypeDef,
    GetCompositionResponseTypeDef,
    GetEncoderConfigurationResponseTypeDef,
    GetParticipantResponseTypeDef,
    GetPublicKeyResponseTypeDef,
    GetStageResponseTypeDef,
    GetStageSessionResponseTypeDef,
    GetStorageConfigurationResponseTypeDef,
    ImportPublicKeyResponseTypeDef,
    LayoutConfigurationTypeDef,
    ListCompositionsResponseTypeDef,
    ListEncoderConfigurationsResponseTypeDef,
    ListParticipantEventsResponseTypeDef,
    ListParticipantsResponseTypeDef,
    ListPublicKeysResponseTypeDef,
    ListStageSessionsResponseTypeDef,
    ListStagesResponseTypeDef,
    ListStorageConfigurationsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ParticipantTokenConfigurationTypeDef,
    S3StorageConfigurationTypeDef,
    StartCompositionResponseTypeDef,
    UpdateStageResponseTypeDef,
    VideoTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = ("IvsrealtimeClient",)


class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    PendingVerification: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class IvsrealtimeClient(AioBaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        IvsrealtimeClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.exceptions)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.can_paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#can_paginate)
        """

    async def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.close)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#close)
        """

    async def create_encoder_configuration(
        self, *, name: str = ..., video: VideoTypeDef = ..., tags: Mapping[str, str] = ...
    ) -> CreateEncoderConfigurationResponseTypeDef:
        """
        Creates an EncoderConfiguration object.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.create_encoder_configuration)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#create_encoder_configuration)
        """

    async def create_participant_token(
        self,
        *,
        stageArn: str,
        duration: int = ...,
        userId: str = ...,
        attributes: Mapping[str, str] = ...,
        capabilities: Sequence[ParticipantTokenCapabilityType] = ...,
    ) -> CreateParticipantTokenResponseTypeDef:
        """
        Creates an additional token for a specified stage.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.create_participant_token)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#create_participant_token)
        """

    async def create_stage(
        self,
        *,
        name: str = ...,
        participantTokenConfigurations: Sequence[ParticipantTokenConfigurationTypeDef] = ...,
        tags: Mapping[str, str] = ...,
        autoParticipantRecordingConfiguration: AutoParticipantRecordingConfigurationUnionTypeDef = ...,
    ) -> CreateStageResponseTypeDef:
        """
        Creates a new stage (and optionally participant tokens).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.create_stage)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#create_stage)
        """

    async def create_storage_configuration(
        self, *, s3: S3StorageConfigurationTypeDef, name: str = ..., tags: Mapping[str, str] = ...
    ) -> CreateStorageConfigurationResponseTypeDef:
        """
        Creates a new storage configuration, used to enable recording to Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.create_storage_configuration)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#create_storage_configuration)
        """

    async def delete_encoder_configuration(self, *, arn: str) -> Dict[str, Any]:
        """
        Deletes an EncoderConfiguration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.delete_encoder_configuration)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#delete_encoder_configuration)
        """

    async def delete_public_key(self, *, arn: str) -> Dict[str, Any]:
        """
        Deletes the specified public key used to sign stage participant tokens.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.delete_public_key)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#delete_public_key)
        """

    async def delete_stage(self, *, arn: str) -> Dict[str, Any]:
        """
        Shuts down and deletes the specified stage (disconnecting all participants).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.delete_stage)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#delete_stage)
        """

    async def delete_storage_configuration(self, *, arn: str) -> Dict[str, Any]:
        """
        Deletes the storage configuration for the specified ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.delete_storage_configuration)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#delete_storage_configuration)
        """

    async def disconnect_participant(
        self, *, stageArn: str, participantId: str, reason: str = ...
    ) -> Dict[str, Any]:
        """
        Disconnects a specified participant and revokes the participant permanently
        from a specified
        stage.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.disconnect_participant)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#disconnect_participant)
        """

    async def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.generate_presigned_url)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#generate_presigned_url)
        """

    async def get_composition(self, *, arn: str) -> GetCompositionResponseTypeDef:
        """
        Get information about the specified Composition resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.get_composition)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#get_composition)
        """

    async def get_encoder_configuration(
        self, *, arn: str
    ) -> GetEncoderConfigurationResponseTypeDef:
        """
        Gets information about the specified EncoderConfiguration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.get_encoder_configuration)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#get_encoder_configuration)
        """

    async def get_participant(
        self, *, stageArn: str, sessionId: str, participantId: str
    ) -> GetParticipantResponseTypeDef:
        """
        Gets information about the specified participant token.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.get_participant)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#get_participant)
        """

    async def get_public_key(self, *, arn: str) -> GetPublicKeyResponseTypeDef:
        """
        Gets information for the specified public key.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.get_public_key)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#get_public_key)
        """

    async def get_stage(self, *, arn: str) -> GetStageResponseTypeDef:
        """
        Gets information for the specified stage.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.get_stage)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#get_stage)
        """

    async def get_stage_session(
        self, *, stageArn: str, sessionId: str
    ) -> GetStageSessionResponseTypeDef:
        """
        Gets information for the specified stage session.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.get_stage_session)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#get_stage_session)
        """

    async def get_storage_configuration(
        self, *, arn: str
    ) -> GetStorageConfigurationResponseTypeDef:
        """
        Gets the storage configuration for the specified ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.get_storage_configuration)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#get_storage_configuration)
        """

    async def import_public_key(
        self, *, publicKeyMaterial: str, name: str = ..., tags: Mapping[str, str] = ...
    ) -> ImportPublicKeyResponseTypeDef:
        """
        Import a public key to be used for signing stage participant tokens.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.import_public_key)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#import_public_key)
        """

    async def list_compositions(
        self,
        *,
        filterByStageArn: str = ...,
        filterByEncoderConfigurationArn: str = ...,
        nextToken: str = ...,
        maxResults: int = ...,
    ) -> ListCompositionsResponseTypeDef:
        """
        Gets summary information about all Compositions in your account, in the AWS
        region where the API request is
        processed.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_compositions)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_compositions)
        """

    async def list_encoder_configurations(
        self, *, nextToken: str = ..., maxResults: int = ...
    ) -> ListEncoderConfigurationsResponseTypeDef:
        """
        Gets summary information about all EncoderConfigurations in your account, in
        the AWS region where the API request is
        processed.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_encoder_configurations)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_encoder_configurations)
        """

    async def list_participant_events(
        self,
        *,
        stageArn: str,
        sessionId: str,
        participantId: str,
        nextToken: str = ...,
        maxResults: int = ...,
    ) -> ListParticipantEventsResponseTypeDef:
        """
        Lists events for a specified participant that occurred during a specified stage
        session.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_participant_events)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_participant_events)
        """

    async def list_participants(
        self,
        *,
        stageArn: str,
        sessionId: str,
        filterByUserId: str = ...,
        filterByPublished: bool = ...,
        filterByState: ParticipantStateType = ...,
        nextToken: str = ...,
        maxResults: int = ...,
        filterByRecordingState: ParticipantRecordingFilterByRecordingStateType = ...,
    ) -> ListParticipantsResponseTypeDef:
        """
        Lists all participants in a specified stage session.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_participants)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_participants)
        """

    async def list_public_keys(
        self, *, nextToken: str = ..., maxResults: int = ...
    ) -> ListPublicKeysResponseTypeDef:
        """
        Gets summary information about all public keys in your account, in the AWS
        region where the API request is
        processed.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_public_keys)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_public_keys)
        """

    async def list_stage_sessions(
        self, *, stageArn: str, nextToken: str = ..., maxResults: int = ...
    ) -> ListStageSessionsResponseTypeDef:
        """
        Gets all sessions for a specified stage.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_stage_sessions)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_stage_sessions)
        """

    async def list_stages(
        self, *, nextToken: str = ..., maxResults: int = ...
    ) -> ListStagesResponseTypeDef:
        """
        Gets summary information about all stages in your account, in the AWS region
        where the API request is
        processed.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_stages)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_stages)
        """

    async def list_storage_configurations(
        self, *, nextToken: str = ..., maxResults: int = ...
    ) -> ListStorageConfigurationsResponseTypeDef:
        """
        Gets summary information about all storage configurations in your account, in
        the AWS region where the API request is
        processed.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_storage_configurations)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_storage_configurations)
        """

    async def list_tags_for_resource(
        self, *, resourceArn: str
    ) -> ListTagsForResourceResponseTypeDef:
        """
        Gets information about AWS tags for the specified ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.list_tags_for_resource)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#list_tags_for_resource)
        """

    async def start_composition(
        self,
        *,
        stageArn: str,
        destinations: Sequence[DestinationConfigurationUnionTypeDef],
        idempotencyToken: str = ...,
        layout: LayoutConfigurationTypeDef = ...,
        tags: Mapping[str, str] = ...,
    ) -> StartCompositionResponseTypeDef:
        """
        Starts a Composition from a stage based on the configuration provided in the
        request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.start_composition)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#start_composition)
        """

    async def stop_composition(self, *, arn: str) -> Dict[str, Any]:
        """
        Stops and deletes a Composition resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.stop_composition)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#stop_composition)
        """

    async def tag_resource(self, *, resourceArn: str, tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        Adds or updates tags for the AWS resource with the specified ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.tag_resource)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#tag_resource)
        """

    async def untag_resource(self, *, resourceArn: str, tagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes tags from the resource with the specified ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.untag_resource)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#untag_resource)
        """

    async def update_stage(
        self,
        *,
        arn: str,
        name: str = ...,
        autoParticipantRecordingConfiguration: AutoParticipantRecordingConfigurationUnionTypeDef = ...,
    ) -> UpdateStageResponseTypeDef:
        """
        Updates a stage's configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.update_stage)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#update_stage)
        """

    def get_paginator(self, operation_name: Literal["list_public_keys"]) -> ListPublicKeysPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client.get_paginator)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/#get_paginator)
        """

    async def __aenter__(self) -> "IvsrealtimeClient":
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/)
        """

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/client/)
        """
