# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.policyinsights import PolicyInsightsClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestPolicyInsightsPolicyStatesOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(PolicyInsightsClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_list_query_results_for_management_group(self, resource_group):
        response = self.client.policy_states.list_query_results_for_management_group(
            policy_states_resource="str",
            management_group_name="str",
            management_groups_namespace="Microsoft.Management",
            api_version="2024-10-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_summarize_for_management_group(self, resource_group):
        response = self.client.policy_states.summarize_for_management_group(
            policy_states_summary_resource="str",
            management_group_name="str",
            management_groups_namespace="Microsoft.Management",
            api_version="2024-10-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_list_query_results_for_subscription(self, resource_group):
        response = self.client.policy_states.list_query_results_for_subscription(
            policy_states_resource="str",
            subscription_id="str",
            api_version="2024-10-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_summarize_for_subscription(self, resource_group):
        response = self.client.policy_states.summarize_for_subscription(
            policy_states_summary_resource="str",
            subscription_id="str",
            api_version="2024-10-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_list_query_results_for_resource_group(self, resource_group):
        response = self.client.policy_states.list_query_results_for_resource_group(
            policy_states_resource="str",
            subscription_id="str",
            resource_group_name=resource_group.name,
            api_version="2024-10-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_summarize_for_resource_group(self, resource_group):
        response = self.client.policy_states.summarize_for_resource_group(
            policy_states_summary_resource="str",
            subscription_id="str",
            resource_group_name=resource_group.name,
            api_version="2024-10-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_list_query_results_for_resource(self, resource_group):
        response = self.client.policy_states.list_query_results_for_resource(
            policy_states_resource="str",
            resource_id="str",
            api_version="2024-10-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_summarize_for_resource(self, resource_group):
        response = self.client.policy_states.summarize_for_resource(
            policy_states_summary_resource="str",
            resource_id="str",
            api_version="2024-10-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_begin_trigger_subscription_evaluation(self, resource_group):
        response = self.client.policy_states.begin_trigger_subscription_evaluation(
            subscription_id="str",
            api_version="2024-10-01",
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_begin_trigger_resource_group_evaluation(self, resource_group):
        response = self.client.policy_states.begin_trigger_resource_group_evaluation(
            subscription_id="str",
            resource_group_name=resource_group.name,
            api_version="2024-10-01",
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_list_query_results_for_policy_set_definition(self, resource_group):
        response = self.client.policy_states.list_query_results_for_policy_set_definition(
            policy_states_resource="str",
            subscription_id="str",
            policy_set_definition_name="str",
            authorization_namespace="Microsoft.Authorization",
            api_version="2024-10-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_summarize_for_policy_set_definition(self, resource_group):
        response = self.client.policy_states.summarize_for_policy_set_definition(
            policy_states_summary_resource="str",
            subscription_id="str",
            policy_set_definition_name="str",
            authorization_namespace="Microsoft.Authorization",
            api_version="2024-10-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_list_query_results_for_policy_definition(self, resource_group):
        response = self.client.policy_states.list_query_results_for_policy_definition(
            policy_states_resource="str",
            subscription_id="str",
            policy_definition_name="str",
            authorization_namespace="Microsoft.Authorization",
            api_version="2024-10-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_summarize_for_policy_definition(self, resource_group):
        response = self.client.policy_states.summarize_for_policy_definition(
            policy_states_summary_resource="str",
            subscription_id="str",
            policy_definition_name="str",
            authorization_namespace="Microsoft.Authorization",
            api_version="2024-10-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_list_query_results_for_subscription_level_policy_assignment(self, resource_group):
        response = self.client.policy_states.list_query_results_for_subscription_level_policy_assignment(
            policy_states_resource="str",
            subscription_id="str",
            policy_assignment_name="str",
            authorization_namespace="Microsoft.Authorization",
            api_version="2024-10-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_summarize_for_subscription_level_policy_assignment(self, resource_group):
        response = self.client.policy_states.summarize_for_subscription_level_policy_assignment(
            policy_states_summary_resource="str",
            subscription_id="str",
            policy_assignment_name="str",
            authorization_namespace="Microsoft.Authorization",
            api_version="2024-10-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_list_query_results_for_resource_group_level_policy_assignment(self, resource_group):
        response = self.client.policy_states.list_query_results_for_resource_group_level_policy_assignment(
            policy_states_resource="str",
            subscription_id="str",
            resource_group_name=resource_group.name,
            policy_assignment_name="str",
            authorization_namespace="Microsoft.Authorization",
            api_version="2024-10-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_policy_states_summarize_for_resource_group_level_policy_assignment(self, resource_group):
        response = self.client.policy_states.summarize_for_resource_group_level_policy_assignment(
            policy_states_summary_resource="str",
            subscription_id="str",
            resource_group_name=resource_group.name,
            policy_assignment_name="str",
            authorization_namespace="Microsoft.Authorization",
            api_version="2024-10-01",
        )

        # please add some check logic here by yourself
        # ...
