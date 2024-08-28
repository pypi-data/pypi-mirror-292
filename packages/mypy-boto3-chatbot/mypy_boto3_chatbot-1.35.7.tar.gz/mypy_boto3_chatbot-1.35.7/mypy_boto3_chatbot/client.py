"""
Type annotations for chatbot service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_chatbot.client import ChatbotClient

    session = Session()
    client: ChatbotClient = session.client("chatbot")
    ```
"""

import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .paginator import (
    DescribeChimeWebhookConfigurationsPaginator,
    DescribeSlackChannelConfigurationsPaginator,
    DescribeSlackUserIdentitiesPaginator,
    DescribeSlackWorkspacesPaginator,
    ListMicrosoftTeamsChannelConfigurationsPaginator,
    ListMicrosoftTeamsConfiguredTeamsPaginator,
    ListMicrosoftTeamsUserIdentitiesPaginator,
)
from .type_defs import (
    CreateChimeWebhookConfigurationResultTypeDef,
    CreateSlackChannelConfigurationResultTypeDef,
    CreateTeamsChannelConfigurationResultTypeDef,
    DescribeChimeWebhookConfigurationsResultTypeDef,
    DescribeSlackChannelConfigurationsResultTypeDef,
    DescribeSlackUserIdentitiesResultTypeDef,
    DescribeSlackWorkspacesResultTypeDef,
    GetAccountPreferencesResultTypeDef,
    GetTeamsChannelConfigurationResultTypeDef,
    ListMicrosoftTeamsConfiguredTeamsResultTypeDef,
    ListMicrosoftTeamsUserIdentitiesResultTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListTeamsChannelConfigurationsResultTypeDef,
    TagTypeDef,
    UpdateAccountPreferencesResultTypeDef,
    UpdateChimeWebhookConfigurationResultTypeDef,
    UpdateSlackChannelConfigurationResultTypeDef,
    UpdateTeamsChannelConfigurationResultTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = ("ChatbotClient",)


class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    CreateChimeWebhookConfigurationException: Type[BotocoreClientError]
    CreateSlackChannelConfigurationException: Type[BotocoreClientError]
    CreateTeamsChannelConfigurationException: Type[BotocoreClientError]
    DeleteChimeWebhookConfigurationException: Type[BotocoreClientError]
    DeleteMicrosoftTeamsUserIdentityException: Type[BotocoreClientError]
    DeleteSlackChannelConfigurationException: Type[BotocoreClientError]
    DeleteSlackUserIdentityException: Type[BotocoreClientError]
    DeleteSlackWorkspaceAuthorizationFault: Type[BotocoreClientError]
    DeleteTeamsChannelConfigurationException: Type[BotocoreClientError]
    DeleteTeamsConfiguredTeamException: Type[BotocoreClientError]
    DescribeChimeWebhookConfigurationsException: Type[BotocoreClientError]
    DescribeSlackChannelConfigurationsException: Type[BotocoreClientError]
    DescribeSlackUserIdentitiesException: Type[BotocoreClientError]
    DescribeSlackWorkspacesException: Type[BotocoreClientError]
    GetAccountPreferencesException: Type[BotocoreClientError]
    GetTeamsChannelConfigurationException: Type[BotocoreClientError]
    InternalServiceError: Type[BotocoreClientError]
    InvalidParameterException: Type[BotocoreClientError]
    InvalidRequestException: Type[BotocoreClientError]
    LimitExceededException: Type[BotocoreClientError]
    ListMicrosoftTeamsConfiguredTeamsException: Type[BotocoreClientError]
    ListMicrosoftTeamsUserIdentitiesException: Type[BotocoreClientError]
    ListTeamsChannelConfigurationsException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceUnavailableException: Type[BotocoreClientError]
    TooManyTagsException: Type[BotocoreClientError]
    UpdateAccountPreferencesException: Type[BotocoreClientError]
    UpdateChimeWebhookConfigurationException: Type[BotocoreClientError]
    UpdateSlackChannelConfigurationException: Type[BotocoreClientError]
    UpdateTeamsChannelConfigurationException: Type[BotocoreClientError]


class ChatbotClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        ChatbotClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#can_paginate)
        """

    def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.close)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#close)
        """

    def create_chime_webhook_configuration(
        self,
        *,
        WebhookDescription: str,
        WebhookUrl: str,
        SnsTopicArns: Sequence[str],
        IamRoleArn: str,
        ConfigurationName: str,
        LoggingLevel: str = ...,
        Tags: Sequence[TagTypeDef] = ...,
    ) -> CreateChimeWebhookConfigurationResultTypeDef:
        """
        Creates an AWS Chatbot configuration for Amazon Chime.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.create_chime_webhook_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#create_chime_webhook_configuration)
        """

    def create_microsoft_teams_channel_configuration(
        self,
        *,
        ChannelId: str,
        TeamId: str,
        TenantId: str,
        IamRoleArn: str,
        ConfigurationName: str,
        ChannelName: str = ...,
        TeamName: str = ...,
        SnsTopicArns: Sequence[str] = ...,
        LoggingLevel: str = ...,
        GuardrailPolicyArns: Sequence[str] = ...,
        UserAuthorizationRequired: bool = ...,
        Tags: Sequence[TagTypeDef] = ...,
    ) -> CreateTeamsChannelConfigurationResultTypeDef:
        """
        Creates an AWS Chatbot configuration for Microsoft Teams.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.create_microsoft_teams_channel_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#create_microsoft_teams_channel_configuration)
        """

    def create_slack_channel_configuration(
        self,
        *,
        SlackTeamId: str,
        SlackChannelId: str,
        IamRoleArn: str,
        ConfigurationName: str,
        SlackChannelName: str = ...,
        SnsTopicArns: Sequence[str] = ...,
        LoggingLevel: str = ...,
        GuardrailPolicyArns: Sequence[str] = ...,
        UserAuthorizationRequired: bool = ...,
        Tags: Sequence[TagTypeDef] = ...,
    ) -> CreateSlackChannelConfigurationResultTypeDef:
        """
        Creates an AWS Chatbot confugration for Slack.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.create_slack_channel_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#create_slack_channel_configuration)
        """

    def delete_chime_webhook_configuration(self, *, ChatConfigurationArn: str) -> Dict[str, Any]:
        """
        Deletes a Amazon Chime webhook configuration for AWS Chatbot.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.delete_chime_webhook_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#delete_chime_webhook_configuration)
        """

    def delete_microsoft_teams_channel_configuration(
        self, *, ChatConfigurationArn: str
    ) -> Dict[str, Any]:
        """
        Deletes a Microsoft Teams channel configuration for AWS Chatbot See also: [AWS
        API
        Documentation](https://docs.aws.amazon.com/goto/WebAPI/chatbot-2017-10-11/DeleteMicrosoftTeamsChannelConfiguration).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.delete_microsoft_teams_channel_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#delete_microsoft_teams_channel_configuration)
        """

    def delete_microsoft_teams_configured_team(self, *, TeamId: str) -> Dict[str, Any]:
        """
        Deletes the Microsoft Teams team authorization allowing for channels to be
        configured in that Microsoft Teams
        team.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.delete_microsoft_teams_configured_team)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#delete_microsoft_teams_configured_team)
        """

    def delete_microsoft_teams_user_identity(
        self, *, ChatConfigurationArn: str, UserId: str
    ) -> Dict[str, Any]:
        """
        Identifes a user level permission for a channel configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.delete_microsoft_teams_user_identity)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#delete_microsoft_teams_user_identity)
        """

    def delete_slack_channel_configuration(self, *, ChatConfigurationArn: str) -> Dict[str, Any]:
        """
        Deletes a Slack channel configuration for AWS Chatbot See also: [AWS API
        Documentation](https://docs.aws.amazon.com/goto/WebAPI/chatbot-2017-10-11/DeleteSlackChannelConfiguration).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.delete_slack_channel_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#delete_slack_channel_configuration)
        """

    def delete_slack_user_identity(
        self, *, ChatConfigurationArn: str, SlackTeamId: str, SlackUserId: str
    ) -> Dict[str, Any]:
        """
        Deletes a user level permission for a Slack channel configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.delete_slack_user_identity)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#delete_slack_user_identity)
        """

    def delete_slack_workspace_authorization(self, *, SlackTeamId: str) -> Dict[str, Any]:
        """
        Deletes the Slack workspace authorization that allows channels to be configured
        in that
        workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.delete_slack_workspace_authorization)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#delete_slack_workspace_authorization)
        """

    def describe_chime_webhook_configurations(
        self, *, MaxResults: int = ..., NextToken: str = ..., ChatConfigurationArn: str = ...
    ) -> DescribeChimeWebhookConfigurationsResultTypeDef:
        """
        Lists Amazon Chime webhook configurations optionally filtered by
        ChatConfigurationArn See also: [AWS API
        Documentation](https://docs.aws.amazon.com/goto/WebAPI/chatbot-2017-10-11/DescribeChimeWebhookConfigurations).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.describe_chime_webhook_configurations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#describe_chime_webhook_configurations)
        """

    def describe_slack_channel_configurations(
        self, *, MaxResults: int = ..., NextToken: str = ..., ChatConfigurationArn: str = ...
    ) -> DescribeSlackChannelConfigurationsResultTypeDef:
        """
        Lists Slack channel configurations optionally filtered by ChatConfigurationArn
        See also: [AWS API
        Documentation](https://docs.aws.amazon.com/goto/WebAPI/chatbot-2017-10-11/DescribeSlackChannelConfigurations).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.describe_slack_channel_configurations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#describe_slack_channel_configurations)
        """

    def describe_slack_user_identities(
        self, *, ChatConfigurationArn: str = ..., NextToken: str = ..., MaxResults: int = ...
    ) -> DescribeSlackUserIdentitiesResultTypeDef:
        """
        Lists all Slack user identities with a mapped role.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.describe_slack_user_identities)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#describe_slack_user_identities)
        """

    def describe_slack_workspaces(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> DescribeSlackWorkspacesResultTypeDef:
        """
        List all authorized Slack workspaces connected to the AWS Account onboarded
        with AWS
        Chatbot.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.describe_slack_workspaces)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#describe_slack_workspaces)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#generate_presigned_url)
        """

    def get_account_preferences(self) -> GetAccountPreferencesResultTypeDef:
        """
        Returns AWS Chatbot account preferences.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_account_preferences)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_account_preferences)
        """

    def get_microsoft_teams_channel_configuration(
        self, *, ChatConfigurationArn: str
    ) -> GetTeamsChannelConfigurationResultTypeDef:
        """
        Returns a Microsoft Teams channel configuration in an AWS account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_microsoft_teams_channel_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_microsoft_teams_channel_configuration)
        """

    def list_microsoft_teams_channel_configurations(
        self, *, MaxResults: int = ..., NextToken: str = ..., TeamId: str = ...
    ) -> ListTeamsChannelConfigurationsResultTypeDef:
        """
        Lists all AWS Chatbot Microsoft Teams channel configurations in an AWS account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.list_microsoft_teams_channel_configurations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#list_microsoft_teams_channel_configurations)
        """

    def list_microsoft_teams_configured_teams(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListMicrosoftTeamsConfiguredTeamsResultTypeDef:
        """
        Lists all authorized Microsoft Teams for an AWS Account See also: [AWS API
        Documentation](https://docs.aws.amazon.com/goto/WebAPI/chatbot-2017-10-11/ListMicrosoftTeamsConfiguredTeams).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.list_microsoft_teams_configured_teams)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#list_microsoft_teams_configured_teams)
        """

    def list_microsoft_teams_user_identities(
        self, *, ChatConfigurationArn: str = ..., NextToken: str = ..., MaxResults: int = ...
    ) -> ListMicrosoftTeamsUserIdentitiesResultTypeDef:
        """
        A list all Microsoft Teams user identities with a mapped role.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.list_microsoft_teams_user_identities)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#list_microsoft_teams_user_identities)
        """

    def list_tags_for_resource(self, *, ResourceARN: str) -> ListTagsForResourceResponseTypeDef:
        """
        Lists all of the tags associated with the Amazon Resource Name (ARN) that you
        specify.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#list_tags_for_resource)
        """

    def tag_resource(self, *, ResourceARN: str, Tags: Sequence[TagTypeDef]) -> Dict[str, Any]:
        """
        Attaches a key-value pair to a resource, as identified by its Amazon Resource
        Name
        (ARN).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#tag_resource)
        """

    def untag_resource(self, *, ResourceARN: str, TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Detaches a key-value pair from a resource, as identified by its Amazon Resource
        Name
        (ARN).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#untag_resource)
        """

    def update_account_preferences(
        self, *, UserAuthorizationRequired: bool = ..., TrainingDataCollectionEnabled: bool = ...
    ) -> UpdateAccountPreferencesResultTypeDef:
        """
        Updates AWS Chatbot account preferences.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.update_account_preferences)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#update_account_preferences)
        """

    def update_chime_webhook_configuration(
        self,
        *,
        ChatConfigurationArn: str,
        WebhookDescription: str = ...,
        WebhookUrl: str = ...,
        SnsTopicArns: Sequence[str] = ...,
        IamRoleArn: str = ...,
        LoggingLevel: str = ...,
    ) -> UpdateChimeWebhookConfigurationResultTypeDef:
        """
        Updates a Amazon Chime webhook configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.update_chime_webhook_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#update_chime_webhook_configuration)
        """

    def update_microsoft_teams_channel_configuration(
        self,
        *,
        ChatConfigurationArn: str,
        ChannelId: str,
        ChannelName: str = ...,
        SnsTopicArns: Sequence[str] = ...,
        IamRoleArn: str = ...,
        LoggingLevel: str = ...,
        GuardrailPolicyArns: Sequence[str] = ...,
        UserAuthorizationRequired: bool = ...,
    ) -> UpdateTeamsChannelConfigurationResultTypeDef:
        """
        Updates an Microsoft Teams channel configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.update_microsoft_teams_channel_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#update_microsoft_teams_channel_configuration)
        """

    def update_slack_channel_configuration(
        self,
        *,
        ChatConfigurationArn: str,
        SlackChannelId: str,
        SlackChannelName: str = ...,
        SnsTopicArns: Sequence[str] = ...,
        IamRoleArn: str = ...,
        LoggingLevel: str = ...,
        GuardrailPolicyArns: Sequence[str] = ...,
        UserAuthorizationRequired: bool = ...,
    ) -> UpdateSlackChannelConfigurationResultTypeDef:
        """
        Updates a Slack channel configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.update_slack_channel_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#update_slack_channel_configuration)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_chime_webhook_configurations"]
    ) -> DescribeChimeWebhookConfigurationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_slack_channel_configurations"]
    ) -> DescribeSlackChannelConfigurationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_slack_user_identities"]
    ) -> DescribeSlackUserIdentitiesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_slack_workspaces"]
    ) -> DescribeSlackWorkspacesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_microsoft_teams_channel_configurations"]
    ) -> ListMicrosoftTeamsChannelConfigurationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_microsoft_teams_configured_teams"]
    ) -> ListMicrosoftTeamsConfiguredTeamsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_microsoft_teams_user_identities"]
    ) -> ListMicrosoftTeamsUserIdentitiesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/chatbot.html#Chatbot.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_chatbot/client/#get_paginator)
        """
