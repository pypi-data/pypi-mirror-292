from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_policies_get_ci_image_compliance(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/compliance/ci/images", json={"key": "value"})
    resp = pcce.policies.get_ci_image_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_ci_image_compliance(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/compliance/ci/images")
    pcce.policies.update_ci_image_compliance(rules=[{"key": "value"}])


@responses.activate
def test_policies_get_ci_serverless_compliance(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/compliance/ci/serverless", json={"key": "value"}
    )
    resp = pcce.policies.get_ci_serverless_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_ci_serverless_compliance(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/compliance/ci/serverless")
    pcce.policies.update_ci_serverless_compliance(rules=[{"key": "value"}])


@responses.activate
def test_policies_get_container_compliance(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/compliance/container", json={"key": "value"})
    resp = pcce.policies.get_container_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_container_compliance(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/compliance/container")
    pcce.policies.update_container_compliance(rules=[{"key": "value"}])


@responses.activate
def test_policies_get_impacted_container_compliance(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/compliance/container/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_impacted_container_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_host_compliance(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/compliance/host", json={"key": "value"})
    resp = pcce.policies.get_host_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_host_compliance(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/compliance/host")
    pcce.policies.update_host_compliance(rules=[{"key": "value"}])


@responses.activate
def test_policies_get_serverless_compliance(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/compliance/serverless", json={"key": "value"})
    resp = pcce.policies.get_serverless_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_serverless_compliance(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/compliance/serverless")
    pcce.policies.update_serverless_compliance(rules=[{"key": "value"}])


@responses.activate
def test_policies_get_impacted_vms_compliance(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/compliance/vms/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_impacted_vms_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_agentless_app_firewall(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/agentless", json={"key": "value"})
    resp = pcce.policies.get_agentless_app_firewall()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_agentless_app_firewall(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/firewall/app/agentless")
    pcce.policies.update_agentless_app_firewall(min_port=1000, max_port=2000, rules=[{"key": "value"}])


@responses.activate
def test_policies_get_agentless_app_firewall_impacted(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/agentless/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_agentless_app_firewall_impacted()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_agentless_app_firewall_resource(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/policies/firewall/app/agentless/resources",
        json=[{"key": "value"} for i in range(10)],
    )
    resp = pcce.policies.get_agentless_app_firewall_resource()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_policies_get_agentless_app_firewall_state(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/agentless/state", json={"key": "value"}
    )
    resp = pcce.policies.get_agentless_app_firewall_state()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_generate_waas_api_spec_object(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/policies/firewall/app/apispec")
    pcce.policies.generate_waas_api_spec_object(apispec={"key": "value"})


@responses.activate
def test_policies_get_waas_app_embedded(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/app-embedded", json={"key": "value"}
    )
    resp = pcce.policies.get_waas_app_embedded()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_waas_app_embedded(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/firewall/app/app-embedded")
    pcce.policies.update_waas_app_embedded(_id="str", min_port=1000, max_port=2000, rules=[{"key": "value"}])


@responses.activate
def test_policies_get_waas_container(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/container", json={"key": "value"})
    resp = pcce.policies.get_waas_container()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_waas_container(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/firewall/app/container")
    pcce.policies.update_waas_container(_id="str", min_port=1000, max_port=2000, rules=[{"key": "value"}])


@responses.activate
def test_policies_get_waas_container_impacted(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/container/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_waas_container_impacted()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_waas_host(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/host", json={"key": "value"})
    resp = pcce.policies.get_waas_host()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_waas_host(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/firewall/app/host")
    pcce.policies.update_waas_host(_id="str", min_port=1000, max_port=2000, rules=[{"key": "value"}])


@responses.activate
def test_policies_get_waas_host_impacted(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/host/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_waas_host_impacted()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_waas_network(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/network-list", json={"key": "value"}
    )
    resp = pcce.policies.get_waas_network()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_create_waas_network(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/policies/firewall/app/network-list")
    pcce.policies.create_waas_network()


@responses.activate
def test_policies_update_waas_network(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/firewall/app/network-list")
    pcce.policies.update_waas_network()


@responses.activate
def test_policies_delete_waas_network(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/policies/firewall/app/network-list/str")
    pcce.policies.delete_waas_network(_id="str")


@responses.activate
def test_policies_get_out_of_band_waas(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/out-of-band", json={"key": "value"}
    )
    resp = pcce.policies.get_out_of_band_waas()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_out_of_band_waas(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/firewall/app/out-of-band")
    pcce.policies.update_out_of_band_waas(_id="str", min_port=1000, max_port=2000, rules=[{"key": "value"}])


@responses.activate
def test_policies_get_out_of_band_waas_impacted(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/out-of-band/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_out_of_band_waas_impacted()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_waas_serverless(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/firewall/app/serverless", json={"key": "value"}
    )
    resp = pcce.policies.get_waas_serverless()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_waas_serverless(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/firewall/app/serverless")
    pcce.policies.update_waas_serverless(_id="str", min_port=1000, max_port=2000, rules=[{"key": "value"}])


@responses.activate
def test_policies_get_cnns_container_and_host(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/firewall/network", json={"key": "value"})
    resp = pcce.policies.get_cnns_container_and_host()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_cnns_container_and_host(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/firewall/network")
    pcce.policies.update_cnns_container_and_host(data={"key": "value"})


@responses.activate
def test_policies_get_runtime_app_embeded(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/runtime/app-embedded", json={"key": "value"})
    resp = pcce.policies.get_runtime_app_embeded()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_create_runtime_app_embeded(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/policies/runtime/app-embedded")
    pcce.policies.create_runtime_app_embeded(data={"key": "value"})


@responses.activate
def test_policies_update_runtime_app_embeded(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/runtime/app-embedded")
    pcce.policies.update_runtime_app_embeded(data={"key": "value"})


@responses.activate
def test_policies_get_runtime_container(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/runtime/container", json={"key": "value"})
    resp = pcce.policies.get_runtime_container()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_create_runtime_container(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/policies/runtime/container")
    pcce.policies.create_runtime_container(data={"key": "value"})


@responses.activate
def test_policies_update_runtime_container(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/runtime/container")
    pcce.policies.update_runtime_container(data={"key": "value"})


@responses.activate
def test_policies_get_runtime_container_impacted(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/runtime/container/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_runtime_container_impacted()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_runtime_host(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/runtime/host", json={"key": "value"})
    resp = pcce.policies.get_runtime_host()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_create_runtime_host(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/policies/runtime/host")
    pcce.policies.create_runtime_host(data={"key": "value"})


@responses.activate
def test_policies_update_runtime_host(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/runtime/host")
    pcce.policies.update_runtime_host(data={"key": "value"})


@responses.activate
def test_policies_get_runtime_serverless(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/runtime/serverless", json={"key": "value"})
    resp = pcce.policies.get_runtime_serverless()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_create_runtime_serverless(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/policies/runtime/serverless")
    pcce.policies.create_runtime_serverless(data={"key": "value"})


@responses.activate
def test_policies_update_runtime_serverless(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/runtime/serverless")
    pcce.policies.update_runtime_serverless(data={"key": "value"})


@responses.activate
def test_policies_list_vulnerabitity_base_image(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/policies/vulnerability/base-images",
        json=[{"key": "value"} for i in range(10)],
    )
    resp = pcce.policies.list_vulnerabitity_base_image()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_policies_add_vulnerabitity_base_image(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/policies/vulnerability/base-images")
    pcce.policies.add_vulnerabitity_base_image(data={"key": "value"})


@responses.activate
def test_policies_download_vulnerabitity_base_image(pcce):
    fobj = BytesIO(b"test content")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/base-images/download", body=fobj.read()
    )
    fobj.seek(0)
    resp = pcce.policies.download_vulnerabitity_base_image()
    assert resp.read() == fobj.read()


@responses.activate
def test_policies_delete_vulnerabitity_base_image(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/policies/vulnerability/base-images/string")
    pcce.policies.delete_vulnerabitity_base_image(_id="string")


@responses.activate
def test_policies_get_vulnerabitity_ci_image(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/ci/images", json={"key": "value"}
    )
    resp = pcce.policies.get_vulnerabitity_ci_image()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_vulnerabitity_ci_image(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/vulnerability/ci/images")
    pcce.policies.update_vulnerabitity_ci_image(data={"key": "value"})


@responses.activate
def test_policies_get_vulnerabitity_ci_serverless(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/ci/serverless", json={"key": "value"}
    )
    resp = pcce.policies.get_vulnerabitity_ci_serverless()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_vulnerabitity_ci_serverless(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/vulnerability/ci/serverless")
    pcce.policies.update_vulnerabitity_ci_serverless(data={"key": "value"})


@responses.activate
def test_policies_get_vulnerabitity_code_repo(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/coderepos", json={"key": "value"}
    )
    resp = pcce.policies.get_vulnerabitity_code_repo()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_vulnerabitity_code_repo(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/vulnerability/coderepos")
    pcce.policies.update_vulnerabitity_code_repo(data={"key": "value"})


@responses.activate
def test_policies_get_vulnerabitity_code_repo_impacted(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/coderepos/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_vulnerabitity_code_repo_impacted()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_vulnerabitity_host(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/host", json={"key": "value"})
    resp = pcce.policies.get_vulnerabitity_host()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_vulnerabitity_host(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/vulnerability/host")
    pcce.policies.update_vulnerabitity_host(data={"key": "value"})


@responses.activate
def test_policies_get_vulnerabitity_host_impacted(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/host/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_vulnerabitity_host_impacted()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_vulnerabitity_deployed_images(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/images", json={"key": "value"})
    resp = pcce.policies.get_vulnerabitity_deployed_images()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_vulnerabitity_deployed_images(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/vulnerability/images")
    pcce.policies.update_vulnerabitity_deployed_images(data={"key": "value"})


@responses.activate
def test_policies_get_vulnerabitity_deployed_images_impacted(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/images/impacted", json={"key": "value"}
    )
    resp = pcce.policies.get_vulnerabitity_deployed_images_impacted()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_get_vulnerabitity_serverless(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/policies/vulnerability/serverless", json={"key": "value"}
    )
    resp = pcce.policies.get_vulnerabitity_serverless()
    assert resp == {"key": "value"}


@responses.activate
def test_policies_update_vulnerabitity_serverless(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/policies/vulnerability/serverless")
    pcce.policies.update_vulnerabitity_serverless(data={"key": "value"})
