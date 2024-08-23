"""
Type annotations for application-signals service client.

[Open documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/)

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_application_signals.client import CloudWatchApplicationSignalsClient

    session = get_session()
    async with session.create_client("application-signals") as client:
        client: CloudWatchApplicationSignalsClient
    ```
"""

import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from aiobotocore.client import AioBaseClient
from botocore.client import ClientMeta

from .paginator import (
    ListServiceDependenciesPaginator,
    ListServiceDependentsPaginator,
    ListServiceLevelObjectivesPaginator,
    ListServiceOperationsPaginator,
    ListServicesPaginator,
)
from .type_defs import (
    BatchGetServiceLevelObjectiveBudgetReportOutputTypeDef,
    CreateServiceLevelObjectiveOutputTypeDef,
    GetServiceLevelObjectiveOutputTypeDef,
    GetServiceOutputTypeDef,
    GoalUnionTypeDef,
    ListServiceDependenciesOutputTypeDef,
    ListServiceDependentsOutputTypeDef,
    ListServiceLevelObjectivesOutputTypeDef,
    ListServiceOperationsOutputTypeDef,
    ListServicesOutputTypeDef,
    ListTagsForResourceResponseTypeDef,
    ServiceLevelIndicatorConfigTypeDef,
    TagTypeDef,
    TimestampTypeDef,
    UpdateServiceLevelObjectiveOutputTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = ("CloudWatchApplicationSignalsClient",)


class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class CloudWatchApplicationSignalsClient(AioBaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        CloudWatchApplicationSignalsClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.exceptions)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#exceptions)
        """

    async def batch_get_service_level_objective_budget_report(
        self, *, Timestamp: TimestampTypeDef, SloIds: Sequence[str]
    ) -> BatchGetServiceLevelObjectiveBudgetReportOutputTypeDef:
        """
        Use this operation to retrieve one or more *service level objective (SLO)
        budget
        reports*.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.batch_get_service_level_objective_budget_report)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#batch_get_service_level_objective_budget_report)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.can_paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#can_paginate)
        """

    async def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.close)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#close)
        """

    async def create_service_level_objective(
        self,
        *,
        Name: str,
        SliConfig: ServiceLevelIndicatorConfigTypeDef,
        Description: str = ...,
        Goal: GoalUnionTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...,
    ) -> CreateServiceLevelObjectiveOutputTypeDef:
        """
        Creates a service level objective (SLO), which can help you ensure that your
        critical business operations are meeting customer
        expectations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.create_service_level_objective)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#create_service_level_objective)
        """

    async def delete_service_level_objective(self, *, Id: str) -> Dict[str, Any]:
        """
        Deletes the specified service level objective.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.delete_service_level_objective)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#delete_service_level_objective)
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

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.generate_presigned_url)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#generate_presigned_url)
        """

    async def get_service(
        self,
        *,
        StartTime: TimestampTypeDef,
        EndTime: TimestampTypeDef,
        KeyAttributes: Mapping[str, str],
    ) -> GetServiceOutputTypeDef:
        """
        Returns information about a service discovered by Application Signals.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.get_service)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#get_service)
        """

    async def get_service_level_objective(
        self, *, Id: str
    ) -> GetServiceLevelObjectiveOutputTypeDef:
        """
        Returns information about one SLO created in the account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.get_service_level_objective)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#get_service_level_objective)
        """

    async def list_service_dependencies(
        self,
        *,
        StartTime: TimestampTypeDef,
        EndTime: TimestampTypeDef,
        KeyAttributes: Mapping[str, str],
        MaxResults: int = ...,
        NextToken: str = ...,
    ) -> ListServiceDependenciesOutputTypeDef:
        """
        Returns a list of service dependencies of the service that you specify.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.list_service_dependencies)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#list_service_dependencies)
        """

    async def list_service_dependents(
        self,
        *,
        StartTime: TimestampTypeDef,
        EndTime: TimestampTypeDef,
        KeyAttributes: Mapping[str, str],
        MaxResults: int = ...,
        NextToken: str = ...,
    ) -> ListServiceDependentsOutputTypeDef:
        """
        Returns the list of dependents that invoked the specified service during the
        provided time
        range.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.list_service_dependents)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#list_service_dependents)
        """

    async def list_service_level_objectives(
        self,
        *,
        KeyAttributes: Mapping[str, str] = ...,
        OperationName: str = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
    ) -> ListServiceLevelObjectivesOutputTypeDef:
        """
        Returns a list of SLOs created in this account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.list_service_level_objectives)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#list_service_level_objectives)
        """

    async def list_service_operations(
        self,
        *,
        StartTime: TimestampTypeDef,
        EndTime: TimestampTypeDef,
        KeyAttributes: Mapping[str, str],
        MaxResults: int = ...,
        NextToken: str = ...,
    ) -> ListServiceOperationsOutputTypeDef:
        """
        Returns a list of the *operations* of this service that have been discovered by
        Application
        Signals.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.list_service_operations)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#list_service_operations)
        """

    async def list_services(
        self,
        *,
        StartTime: TimestampTypeDef,
        EndTime: TimestampTypeDef,
        MaxResults: int = ...,
        NextToken: str = ...,
    ) -> ListServicesOutputTypeDef:
        """
        Returns a list of services that have been discovered by Application Signals.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.list_services)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#list_services)
        """

    async def list_tags_for_resource(
        self, *, ResourceArn: str
    ) -> ListTagsForResourceResponseTypeDef:
        """
        Displays the tags associated with a CloudWatch resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.list_tags_for_resource)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#list_tags_for_resource)
        """

    async def start_discovery(self) -> Dict[str, Any]:
        """
        Enables this Amazon Web Services account to be able to use CloudWatch
        Application Signals by creating the
        *AWSServiceRoleForCloudWatchApplicationSignals* service-linked
        role.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.start_discovery)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#start_discovery)
        """

    async def tag_resource(self, *, ResourceArn: str, Tags: Sequence[TagTypeDef]) -> Dict[str, Any]:
        """
        Assigns one or more tags (key-value pairs) to the specified CloudWatch
        resource, such as a service level
        objective.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.tag_resource)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#tag_resource)
        """

    async def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes one or more tags from the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.untag_resource)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#untag_resource)
        """

    async def update_service_level_objective(
        self,
        *,
        Id: str,
        Description: str = ...,
        SliConfig: ServiceLevelIndicatorConfigTypeDef = ...,
        Goal: GoalUnionTypeDef = ...,
    ) -> UpdateServiceLevelObjectiveOutputTypeDef:
        """
        Updates an existing service level objective (SLO).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.update_service_level_objective)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#update_service_level_objective)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_service_dependencies"]
    ) -> ListServiceDependenciesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.get_paginator)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_service_dependents"]
    ) -> ListServiceDependentsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.get_paginator)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_service_level_objectives"]
    ) -> ListServiceLevelObjectivesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.get_paginator)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_service_operations"]
    ) -> ListServiceOperationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.get_paginator)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_services"]) -> ListServicesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client.get_paginator)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/#get_paginator)
        """

    async def __aenter__(self) -> "CloudWatchApplicationSignalsClient":
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/)
        """

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/application-signals.html#CloudWatchApplicationSignals.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_application_signals/client/)
        """
