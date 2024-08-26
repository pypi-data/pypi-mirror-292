"""Tests for the generative firewall SDK."""
import re
from unittest.mock import Mock, call

import pytest
from pytest_mock import MockerFixture

from rime_sdk.generative_firewall import FirewallClient, FirewallInstance
from rime_sdk.swagger.swagger_client import (
    FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody,
    FirewallInstanceManagerApi,
    GenerativefirewallCreateFirewallInstanceRequest,
    GenerativefirewallCreateFirewallInstanceResponse,
    GenerativefirewallFirewallAction,
    GenerativefirewallFirewallInstanceInfo,
    GenerativefirewallFirewallInstanceStatus,
    GenerativefirewallFirewallRuleConfig,
    GenerativefirewallGetFirewallInstanceResponse,
    GenerativefirewallListFirewallInstancesResponse,
    GenerativefirewallRuleOutput,
    GenerativefirewallUpdateFirewallInstanceResponse,
    GenerativefirewallValidateRequest,
    RiskscoreRiskCategoryType,
    ValidateRequestInput,
    ValidateRequestOutput,
)
from rime_sdk.swagger.swagger_client.api.firewall_api import FirewallApi
from rime_sdk.swagger.swagger_client.api_client import ApiClient
from rime_sdk.swagger.swagger_client.models.generativefirewall_get_firewall_effective_config_response import (
    GenerativefirewallGetFirewallEffectiveConfigResponse,
)
from rime_sdk.swagger.swagger_client.models.generativefirewall_validate_response import (
    GenerativefirewallValidateResponse,
)
from rime_sdk.swagger.swagger_client.models.rime_language import RimeLanguage
from rime_sdk.swagger.swagger_client.models.rime_uuid import RimeUUID

# skip the CI test for auth
# firewall.auth


@pytest.fixture()
def test_firewall_instance() -> FirewallInstance:
    yield FirewallInstance("foo", ApiClient())


@pytest.fixture()
def mock_get_firewall_instance(mocker: MockerFixture) -> Mock:
    """Mock out the GetFirewallInstance call."""

    def get_side_effect(
        firewall_instance_id: str,
    ) -> GenerativefirewallGetFirewallInstanceResponse:
        return GenerativefirewallGetFirewallInstanceResponse(
            firewall_instance=GenerativefirewallFirewallInstanceInfo(
                deployment_status=GenerativefirewallFirewallInstanceStatus.READY,
                config=GenerativefirewallFirewallRuleConfig(selected_rules=["bogus"]),
                firewall_instance_id=RimeUUID(uuid=firewall_instance_id),
                description="this is a server-side desc",
            ),
        )

    yield mocker.patch.object(
        FirewallInstanceManagerApi,
        "firewall_instance_manager_get_firewall_instance",
        side_effect=get_side_effect,
    )


@pytest.fixture()
def mock_firewall_validate2(mocker: MockerFixture) -> Mock:
    """Mock out the Validate call to a specific firewall instance."""

    yield mocker.patch.object(FirewallApi, "firewall_validate2")


@pytest.fixture()
def mock_firewall_effectiveconfig2(mocker: MockerFixture) -> Mock:
    """Mock out the effective config call to a specific firewall instance."""

    def effective_config_side_effect(
        firewall_instance_id_uuid: str,
    ) -> GenerativefirewallGetFirewallEffectiveConfigResponse:
        if firewall_instance_id_uuid == "none":
            return GenerativefirewallGetFirewallEffectiveConfigResponse(
                config=None,
            )
        return GenerativefirewallGetFirewallEffectiveConfigResponse(
            config=GenerativefirewallFirewallRuleConfig(language="LANGUAGE_EN"),
        )

    yield mocker.patch.object(
        FirewallApi,
        "firewall_get_firewall_effective_config2",
        side_effect=effective_config_side_effect,
    )


@pytest.fixture()
def mock_firewall_update(mocker: MockerFixture) -> Mock:
    """Mock out the update call to a specific firewall instance."""

    def firewall_instance_update_side_effect(
        body: FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody,
        firewall_instance_id_uuid: str,
    ) -> GenerativefirewallGetFirewallEffectiveConfigResponse:
        if firewall_instance_id_uuid == "none":
            return GenerativefirewallUpdateFirewallInstanceResponse(
                updated_firewall_instance=None,
            )
        return GenerativefirewallUpdateFirewallInstanceResponse(
            updated_firewall_instance=GenerativefirewallFirewallInstanceInfo(
                deployment_status=GenerativefirewallFirewallInstanceStatus.READY,
                config=body.config,
                firewall_instance_id=RimeUUID(uuid=firewall_instance_id_uuid),
                description=body.description,
            ),
        )

    yield mocker.patch.object(
        FirewallInstanceManagerApi,
        "firewall_instance_manager_update_firewall_instance",
        side_effect=firewall_instance_update_side_effect,
    )


class TestFirewallInstance:
    """Tests for the FirewallInstance class."""

    def test_init_and_access_properties(
        self, test_firewall_instance: FirewallInstance, mock_get_firewall_instance: Mock
    ):
        """Test initializing the FirewallInstance."""
        assert (
            test_firewall_instance.status
            == GenerativefirewallFirewallInstanceStatus.READY
        )
        assert (
            test_firewall_instance.rule_config
            == GenerativefirewallFirewallRuleConfig(selected_rules=["bogus"]).to_dict()
        )
        assert test_firewall_instance.firewall_instance_id == "foo"
        mock_get_firewall_instance.assert_has_calls(calls=[call("foo"), call("foo")])

    def test_validate(
        self,
        test_firewall_instance: FirewallInstance,
        mock_firewall_validate2: Mock,
    ):
        """Test validating against the firewall instance."""
        mock_firewall_validate2.return_value = GenerativefirewallValidateResponse(
            input_results={
                "FIREWALL_RULE_TYPE_PROMPT_INJECTION": GenerativefirewallRuleOutput(
                    rule_name="Prompt Injection",
                    action=GenerativefirewallFirewallAction.ALLOW,
                    risk_category=RiskscoreRiskCategoryType.SECURITY_RISK,
                ),
            }
        )

        with pytest.raises(ValueError):
            test_firewall_instance.validate()

        validation_res = test_firewall_instance.validate("ignore")
        mock_firewall_validate2.assert_called_once_with(
            body=GenerativefirewallValidateRequest(
                input=ValidateRequestInput(user_input_text="ignore"),
                output=ValidateRequestOutput(output_text=None),
            ),
            firewall_instance_id_uuid="foo",
        )
        expected_res = {
            "input_results": {
                "FIREWALL_RULE_TYPE_PROMPT_INJECTION": {
                    "rule_name": "Prompt Injection",
                    "action": "FIREWALL_ACTION_ALLOW",
                    "risk_category": "RISK_CATEGORY_TYPE_SECURITY_RISK",
                },
            }
        }
        assert validation_res == expected_res

    def test_str(
        self, test_firewall_instance: FirewallInstance, mock_get_firewall_instance: Mock
    ):
        """Test the __str__ method."""
        assert (
            str(test_firewall_instance)
            == 'FirewallInstance(id="foo", description="this is a server-side desc")'
        )

    def test_get_effective_config(
        self,
        test_firewall_instance: FirewallInstance,
        mock_firewall_effectiveconfig2: Mock,
    ):
        """Test get effective config for the firewall instance."""
        res = test_firewall_instance.get_effective_config()
        assert (
            res
            == GenerativefirewallFirewallRuleConfig(language="LANGUAGE_EN").to_dict()
        )

        fw_none = FirewallInstance("none", ApiClient())
        res_none = fw_none.get_effective_config()
        assert res_none == {}

        mock_firewall_effectiveconfig2.assert_has_calls(
            calls=[
                call(firewall_instance_id_uuid="foo"),
                call(firewall_instance_id_uuid="none"),
            ]
        )

    @pytest.mark.parametrize(
        "rule_config, description, expected_req",
        [
            (
                {},
                None,
                FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody(
                    config=GenerativefirewallFirewallRuleConfig(),
                    description=None,
                ),
            ),
            (
                {"language": "LANGUAGE_JA"},
                "desc2",
                FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody(
                    config=GenerativefirewallFirewallRuleConfig(language="LANGUAGE_JA"),
                    description="desc2",
                ),
            ),
            (
                None,
                "no_config",
                FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody(
                    config=None,
                    description="no_config",
                ),
            ),
            (
                {"individual_rules_config": {"off_topic": {"in_domain_intents": []}}},
                None,
                FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody(
                    config=GenerativefirewallFirewallRuleConfig(
                        individual_rules_config={
                            "off_topic": {"in_domain_intents": []},
                        }
                    ),
                    description=None,
                ),
            ),
            (
                {
                    "language": "LANGUAGE_EN",
                    "individual_rules_config": {
                        "off_topic": {"in_domain_intents": ["Example Data Point"]},
                        "unknown_external_source": {},
                    },
                    "selected_rules": [
                        "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                        "FIREWALL_RULE_TYPE_TOXICITY",
                    ],
                },
                None,
                FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody(
                    config=GenerativefirewallFirewallRuleConfig(
                        language="LANGUAGE_EN",
                        individual_rules_config={
                            "off_topic": {"in_domain_intents": ["Example Data Point"]},
                            "unknown_external_source": {},
                        },
                        selected_rules=[
                            "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                            "FIREWALL_RULE_TYPE_TOXICITY",
                        ],
                    ),
                    description=None,
                ),
            ),
            (
                {
                    "individual_rules_config": {"denial_of_service_input": {}},
                    "selected_rules": [
                        "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                        "FIREWALL_RULE_TYPE_TOXICITY",
                    ],
                },
                None,
                FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody(
                    config=GenerativefirewallFirewallRuleConfig(
                        individual_rules_config={"denial_of_service_input": {}},
                        selected_rules=[
                            "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                            "FIREWALL_RULE_TYPE_TOXICITY",
                        ],
                    ),
                    description=None,
                ),
            ),
        ],
    )
    def test_update_successful(
        self,
        test_firewall_instance: FirewallInstance,
        rule_config: dict,
        description: str,
        expected_req: FirewallinstanceFirewallInstanceFirewallInstanceIdUuidBody,
        mock_firewall_update: Mock,
        mock_get_firewall_instance: Mock,
    ):
        """Test the update_firewall_instance method."""

        test_firewall_instance.update_firewall_instance(
            config=rule_config,
            description=description,
            block_until_ready_poll_rate_sec=0.1,
        )
        mock_firewall_update.assert_called_once_with(expected_req, "foo")
        mock_get_firewall_instance.assert_called_with("foo")
        # This tests that the FirewallInstance is populated with the rule config
        # returned by the server, and not the rule config directly supplied
        # by the user.
        assert (
            test_firewall_instance.rule_config
            == GenerativefirewallFirewallRuleConfig(selected_rules=["bogus"]).to_dict()
        )

    @pytest.mark.parametrize(
        "rule_config, expected_raises",
        [
            (
                {
                    "individual_rules_config": {"denial_of_service_input": None},
                },
                pytest.raises(
                    TypeError,
                    match="Each individual rule config must be a dictionary. Value 'None' for rule config 'denial_of_service_input' is not a dictionary",
                ),
            ),
            (
                {
                    "individual_rules_config": [],
                },
                pytest.raises(
                    TypeError, match="individual rules config must be a dict"
                ),
            ),
            (
                {
                    "individual_rules_config": {"denial_of_service_input": 5},
                },
                pytest.raises(
                    TypeError,
                    match="Each individual rule config must be a dictionary. Value '5' for rule config 'denial_of_service_input' is not a dictionary",
                ),
            ),
            (
                {
                    "individual_rules_config": {"extraneous_key": {}},
                },
                pytest.raises(
                    ValueError,
                    match="Found unrecognized rule 'extraneous_key' in `rule_config.individual_rules_config`. The list of accepted individual rule configs",
                ),
            ),
            (
                {
                    "individual_rules_config": {
                        "pii_detection_input": {"foo": "bar", "baz": "qux"}
                    },
                },
                pytest.raises(
                    ValueError,
                    match="Provided individual rule config for rule 'pii_detection_input' has unrecognized keys '(foo.*baz|baz.*foo)",
                ),
            ),
        ],
    )
    def test_update_bad_individual_rules_config(
        self,
        test_firewall_instance: FirewallInstance,
        rule_config: dict,
        expected_raises,
    ) -> None:
        """Test `update_firewall_instance` with a bad individual rules config."""
        with expected_raises:
            test_firewall_instance.update_firewall_instance(config=rule_config)

    def test_update_no_config_and_description(
        self,
        test_firewall_instance: FirewallInstance,
    ) -> None:
        """Test `update_firewall_instance` with no config and description."""
        with pytest.raises(
            ValueError,
            match="A new `config` or `description` must be provided.",
        ):
            test_firewall_instance.update_firewall_instance()

    @pytest.mark.parametrize(
        "rule_config, expected_raises",
        [
            (
                {
                    "selected_rules": [
                        "zwerg",
                        "Kobold",
                        "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                    ],
                },
                pytest.raises(
                    ValueError,
                    match="Unrecognized firewall rule type enum values '(zwerg.*Kobold|Kobold.*zwerg)'.*(FIREWALL_RULE_TYPE.*){5,}",
                ),
            ),
            (
                {"selected_rules": 5},
                pytest.raises(TypeError, match="selected_rules must be a list"),
            ),
            (
                {"selected_rules": {}},
                pytest.raises(TypeError, match="selected_rules must be a list"),
            ),
        ],
    )
    def test_update_bad_selected_rules(
        self,
        test_firewall_instance: FirewallInstance,
        rule_config: dict,
        expected_raises,
    ) -> None:
        """Test `update_firewall_instance` with a bad selected_rules."""
        with expected_raises:
            test_firewall_instance.update_firewall_instance(config=rule_config)

    @pytest.mark.parametrize(
        "rule_config",
        [{"foo": "bar"}, {"language": "LANGUAGE_JA", "foo": None}],
    )
    def test_update_extra_fields(
        self,
        test_firewall_instance: FirewallInstance,
        rule_config: dict,
    ):
        """Test `update_firewall_instance` raises an exception when there are unexpected fields."""
        with pytest.raises(
            ValueError,
            match=re.escape("Found unexpected keys in `rule_config`: ['foo']"),
        ):
            test_firewall_instance.update_firewall_instance(config=rule_config)

    @pytest.mark.parametrize(
        "incorrect_language",
        [RimeLanguage.UNSPECIFIED, "asdfasdfklasjdf", "german my dude"],
    )
    def test_update_incorrectly_specified_language(
        self, test_firewall_instance: FirewallInstance, incorrect_language: str
    ):
        """Test `update_firewall_instance` raises an exception on incorrect language."""
        with pytest.raises(
            ValueError,
            match=f"Provided language {incorrect_language} is invalid",
        ):
            test_firewall_instance.update_firewall_instance(
                config={"language": incorrect_language},
            )

    @pytest.mark.parametrize(
        "block_until_ready_kwargs, expected_forwarded_kwargs",
        [
            (
                {"block_until_ready_verbose": True},
                {"verbose": True, "consecutive_ready_count": 2},
            ),
            ({"block_until_ready_verbose": None}, {"consecutive_ready_count": 2}),
            (
                {
                    "block_until_ready_timeout_sec": None,
                    "block_until_ready_poll_rate_sec": 5.0,
                },
                {"poll_rate_sec": 5.0, "consecutive_ready_count": 2},
            ),
            (
                {
                    "block_until_ready_timeout_sec": 1.0,
                    "block_until_ready_poll_rate_sec": None,
                },
                {"timeout_sec": 1.0, "consecutive_ready_count": 2},
            ),
        ],
    )
    def test_update_block_until_ready_args(
        self,
        test_firewall_instance: FirewallInstance,
        mock_firewall_update: Mock,
        mocker: MockerFixture,
        block_until_ready_kwargs: dict,
        expected_forwarded_kwargs: dict,
    ):
        """Test `update_firewall_instance` forwards block_until_ready kwargs."""

        block_until_ready_mock = mocker.patch.object(
            FirewallInstance, "block_until_ready"
        )
        test_firewall_instance.update_firewall_instance(
            config={}, **block_until_ready_kwargs
        )
        block_until_ready_mock.assert_called_once_with(**expected_forwarded_kwargs)
        mock_firewall_update.assert_called()

    @pytest.mark.parametrize(
        "block_until_ready_kwargs",
        [
            {
                "block_until_ready_timeout_sec": None,
                "block_until_ready_poll_rate_sec": -5.0,
            },
            {
                "block_until_ready_timeout_sec": 0,
                "block_until_ready_poll_rate_sec": None,
            },
            {
                "block_until_ready_timeout_sec": "ab",
                "block_until_ready_poll_rate_sec": None,
            },
            {
                "block_until_ready_timeout_sec": -10,
                "block_until_ready_poll_rate_sec": 2,
            },
            {
                "block_until_ready_timeout_sec": 10,
                "block_until_consecutive_ready_count": -2,
            },
        ],
    )
    def test_update_block_until_ready_incorrect_args(
        self,
        test_firewall_instance: FirewallInstance,
        block_until_ready_kwargs: dict,
    ):
        """Test `update_firewall_instance` returns error on invalid input."""

        with pytest.raises(
            ValueError,
            match="The value must be a positive number.",
        ):
            test_firewall_instance.update_firewall_instance(
                config={}, **block_until_ready_kwargs
            )

    def test_block_until_multiple_ready(
        self, test_firewall_instance: FirewallInstance, mocker: MockerFixture
    ):
        """Test the block until ready method for the firewall instance."""
        return_values = [
            GenerativefirewallGetFirewallInstanceResponse(
                firewall_instance=GenerativefirewallFirewallInstanceInfo(
                    deployment_status=GenerativefirewallFirewallInstanceStatus.READY,
                ),
            ),
            GenerativefirewallGetFirewallInstanceResponse(
                firewall_instance=GenerativefirewallFirewallInstanceInfo(
                    deployment_status=GenerativefirewallFirewallInstanceStatus.PENDING,
                ),
            ),
            GenerativefirewallGetFirewallInstanceResponse(
                firewall_instance=GenerativefirewallFirewallInstanceInfo(
                    deployment_status=GenerativefirewallFirewallInstanceStatus.PENDING,
                ),
            ),
            GenerativefirewallGetFirewallInstanceResponse(
                firewall_instance=GenerativefirewallFirewallInstanceInfo(
                    deployment_status=GenerativefirewallFirewallInstanceStatus.READY,
                ),
            ),
            GenerativefirewallGetFirewallInstanceResponse(
                firewall_instance=GenerativefirewallFirewallInstanceInfo(
                    deployment_status=GenerativefirewallFirewallInstanceStatus.READY,
                ),
            ),
        ]
        mock = mocker.patch.object(
            FirewallInstanceManagerApi,
            "firewall_instance_manager_get_firewall_instance",
            side_effect=return_values,
        )

        test_firewall_instance.block_until_ready(
            poll_rate_sec=0.0001,
            consecutive_ready_count=2,
        )
        mock.assert_has_calls([call("foo")] * len(return_values))

    def test_block_until_ready_timeout(
        self, test_firewall_instance: FirewallInstance, mocker: MockerFixture
    ):
        """Test the block until ready with timeout."""
        get_mock = mocker.patch.object(
            FirewallInstanceManagerApi,
            "firewall_instance_manager_get_firewall_instance",
        )
        get_mock.return_value = GenerativefirewallGetFirewallInstanceResponse(
            firewall_instance=GenerativefirewallFirewallInstanceInfo(
                deployment_status=GenerativefirewallFirewallInstanceStatus.PENDING,
            ),
        )
        with pytest.raises(TimeoutError):
            test_firewall_instance.block_until_ready(
                poll_rate_sec=0.0001, timeout_sec=0.003
            )

    @pytest.mark.parametrize(
        "block_until_ready_kwargs",
        [
            {
                "timeout_sec": None,
                "poll_rate_sec": -5.0,
            },
            {
                "timeout_sec": 0,
                "poll_rate_sec": None,
            },
            {
                "timeout_sec": "ab",
                "poll_rate_sec": None,
            },
            {
                "timeout_sec": -10,
                "poll_rate_sec": 2,
            },
            {
                "timeout_sec": None,
                "poll_rate_sec": None,
            },
            {
                "consecutive_ready_count": -2,
            },
        ],
    )
    def test_block_until_ready_timeout_incorrect_input(
        self,
        test_firewall_instance: FirewallInstance,
        block_until_ready_kwargs: dict,
    ):
        """Test `block_until_ready` returns error on invalid input."""
        with pytest.raises(
            ValueError,
            match="The value must be a positive number.",
        ):
            test_firewall_instance.block_until_ready(**block_until_ready_kwargs)


@pytest.fixture()
def mock_create_firewall_instance(mocker: MockerFixture) -> Mock:
    """Mock out the CreateFirewallInstance call."""

    def create_side_effect(
        _body: GenerativefirewallCreateFirewallInstanceRequest,
    ) -> GenerativefirewallCreateFirewallInstanceResponse:
        return GenerativefirewallCreateFirewallInstanceResponse(
            firewall_instance_id=RimeUUID(uuid="didierdrogba")
        )

    yield mocker.patch.object(
        FirewallInstanceManagerApi,
        "firewall_instance_manager_create_firewall_instance",
        side_effect=create_side_effect,
    )


@pytest.fixture
def firewall_client():
    """Fake FirewallClient object for testing."""
    return FirewallClient("")


def test_create_firewall_client_with_api_key():
    """Test creating a firewall client with api key."""
    firewall = FirewallClient("foo.com", "super_secret_api_key")
    client_configuration = firewall._api_client.configuration
    assert client_configuration.host == "https://foo.com"
    assert client_configuration.api_key["X-Firewall-Api-Key"] == "super_secret_api_key"


def test_create_firewall_client_with_auth_token():
    """Test creating a firewall client with auth token."""
    firewall = FirewallClient("foo.com", auth_token="secret")
    client_configuration = firewall._api_client.configuration
    assert client_configuration.host == "https://foo.com"
    assert client_configuration.api_key["X-Firewall-Auth-Token"] == "secret"


class TestFirewallClient:
    """Tests for the FirewallClient class."""

    @pytest.mark.parametrize(
        "rule_config, expected_req",
        [
            (
                {},
                GenerativefirewallCreateFirewallInstanceRequest(
                    config=GenerativefirewallFirewallRuleConfig(), description=""
                ),
            ),
            (
                {"language": "LANGUAGE_JA"},
                GenerativefirewallCreateFirewallInstanceRequest(
                    config=GenerativefirewallFirewallRuleConfig(language="LANGUAGE_JA"),
                    description="",
                ),
            ),
            (
                {"individual_rules_config": {"off_topic": {"in_domain_intents": []}}},
                GenerativefirewallCreateFirewallInstanceRequest(
                    config=GenerativefirewallFirewallRuleConfig(
                        individual_rules_config={
                            "off_topic": {"in_domain_intents": []},
                        }
                    ),
                    description="",
                ),
            ),
            (
                {
                    "language": "LANGUAGE_EN",
                    "individual_rules_config": {
                        "off_topic": {"in_domain_intents": ["Example Data Point"]},
                        "unknown_external_source": {},
                    },
                    "selected_rules": [
                        "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                        "FIREWALL_RULE_TYPE_TOXICITY",
                    ],
                },
                GenerativefirewallCreateFirewallInstanceRequest(
                    config=GenerativefirewallFirewallRuleConfig(
                        language="LANGUAGE_EN",
                        individual_rules_config={
                            "off_topic": {"in_domain_intents": ["Example Data Point"]},
                            "unknown_external_source": {},
                        },
                        selected_rules=[
                            "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                            "FIREWALL_RULE_TYPE_TOXICITY",
                        ],
                    ),
                    description="",
                ),
            ),
            (
                {
                    "individual_rules_config": {"denial_of_service_input": {}},
                    "selected_rules": [
                        "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                        "FIREWALL_RULE_TYPE_TOXICITY",
                    ],
                },
                GenerativefirewallCreateFirewallInstanceRequest(
                    config=GenerativefirewallFirewallRuleConfig(
                        individual_rules_config={"denial_of_service_input": {}},
                        selected_rules=[
                            "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                            "FIREWALL_RULE_TYPE_TOXICITY",
                        ],
                    ),
                    description="",
                ),
            ),
        ],
    )
    def test_create_firewall_instance(
        self,
        firewall_client: FirewallClient,
        mock_create_firewall_instance: Mock,
        mock_get_firewall_instance: Mock,
        rule_config: dict,
        expected_req: GenerativefirewallCreateFirewallInstanceRequest,
    ):
        """Test the create_firewall_instance method."""

        fw = firewall_client.create_firewall_instance(rule_config=rule_config)
        mock_create_firewall_instance.assert_called_once_with(expected_req)
        mock_get_firewall_instance.assert_called_with("didierdrogba")
        # This tests that the FirewallInstance is populated with the rule config
        # returned by the server, and not the rule config directly supplied
        # by the user.
        assert (
            fw.rule_config
            == GenerativefirewallFirewallRuleConfig(selected_rules=["bogus"]).to_dict()
        )

    def test_create_firewall_instance_with_description(
        self,
        firewall_client: FirewallClient,
        mock_create_firewall_instance: Mock,
        mock_get_firewall_instance: Mock,
    ):
        """Test the create_firewall_instance method with a description."""
        firewall_client.create_firewall_instance(rule_config={}, description="foobar")
        mock_create_firewall_instance.assert_called_once_with(
            GenerativefirewallCreateFirewallInstanceRequest(
                config=GenerativefirewallFirewallRuleConfig(), description="foobar"
            ),
        )
        mock_get_firewall_instance.assert_called_with("didierdrogba")

    @pytest.mark.parametrize(
        "rule_config, expected_raises",
        [
            (
                {
                    "individual_rules_config": {"denial_of_service_input": None},
                },
                pytest.raises(
                    TypeError,
                    match="Each individual rule config must be a dictionary. Value 'None' for rule config 'denial_of_service_input' is not a dictionary",
                ),
            ),
            (
                {
                    "individual_rules_config": [],
                },
                pytest.raises(
                    TypeError, match="individual rules config must be a dict"
                ),
            ),
            (
                {
                    "individual_rules_config": {"denial_of_service_input": 5},
                },
                pytest.raises(
                    TypeError,
                    match="Each individual rule config must be a dictionary. Value '5' for rule config 'denial_of_service_input' is not a dictionary",
                ),
            ),
            (
                {
                    "individual_rules_config": {"extraneous_key": {}},
                },
                pytest.raises(
                    ValueError,
                    match="Found unrecognized rule 'extraneous_key' in `rule_config.individual_rules_config`. The list of accepted individual rule configs",
                ),
            ),
            (
                {
                    "individual_rules_config": {
                        "pii_detection_input": {"foo": "bar", "baz": "qux"}
                    },
                },
                pytest.raises(
                    ValueError,
                    match="Provided individual rule config for rule 'pii_detection_input' has unrecognized keys '(foo.*baz|baz.*foo)",
                ),
            ),
        ],
    )
    def test_create_firewall_instance_bad_individual_rules_config(
        self, firewall_client: FirewallClient, rule_config: dict, expected_raises
    ) -> None:
        """Test `create_firewall_instance` with a bad individual rules config."""
        with expected_raises:
            firewall_client.create_firewall_instance(rule_config)

    @pytest.mark.parametrize(
        "rule_config, expected_raises",
        [
            (
                {
                    "selected_rules": [
                        "zwerg",
                        "Kobold",
                        "FIREWALL_RULE_TYPE_PROMPT_INJECTION",
                    ],
                },
                pytest.raises(
                    ValueError,
                    match="Unrecognized firewall rule type enum values '(zwerg.*Kobold|Kobold.*zwerg)'.*(FIREWALL_RULE_TYPE.*){5,}",
                ),
            ),
            (
                {"selected_rules": 5},
                pytest.raises(TypeError, match="selected_rules must be a list"),
            ),
            (
                {"selected_rules": {}},
                pytest.raises(TypeError, match="selected_rules must be a list"),
            ),
        ],
    )
    def test_create_firewall_instance_bad_selected_rules(
        self, firewall_client: FirewallClient, rule_config: dict, expected_raises
    ) -> None:
        """Test `create_firewall_instance` with a bad selected_rules."""
        with expected_raises:
            firewall_client.create_firewall_instance(rule_config)

    @pytest.mark.parametrize(
        "rule_config",
        [{"foo": "bar"}, {"language": "LANGUAGE_JA", "foo": None}],
    )
    def test_create_firewall_instance_extra_fields(
        self,
        firewall_client: FirewallClient,
        rule_config: dict,
    ):
        """Test `create_firewall_instance` raises an exception when there are unexpected fields."""
        with pytest.raises(
            ValueError,
            match=re.escape("Found unexpected keys in `rule_config`: ['foo']"),
        ):
            firewall_client.create_firewall_instance(rule_config)

    @pytest.mark.parametrize(
        "incorrect_language",
        [RimeLanguage.UNSPECIFIED, "asdfasdfklasjdf", "german my dude"],
    )
    def test_create_firewall_incorrectly_specified_language(
        self, firewall_client: FirewallClient, incorrect_language: str
    ):
        """Test `create_firewall_instance` raises an exception on incorrect language."""
        with pytest.raises(
            ValueError,
            match=f"Provided language {incorrect_language} is invalid",
        ):
            firewall_client.create_firewall_instance(
                {"language": incorrect_language},
            )

    @pytest.mark.parametrize(
        "block_until_ready_kwargs, expected_forwarded_kwargs",
        [
            ({"block_until_ready_verbose": True}, {"verbose": True}),
            ({"block_until_ready_verbose": None}, {}),
            (
                {
                    "block_until_ready_timeout_sec": None,
                    "block_until_ready_poll_rate_sec": 5.0,
                },
                {"poll_rate_sec": 5.0},
            ),
            (
                {
                    "block_until_ready_timeout_sec": 1.0,
                    "block_until_ready_poll_rate_sec": None,
                },
                {"timeout_sec": 1.0},
            ),
        ],
    )
    def test_create_firewall_block_until_ready_args(
        self,
        firewall_client: FirewallClient,
        mock_create_firewall_instance: Mock,
        mocker: MockerFixture,
        block_until_ready_kwargs: dict,
        expected_forwarded_kwargs: dict,
    ):
        """Test `create_firewall_instance` forwards block_until_ready kwargs."""

        block_until_ready_mock = mocker.patch.object(
            FirewallInstance, "block_until_ready"
        )
        firewall_client.create_firewall_instance({}, **block_until_ready_kwargs)
        block_until_ready_mock.assert_called_once_with(**expected_forwarded_kwargs)
        mock_create_firewall_instance.assert_called()

    @pytest.mark.parametrize(
        "block_until_ready_kwargs",
        [
            {
                "block_until_ready_timeout_sec": None,
                "block_until_ready_poll_rate_sec": -5.0,
            },
            {
                "block_until_ready_timeout_sec": 0,
                "block_until_ready_poll_rate_sec": None,
            },
            {
                "block_until_ready_timeout_sec": "ab",
                "block_until_ready_poll_rate_sec": None,
            },
            {
                "block_until_ready_timeout_sec": -10,
                "block_until_ready_poll_rate_sec": 2,
            },
        ],
    )
    def test_create_firewall_block_until_ready_incorrect_args(
        self,
        firewall_client: FirewallClient,
        block_until_ready_kwargs: dict,
    ):
        """Test `create_firewall_instance` returns error on invalid input."""

        with pytest.raises(
            ValueError,
            match="The value must be a positive number.",
        ):
            firewall_client.create_firewall_instance({}, **block_until_ready_kwargs)

    def test_get_firewall_instance(
        self,
        mock_get_firewall_instance: Mock,
        firewall_client: FirewallClient,
    ):
        """Test getting the FirewallInstance from the cluster."""

        fw = firewall_client.get_firewall_instance(firewall_instance_id="fook")
        assert fw.status == GenerativefirewallFirewallInstanceStatus.READY

        # This asserts that "status" property makes a GET request and we call
        # GET once during the init.
        mock_get_firewall_instance.assert_has_calls(
            calls=[
                call("fook"),
                call("fook"),
            ]
        )
        assert (
            fw.rule_config
            == GenerativefirewallFirewallRuleConfig(selected_rules=["bogus"]).to_dict()
        )

    def test_delete_firewall_instance(
        self, mocker: MockerFixture, firewall_client: FirewallClient
    ):
        """Test deleting the FirewallInstance from the cluster."""
        delete_firewall_mock = mocker.patch.object(
            FirewallInstanceManagerApi,
            "firewall_instance_manager_delete_firewall_instance",
        )
        firewall_client.delete_firewall_instance(firewall_instance_id="fook")
        delete_firewall_mock.assert_called_once_with("fook")

    def test_list_firewall_instances(
        self,
        mocker: MockerFixture,
        firewall_client: FirewallClient,
    ):
        """Test listing the FirewallInstances from the cluster."""

        def list_side_effect() -> GenerativefirewallListFirewallInstancesResponse:
            return GenerativefirewallListFirewallInstancesResponse(
                firewall_instances=[
                    GenerativefirewallFirewallInstanceInfo(
                        firewall_instance_id=RimeUUID(uuid="yee")
                    ),
                    GenerativefirewallFirewallInstanceInfo(
                        firewall_instance_id=RimeUUID(uuid="yoo")
                    ),
                ]
            )

        list_firewalls_mock = mocker.patch.object(
            FirewallInstanceManagerApi,
            "firewall_instance_manager_list_firewall_instances",
            side_effect=list_side_effect,
        )
        it = firewall_client.list_firewall_instances()
        _ = next(it)
        _ = next(it)
        list_firewalls_mock.assert_called_once()

        with pytest.raises(StopIteration):
            next(it)
