"""
Type annotations for cost-optimization-hub service client paginators.

[Open documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cost_optimization_hub/paginators/)

Usage::

    ```python
    from aiobotocore.session import get_session

    from types_aiobotocore_cost_optimization_hub.client import CostOptimizationHubClient
    from types_aiobotocore_cost_optimization_hub.paginator import (
        ListEnrollmentStatusesPaginator,
        ListRecommendationSummariesPaginator,
        ListRecommendationsPaginator,
    )

    session = get_session()
    with session.create_client("cost-optimization-hub") as client:
        client: CostOptimizationHubClient

        list_enrollment_statuses_paginator: ListEnrollmentStatusesPaginator = client.get_paginator("list_enrollment_statuses")
        list_recommendation_summaries_paginator: ListRecommendationSummariesPaginator = client.get_paginator("list_recommendation_summaries")
        list_recommendations_paginator: ListRecommendationsPaginator = client.get_paginator("list_recommendations")
    ```
"""

import sys
from typing import AsyncIterator, Generic, Iterator, Sequence, TypeVar

from aiobotocore.paginate import AioPaginator
from botocore.paginate import PageIterator

from .type_defs import (
    FilterTypeDef,
    ListEnrollmentStatusesResponseTypeDef,
    ListRecommendationsResponseTypeDef,
    ListRecommendationSummariesResponseTypeDef,
    OrderByTypeDef,
    PaginatorConfigTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = (
    "ListEnrollmentStatusesPaginator",
    "ListRecommendationSummariesPaginator",
    "ListRecommendationsPaginator",
)

_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListEnrollmentStatusesPaginator(AioPaginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListEnrollmentStatuses)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cost_optimization_hub/paginators/#listenrollmentstatusespaginator)
    """

    def paginate(
        self,
        *,
        includeOrganizationInfo: bool = ...,
        accountId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> AsyncIterator[ListEnrollmentStatusesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListEnrollmentStatuses.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cost_optimization_hub/paginators/#listenrollmentstatusespaginator)
        """


class ListRecommendationSummariesPaginator(AioPaginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListRecommendationSummaries)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cost_optimization_hub/paginators/#listrecommendationsummariespaginator)
    """

    def paginate(
        self,
        *,
        groupBy: str,
        filter: FilterTypeDef = ...,
        metrics: Sequence[Literal["SavingsPercentage"]] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> AsyncIterator[ListRecommendationSummariesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListRecommendationSummaries.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cost_optimization_hub/paginators/#listrecommendationsummariespaginator)
        """


class ListRecommendationsPaginator(AioPaginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListRecommendations)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cost_optimization_hub/paginators/#listrecommendationspaginator)
    """

    def paginate(
        self,
        *,
        filter: FilterTypeDef = ...,
        orderBy: OrderByTypeDef = ...,
        includeAllRecommendations: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> AsyncIterator[ListRecommendationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListRecommendations.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cost_optimization_hub/paginators/#listrecommendationspaginator)
        """
