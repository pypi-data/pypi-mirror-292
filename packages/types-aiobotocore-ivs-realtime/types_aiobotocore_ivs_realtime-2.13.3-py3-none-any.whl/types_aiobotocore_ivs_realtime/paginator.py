"""
Type annotations for ivs-realtime service client paginators.

[Open documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/paginators/)

Usage::

    ```python
    from aiobotocore.session import get_session

    from types_aiobotocore_ivs_realtime.client import IvsrealtimeClient
    from types_aiobotocore_ivs_realtime.paginator import (
        ListPublicKeysPaginator,
    )

    session = get_session()
    with session.create_client("ivs-realtime") as client:
        client: IvsrealtimeClient

        list_public_keys_paginator: ListPublicKeysPaginator = client.get_paginator("list_public_keys")
    ```
"""

from typing import AsyncIterator, Generic, Iterator, TypeVar

from aiobotocore.paginate import AioPaginator
from botocore.paginate import PageIterator

from .type_defs import ListPublicKeysResponseTypeDef, PaginatorConfigTypeDef

__all__ = ("ListPublicKeysPaginator",)

_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListPublicKeysPaginator(AioPaginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Paginator.ListPublicKeys)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/paginators/#listpublickeyspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> AsyncIterator[ListPublicKeysResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivs-realtime.html#Ivsrealtime.Paginator.ListPublicKeys.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivs_realtime/paginators/#listpublickeyspaginator)
        """
