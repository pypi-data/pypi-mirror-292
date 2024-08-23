"""
Policy
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint
from restfly.utils import dict_clean

from .schema.utils import PCCEDateTime
from .utils.file import download


class PoliciesAPI(APIEndpoint):
    """Policies"""

    _path = "api/v1/policies"

    def get_ci_image_compliance(self) -> dict:
        """
        Retrieves the compliance policy for images scanned in your continuous integration (CI) pipeline.
        A policy consists of ordered rules.

        Args:

        Example:
            >>> pcce.policies.get_ci_image_compliance()
        """
        return self._get("compliance/ci/images")

    def update_ci_image_compliance(self, rules: list[dict]) -> None:
        """
        Updates the compliance policy for images scanned in your continuous integration (CI) pipeline.
        All rules in the policy are updated in a single shot.

        Args:
            rules (object[]): Rules holds all policy rules.
        Example:
            >>> pcce.policies.get_ci_image_compliance()
        """
        return self._put("compliance/ci/images", json={"policyType": "ciImagesCompliance", "rules": rules})

    def get_ci_serverless_compliance(self) -> dict:
        """
        Retrieves the compliance policy for serverless functions built in your Continuous Integration (CI) pipeline.
            A policy consists of ordered rules.

        Example:
            >>> pcce.policies.get_ci_serverless_compliance()
        """
        return self._get("compliance/ci/serverless")

    def update_ci_serverless_compliance(self, rules: list[dict]) -> None:
        """
        Updates the compliance policy for serverless functions built in your Continuous Integration (CI) pipeline.
            All rules in the policy are updated in a single shot.

        Args:
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_ci_serverless_compliance()
        """
        return self._put("compliance/ci/serverless", json={"policyType": "ciServerlessCompliance", "rules": rules})

    def get_container_compliance(self) -> dict:
        """
        Retrieves the compliance policy for running containers.

        Example:
            >>> pcce.policies.get_container_compliance()
        """
        return self._get("compliance/container")

    def update_container_compliance(self, rules: list[dict]) -> None:
        """
        Updates the compliance policy for running containers.

        Args:
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_container_compliance()
        """
        return self._put("compliance/container", json={"policyType": "containerCompliance", "rules": rules})

    def get_impacted_container_compliance(
        self,
        offset: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
        rule_name: str | None = None,
    ) -> dict:
        """
        Lists the containers caught by your compliance policy on a per-rule basis. These rule names can be found from
            the name variable in the response from a GET on the basic policies/compliance endpoint.

        Args:
            offset (int): Offsets the result to a specific report count. Offset starts from 0.
            limit (int): Limit is the amount to fix.
            sort (str): Sorts the result using a key.
            reverse (bool): Sorts the result in reverse order.
            rule_name (str): RuleName is the rule name to apply.

        Example:
            >>> pcce.policies.get_impacted_container_compliance()
        """
        return self._get(
            "compliance/container/impacted",
            params=dict_clean(
                {"offset": offset, "limit": limit, "sort": sort, "reverse": reverse, "ruleName": rule_name}
            ),
        )

    def get_host_compliance(self) -> dict:
        """
        Retrieves the compliance policy for hosts protected by Defender.

        Example:
            >>> pcce.policies.get_host_compliance()
        """
        return self._get("compliance/host")

    def update_host_compliance(self, rules: list[dict]) -> None:
        """
        Updates the compliance policy for hosts protected by Defender.

        Args:
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_host_compliance()
        """
        return self._put("compliance/host", json={"policyType": "hostCompliance", "rules": rules})

    def get_serverless_compliance(self) -> dict:
        """
        Retrieves the compliance policy for serverless functions situated in your cloud provider's infrastructure.

        Example:
            >>> pcce.policies.get_serverless_compliance()
        """
        return self._get("compliance/serverless")

    def update_serverless_compliance(self, rules: list[dict]) -> None:
        """
        Updates the compliance policy for serverless functions situated in your cloud provider's infrastructure.

        Args:
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_serverless_compliance()
        """
        return self._put("compliance/serverless", json={"policyType": "serverlessCompliance", "rules": rules})

    def get_impacted_vms_compliance(
        self,
        offset: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
        rule_name: str | None = None,
    ) -> dict:
        """
        Retrieves a list of all resources a compliance rule impacts.

        Args:
            offset (int): Offsets the result to a specific report count. Offset starts from 0.
            limit (int): Limit is the amount to fix.
            sort (str): Sorts the result using a key.
            reverse (bool): Sorts the result in reverse order.
            rule_name (str): RuleName is the rule name to apply.

        Example:
            >>> pcce.policies.get_impacted_vms_compliance()
        """
        return self._get(
            "compliance/vms/impacted",
            params=dict_clean(
                {"offset": offset, "limit": limit, "sort": sort, "reverse": reverse, "ruleName": rule_name}
            ),
        )

    def get_agentless_app_firewall(self) -> dict:
        """
        Returns the agentless application firewall policy.

        Example:
            >>> pcce.policies.get_agentless_app_firewall()
        """
        return self._get("firewall/app/agentless")

    def update_agentless_app_firewall(self, min_port: int, max_port: int, rules: list[dict]) -> None:
        """
        Updates the agentless application firewall policy.

        Args:
            min_port (int): Minimum port number to use in the application firewall.
            max_port (int): Maximum port number to use in the application firewall.
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_agentless_app_firewall()
        """
        self._put("firewall/app/agentless", json={"minPort": min_port, "maxPort": max_port, "rules": rules})

    def get_agentless_app_firewall_impacted(
        self,
        offset: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
        rule_name: str | None = None,
    ) -> dict:
        """
        Returns a list of mirrored VMs for which the firewall policy rule applies to.

        Args:
            offset (int): Offsets the result to a specific report count. Offset starts from 0.
            limit (int): Limit is the amount to fix.
            sort (str): Sorts the result using a key.
            reverse (bool): Sorts the result in reverse order.
            rule_name (str): RuleName is the rule name to apply.

        Example:
            >>> pcce.policies.get_agentless_app_firewall_impacted()
        """
        return self._get(
            "firewall/app/agentless/impacted",
            params=dict_clean(
                {"offset": offset, "limit": limit, "sort": sort, "reverse": reverse, "ruleName": rule_name}
            ),
        )

    def get_agentless_app_firewall_resource(
        self,
        offset: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
        config_id: str | None = None,
    ) -> list:
        """
        Returns a list of mirrored VMs for which the firewall policy rule applies to.

        Args:
            offset (int): Offsets the result to a specific report count. Offset starts from 0.
            limit (int): Limit is the amount to fix.
            sort (str): Sorts the result using a key.
            reverse (bool): Sorts the result in reverse order.
            config_id (str): ConfigID is the ID of the VPC configuration.

        Example:
            >>> pcce.policies.get_agentless_app_firewall_impacted()
        """
        return self._get(
            "firewall/app/agentless/resources",
            params=dict_clean(
                {"offset": offset, "limit": limit, "sort": sort, "reverse": reverse, "configID": config_id}
            ),
        )

    def get_agentless_app_firewall_state(self) -> dict:
        """
        Returns the state for the agentless app firewall policy.

        Example:
            >>> pcce.policies.get_agentless_app_firewall_state()
        """
        return self._get("firewall/app/agentless/state")

    def generate_waas_api_spec_object(self, apispec: dict) -> dict:
        """
        Resolves the endpoints defined in an OpenAPI/Swagger specification and returns a waas.APISpec object.

        Args:
            apispec (Dict): a format for the OpenAPI/Swagger specification.

        Example:
            >>> pcce.policies.generate_waas_api_spec_object()
        """
        return self._post("firewall/app/apispec", json=apispec)

    def get_waas_app_embedded(self) -> dict:
        """
        Retrieves the WAAS policy for web apps protected by App-Embedded Defender. A policy consists of ordered rules.

        Example:
            >>> pcce.policies.get_waas_app_embedded()
        """
        return self._get("firewall/app/app-embedded")

    def update_waas_app_embedded(self, _id: str, min_port: int, max_port: int, rules: list[dict]) -> None:
        """
        Updates the WAAS policy for web apps protected by App-Embedded Defender. All rules in the policy are updated
            in a single shot.

        Args:
            _id (str): Unique internal ID.
            min_port (int): Minimum port number to use in the application firewall.
            max_port (int): Maximum port number to use in the application firewall.
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_waas_app_embedded()
        """
        self._put(
            "firewall/app/app-embedded", json={"_id": _id, "minPort": min_port, "maxPort": max_port, "rules": rules}
        )

    def get_waas_container(self) -> dict:
        """
        Retrieves the WAAS policy for containers. A policy consists of ordered rules.

        Example:
            >>> pcce.policies.get_waas_container()
        """
        return self._get("firewall/app/container")

    def update_waas_container(self, _id: str, min_port: int, max_port: int, rules: list[dict]) -> None:
        """
        Updates the WAAS policy for containers. All rules are updated in a single shot.

        Args:
            _id (str): Unique internal ID.
            min_port (int): Minimum port number to use in the application firewall.
            max_port (int): Maximum port number to use in the application firewall.
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_waas_container()
        """
        self._put("firewall/app/container", json={"_id": _id, "minPort": min_port, "maxPort": max_port, "rules": rules})

    def get_waas_container_impacted(
        self,
        offset: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
        rule_name: str | None = None,
    ) -> dict:
        """
        Returns a list of containers for which the firewall policy rule applies to.

        Args:
            offset (int): Offsets the result to a specific report count. Offset starts from 0.
            limit (int): Limit is the amount to fix.
            sort (str): Sorts the result using a key.
            reverse (bool): Sorts the result in reverse order.
            rule_name (str): RuleName is the rule name to apply.

        Example:
            >>> pcce.policies.get_waas_container_impacted()
        """
        return self._get(
            "firewall/app/container/impacted",
            params=dict_clean(
                {"offset": offset, "limit": limit, "sort": sort, "reverse": reverse, "ruleName": rule_name}
            ),
        )

    def get_waas_host(self) -> dict:
        """
        Retrieves the WAAS policy for hosts.

        Example:
            >>> pcce.policies.get_waas_host()
        """
        return self._get("firewall/app/host")

    def update_waas_host(self, _id: str, min_port: int, max_port: int, rules: list[dict]) -> dict:
        """
        Updates the WAAS policy for hosts.

        Args:
            _id (str): Unique internal ID.
            min_port (int): Minimum port number to use in the application firewall.
            max_port (int): Maximum port number to use in the application firewall.
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_waas_host()
        """
        return self._put(
            "firewall/app/host", json={"_id": _id, "minPort": min_port, "maxPort": max_port, "rules": rules}
        )

    def get_waas_host_impacted(
        self,
        offset: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
        rule_name: str | None = None,
    ) -> list:
        """
        Returns a list of hosts for which the firewall policy rule applies to

        Args:
            offset (int): Offsets the result to a specific report count. Offset starts from 0.
            limit (int): Limit is the amount to fix.
            sort (str): Sorts the result using a key.
            reverse (bool): Sorts the result in reverse order.
            rule_name (str): RuleName is the rule name to apply.

        Example:
            >>> pcce.policies.get_waas_host_impacted()
        """
        return self._get(
            "firewall/app/host/impacted",
            params=dict_clean(
                {"offset": offset, "limit": limit, "sort": sort, "reverse": reverse, "ruleName": rule_name}
            ),
        )

    def get_waas_network(self) -> dict:
        """
        Retrieves a list of all WAAS network lists.

        Example:
            >>> pcce.policies.get_waas_network()
        """
        return self._get("firewall/app/network-list")

    def create_waas_network(
        self,
        _id: str | None = None,
        description: str | None = None,
        disabled: bool | None = None,
        modified: PCCEDateTime | None = None,
        name: str | None = None,
        notes: str | None = None,
        owner: str | None = None,
        previous_name: str | None = None,
        subnets: list[str] | None = None,
    ) -> None:
        """
        Creates a new WAAS network list.

        Args:
            _id (str): Unique ID.
            description (str): Description of the network list.
            disabled (bool): Indicates if the rule is currently disabled (true) or not (false).
            modified (datetime): Datetime when the rule was last modified.
            name (str): Name of the rule.
            notes (str): Free-form text.
            owner (str): User who created or last modified the rule.
            previous_name (str): Previous name of the rule. Required for rule renaming.
            subnets (List[str]): List of the IPv4 addresses and IP CIDR blocks.
        Example:
            >>> pcce.policies.create_waas_network()
        """
        self._post(
            "firewall/app/network-list",
            json={
                "_id": _id,
                "description": description,
                "disabled": disabled,
                "modified": modified,
                "name": name,
                "notes": notes,
                "owner": owner,
                "previousName": previous_name,
                "subnets": subnets,
            },
        )

    def update_waas_network(
        self,
        _id: str | None = None,
        description: str | None = None,
        disabled: bool | None = None,
        modified: PCCEDateTime | None = None,
        name: str | None = None,
        notes: str | None = None,
        owner: str | None = None,
        previous_name: str | None = None,
        subnets: list[str] | None = None,
    ) -> None:
        """
        Updates an existing WAAS network list.

        Args:
            _id (str): Unique ID.
            description (str): Description of the network list.
            disabled (bool): Indicates if the rule is currently disabled (true) or not (false).
            modified (datetime): Datetime when the rule was last modified.
            name (str): Name of the rule.
            notes (str): Free-form text.
            owner (str): User who created or last modified the rule.
            previous_name (str): Previous name of the rule. Required for rule renaming.
            subnets (List[str]): List of the IPv4 addresses and IP CIDR blocks.

        Example:
            >>> pcce.policies.update_waas_network()
        """
        self._put(
            "firewall/app/network-list",
            json={
                "_id": _id,
                "description": description,
                "disabled": disabled,
                "modified": modified,
                "name": name,
                "notes": notes,
                "owner": owner,
                "previousName": previous_name,
                "subnets": subnets,
            },
        )

    def delete_waas_network(self, _id: str) -> None:
        """
        Deletes an existing WAAS network list.

        Example:
            >>> pcce.policies.delete_waas_network('id')
        """
        self._delete(f"firewall/app/network-list/{_id}")

    def get_out_of_band_waas(self) -> dict:
        """
        Discovers and detects the HTTP traffic for an existing WAAS out of band custom rule.

        Example:
            >>> pcce.policies.get_out_of_band_waas()
        """
        return self._get("firewall/app/out-of-band")

    def update_out_of_band_waas(self, _id: str, min_port: int, max_port: int, rules: list[dict]) -> None:
        """
        Updates or edits a WAAS custom rule for out of band traffic.

        Args:
            _id (str): Unique internal ID.
            min_port (int): Minimum port number to use in the application firewall.
            max_port (int): Maximum port number to use in the application firewall.
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_out_of_band_waas()
        """
        self._put(
            "firewall/app/out-of-band", json={"_id": _id, "minPort": min_port, "maxPort": max_port, "rules": rules}
        )

    def get_out_of_band_waas_impacted(
        self,
        offset: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
        reverse: bool | None = None,
        rule_name: str | None = None,
    ) -> dict:
        """
        Discovers and detects the impacted resources for the HTTP traffic in an existing WAAS out of band custom rule.

        Args:
            offset (int): Offsets the result to a specific report count. Offset starts from 0.
            limit (int): Limit is the amount to fix.
            sort (str): Sorts the result using a key.
            reverse (bool): Sorts the result in reverse order.
            rule_name (str): RuleName is the rule name to apply.

        Example:
            >>> pcce.policies.get_out_of_band_waas_impacted()
        """
        return self._get(
            "firewall/app/out-of-band/impacted",
            params=dict_clean(
                {"offset": offset, "limit": limit, "sort": sort, "reverse": reverse, "ruleName": rule_name}
            ),
        )

    def get_waas_serverless(self) -> dict:
        """
        Retrieves a list of all WAAS policy rules for serverless functions.

        Example:
            >>> pcce.policies.get_waas_serverless()
        """
        return self._get("firewall/app/serverless")

    def update_waas_serverless(self, _id: str, min_port: int, max_port: int, rules: list[dict]) -> None:
        """
        Updates the WAAS policy for serverless functions.

        Args:
            _id (str): Unique internal ID.
            min_port (int): Minimum port number to use in the application firewall.
            max_port (int): Maximum port number to use in the application firewall.
            rules (object[]): Rules holds all policy rules.

        Example:
            >>> pcce.policies.update_waas_serverless()
        """
        return self._put(
            "firewall/app/serverless", json={"_id": _id, "minPort": min_port, "maxPort": max_port, "rules": rules}
        )

    def get_cnns_container_and_host(self) -> dict:
        """
        Retrieves a list of all CNNS container and host rules.

        Example:
            >>> pcce.policies.get_cnns_container_and_host()
        """
        return self._get("firewall/network")

    def update_cnns_container_and_host(self, data: dict) -> None:
        """
        Updates all container and host CNNS rules in a single shot.

        Example:
            >>> pcce.policies.update_cnns_container_and_host()
        """
        return self._put("firewall/network", json=data)

    def get_runtime_app_embeded(self) -> dict:
        """
        Retrieves the runtime policy for apps protected by App-Embedded Defenders. A policy consists of ordered rules.

        Example:
            >>> pcce.policies.get_runtime_app_embeded()
        """
        return self._get("runtime/app-embedded")

    def create_runtime_app_embeded(self, data: dict) -> None:
        """
        Adds a runtime policy for app-embedded deployments

        Example:
            >>> pcce.policies.create_runtime_app_embeded()
        """
        return self._post("runtime/app-embedded", json=data)

    def update_runtime_app_embeded(self, data: dict) -> None:
        """
        Updates the runtime policy for app-embedded deployments.

        Args:
            data (Dict): runtime policy for app-embeded.

        Example:
            >>> pcce.policies.update_runtime_app_embeded()
        """
        return self._put("runtime/app-embedded", json=data)

    def get_runtime_container(self) -> dict:
        """
        Retrieves the runtime policy for containers protected by Defender.

        Example:
            >>> pcce.policies.get_runtime_container()
        """
        return self._get("runtime/container")

    def create_runtime_container(self, data: dict) -> None:
        """
        Adds the given container runtime policy rule.

        Example:
            >>> pcce.policies.create_runtime_container()
        """
        return self._post("runtime/container", json=data)

    def update_runtime_container(self, data: dict) -> None:
        """
        Updates the runtime policy for containers.

        Example:
            >>> pcce.policies.update_runtime_container()
        """
        return self._put("runtime/container", json=data)

    def get_runtime_container_impacted(self, params: dict | None = None) -> dict:
        """
        Returns the impacted images based on a given rule.

        Example:
            >>> pcce.policies.get_runtime_container_impacted()
        """
        if params is None:  # pragma: no branch
            params = {}
        return self._get("runtime/container/impacted", params=params)

    def get_runtime_host(self) -> dict:
        """
        Retrieves the runtime policy for hosts protected by Defender.

        Example:
            >>> pcce.policies.get_runtime_host()
        """
        return self._get("runtime/host")

    def create_runtime_host(self, data: dict) -> None:
        """
        Set the specified rule first.

        Example:
            >>> pcce.policies.create_runtime_host()
        """
        self._post("runtime/host", json=data)

    def update_runtime_host(self, data: dict) -> None:
        """
        Updates the runtime policy for hosts protected by Defender.

        Example:
            >>> pcce.policies.update_runtime_host()
        """
        self._put("runtime/host", json=data)

    def get_runtime_serverless(self) -> dict:
        """
        Retrieves the runtime policy for your serverless functions.

        Example:
            >>> pcce.policies.get_runtime_serverless()
        """
        return self._get("runtime/serverless")

    def create_runtime_serverless(self, data: dict) -> None:
        """
        Adds the given serverless runtime policy rule.

        Example:
            >>> pcce.policies.create_runtime_serverless()
        """
        self._post("runtime/serverless", json=data)

    def update_runtime_serverless(self, data: dict) -> None:
        """
        Updates the runtime policy for your serverless functions.

        Example:
            >>> pcce.policies.update_runtime_serverless()
        """
        self._put("runtime/serverless", json=data)

    def list_vulnerabitity_base_image(self) -> list:
        """
        Returns all the base image scopes and the list of base images digests for each of them.

        Example:
            >>> pcce.policies.list_vulnerabitity_image()
        """
        return self._get("vulnerability/base-images")

    def add_vulnerabitity_base_image(self, data: dict) -> None:
        """
        Adds the base images which match the given scope configuration.

        Example:
            >>> pcce.policies.add_vulnerabitity_image()
        """
        self._post("vulnerability/base-images", json=data)

    def download_vulnerabitity_base_image(self) -> BytesIO:
        """
        Downloads the base images rules data to CSV.

        Example:
            >>> pcce.policies.download_vulnerabitity_image()
        """

        resp = self._get("vulnerability/base-images/download", stream=True)
        return download(response=resp)

    def delete_vulnerabitity_base_image(self, _id: str) -> None:
        """
        Removes all base images under a given scope.

        Example:
            >>> pcce.policies.delete_vulnerabitity_image()
        """
        self._delete(f"vulnerability/base-images/{_id}")

    def get_vulnerabitity_ci_image(self) -> dict:
        """
        Retrieves the vulnerability policy for images scanned in your continuous integration (CI) pipeline.

        Example:
            >>> pcce.policies.get_vulnerabitity_ci_image()
        """
        return self._get("vulnerability/ci/images")

    def update_vulnerabitity_ci_image(self, data: dict) -> None:
        """
        Updates the policy for images scanned in your continuous integration (CI) pipeline.

        Example:
            >>> pcce.policies.update_vulnerabitity_ci_image()
        """
        self._put("vulnerability/ci/images", json=data)

    def get_vulnerabitity_ci_serverless(self) -> dict:
        """
        Retrieves the vulnerability policy for serverless functions scanned in your continuous integration
            (CI) pipeline.

        Example:
            >>> pcce.policies.get_vulnerabitity_ci_serverless()
        """
        return self._get("vulnerability/ci/serverless")

    def update_vulnerabitity_ci_serverless(self, data: dict) -> None:
        """
        Updates the vulnerability policy for serverless functions scanned in your continuous integration (CI) pipeline.

        Example:
            >>> pcce.policies.update_vulnerabitity_ci_serverless()
        """
        self._put("vulnerability/ci/serverless", json=data)

    def get_vulnerabitity_code_repo(self) -> dict:
        """
        Retrieves the vulnerability policy for code repositories.

        Example:
            >>> pcce.policies.get_vulnerabitity_code_repo()
        """
        return self._get("vulnerability/coderepos")

    def update_vulnerabitity_code_repo(self, data: dict) -> None:
        """
        Updates the vulnerability policy for your code repositories.

        Example:
            >>> pcce.policies.update_vulnerabitity_code_repo()
        """
        self._put("vulnerability/coderepos", json=data)

    def get_vulnerabitity_code_repo_impacted(self, params: dict | None = None) -> dict:
        """
        Lists the code repositories caught by your policy on a per-rule basis.

        Example:
            >>> pcce.policies.get_vulnerabitity_code_repo_impacted()
        """
        return self._get("vulnerability/coderepos/impacted", params=params)

    def get_vulnerabitity_host(self) -> dict:
        """
        Retrieves the vulnerability policy for your hosts protected by Defender.

        Example:
            >>> pcce.policies.get_vulnerabitity_host()
        """
        return self._get("vulnerability/host")

    def update_vulnerabitity_host(self, data: dict) -> None:
        """
        Updates the vulnerability policy for your hosts protected by Defender.

        Example:
            >>> pcce.policies.update_vulnerabitity_host()
        """
        self._put("vulnerability/host", json=data)

    def get_vulnerabitity_host_impacted(self, params: dict | None = None) -> dict:
        """
        Lists the hosts ensnared by your policy on a per-rule basis.

        Example:
            >>> pcce.policies.get_vulnerabitity_host_impacted()
        """
        return self._get("vulnerability/host/impacted", params=params)

    def get_vulnerabitity_deployed_images(self) -> dict:
        """
        Retrieves the vulnerability policy for deployed container images.

        Example:
            >>> pcce.policies.get_vulnerabitity_image()
        """
        return self._get("vulnerability/images")

    def update_vulnerabitity_deployed_images(self, data: dict) -> None:
        """
        Updates the vulnerability policy for deployed container images.

        Example:
            >>> pcce.policies.update_vulnerabitity_image()
        """
        self._put("vulnerability/images", json=data)

    def get_vulnerabitity_deployed_images_impacted(self, params: dict | None = None) -> dict:
        """
        Lists the images caught by your policy on a per-rule basis.

        Example:
            >>> pcce.policies.get_vulnerabitity_image_impacted()
        """
        return self._get("vulnerability/images/impacted", params=params)

    def get_vulnerabitity_serverless(self) -> dict:
        """
        Retrieves the vulnerability policy for serverless functions situated in your cloud provider's infrastructure.

        Example:
            >>> pcce.policies.get_vulnerabitity_serverless()
        """
        return self._get("vulnerability/serverless")

    def update_vulnerabitity_serverless(self, data: dict) -> None:
        """
        Updates the vulnerability policy for serverless functions situated in your cloud provider's infrastructure.

        Example:
            >>> pcce.policies.update_vulnerabitity_serverless()
        """
        self._put("vulnerability/serverless", json=data)
