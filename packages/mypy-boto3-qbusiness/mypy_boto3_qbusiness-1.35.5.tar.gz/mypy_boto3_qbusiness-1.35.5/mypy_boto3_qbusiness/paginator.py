"""
Type annotations for qbusiness service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_qbusiness.client import QBusinessClient
    from mypy_boto3_qbusiness.paginator import (
        GetChatControlsConfigurationPaginator,
        ListApplicationsPaginator,
        ListConversationsPaginator,
        ListDataSourceSyncJobsPaginator,
        ListDataSourcesPaginator,
        ListDocumentsPaginator,
        ListGroupsPaginator,
        ListIndicesPaginator,
        ListMessagesPaginator,
        ListPluginsPaginator,
        ListRetrieversPaginator,
        ListWebExperiencesPaginator,
    )

    session = Session()
    client: QBusinessClient = session.client("qbusiness")

    get_chat_controls_configuration_paginator: GetChatControlsConfigurationPaginator = client.get_paginator("get_chat_controls_configuration")
    list_applications_paginator: ListApplicationsPaginator = client.get_paginator("list_applications")
    list_conversations_paginator: ListConversationsPaginator = client.get_paginator("list_conversations")
    list_data_source_sync_jobs_paginator: ListDataSourceSyncJobsPaginator = client.get_paginator("list_data_source_sync_jobs")
    list_data_sources_paginator: ListDataSourcesPaginator = client.get_paginator("list_data_sources")
    list_documents_paginator: ListDocumentsPaginator = client.get_paginator("list_documents")
    list_groups_paginator: ListGroupsPaginator = client.get_paginator("list_groups")
    list_indices_paginator: ListIndicesPaginator = client.get_paginator("list_indices")
    list_messages_paginator: ListMessagesPaginator = client.get_paginator("list_messages")
    list_plugins_paginator: ListPluginsPaginator = client.get_paginator("list_plugins")
    list_retrievers_paginator: ListRetrieversPaginator = client.get_paginator("list_retrievers")
    list_web_experiences_paginator: ListWebExperiencesPaginator = client.get_paginator("list_web_experiences")
    ```
"""

from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator, Paginator

from .literals import DataSourceSyncJobStatusType
from .type_defs import (
    GetChatControlsConfigurationResponseTypeDef,
    ListApplicationsResponseTypeDef,
    ListConversationsResponseTypeDef,
    ListDataSourcesResponseTypeDef,
    ListDataSourceSyncJobsResponseTypeDef,
    ListDocumentsResponseTypeDef,
    ListGroupsResponseTypeDef,
    ListIndicesResponseTypeDef,
    ListMessagesResponseTypeDef,
    ListPluginsResponseTypeDef,
    ListRetrieversResponseTypeDef,
    ListWebExperiencesResponseTypeDef,
    PaginatorConfigTypeDef,
    TimestampTypeDef,
)

__all__ = (
    "GetChatControlsConfigurationPaginator",
    "ListApplicationsPaginator",
    "ListConversationsPaginator",
    "ListDataSourceSyncJobsPaginator",
    "ListDataSourcesPaginator",
    "ListDocumentsPaginator",
    "ListGroupsPaginator",
    "ListIndicesPaginator",
    "ListMessagesPaginator",
    "ListPluginsPaginator",
    "ListRetrieversPaginator",
    "ListWebExperiencesPaginator",
)

_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class GetChatControlsConfigurationPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.GetChatControlsConfiguration)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#getchatcontrolsconfigurationpaginator)
    """

    def paginate(
        self, *, applicationId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetChatControlsConfigurationResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.GetChatControlsConfiguration.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#getchatcontrolsconfigurationpaginator)
        """


class ListApplicationsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListApplications)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listapplicationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListApplicationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListApplications.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listapplicationspaginator)
        """


class ListConversationsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListConversations)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listconversationspaginator)
    """

    def paginate(
        self,
        *,
        applicationId: str,
        userId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListConversationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListConversations.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listconversationspaginator)
        """


class ListDataSourceSyncJobsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListDataSourceSyncJobs)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listdatasourcesyncjobspaginator)
    """

    def paginate(
        self,
        *,
        dataSourceId: str,
        applicationId: str,
        indexId: str,
        startTime: TimestampTypeDef = ...,
        endTime: TimestampTypeDef = ...,
        statusFilter: DataSourceSyncJobStatusType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListDataSourceSyncJobsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListDataSourceSyncJobs.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listdatasourcesyncjobspaginator)
        """


class ListDataSourcesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListDataSources)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listdatasourcespaginator)
    """

    def paginate(
        self, *, applicationId: str, indexId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListDataSourcesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListDataSources.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listdatasourcespaginator)
        """


class ListDocumentsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListDocuments)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listdocumentspaginator)
    """

    def paginate(
        self,
        *,
        applicationId: str,
        indexId: str,
        dataSourceIds: Sequence[str] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListDocumentsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListDocuments.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listdocumentspaginator)
        """


class ListGroupsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListGroups)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listgroupspaginator)
    """

    def paginate(
        self,
        *,
        applicationId: str,
        indexId: str,
        updatedEarlierThan: TimestampTypeDef,
        dataSourceId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListGroupsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListGroups.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listgroupspaginator)
        """


class ListIndicesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListIndices)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listindicespaginator)
    """

    def paginate(
        self, *, applicationId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListIndicesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListIndices.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listindicespaginator)
        """


class ListMessagesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListMessages)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listmessagespaginator)
    """

    def paginate(
        self,
        *,
        conversationId: str,
        applicationId: str,
        userId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListMessagesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListMessages.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listmessagespaginator)
        """


class ListPluginsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListPlugins)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listpluginspaginator)
    """

    def paginate(
        self, *, applicationId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListPluginsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListPlugins.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listpluginspaginator)
        """


class ListRetrieversPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListRetrievers)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listretrieverspaginator)
    """

    def paginate(
        self, *, applicationId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListRetrieversResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListRetrievers.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listretrieverspaginator)
        """


class ListWebExperiencesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListWebExperiences)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listwebexperiencespaginator)
    """

    def paginate(
        self, *, applicationId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListWebExperiencesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qbusiness.html#QBusiness.Paginator.ListWebExperiences.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_qbusiness/paginators/#listwebexperiencespaginator)
        """
