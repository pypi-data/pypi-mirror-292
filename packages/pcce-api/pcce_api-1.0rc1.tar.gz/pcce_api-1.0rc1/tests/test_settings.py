from __future__ import annotations

import responses


@responses.activate
def test_settings_add_cert_client(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/certificates")
    pcce.settings.add_cert_client()


@responses.activate
def test_settings_get_cert(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/settings/certs", json=[{"key": "value"} for i in range(10)]
    )
    resp = pcce.settings.get_cert()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_settings_add_cert(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/certs")
    pcce.settings.add_cert(console_san=[{"key": "value"}], ca_expiration="string", defender_old_expiration="string")


@responses.activate
def test_settings_list_code_repo(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/settings/coderepo", json=[{"key": "value"} for i in range(10)]
    )
    resp = pcce.settings.list_code_repo()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_settings_update_code_repo(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/coderepo")
    pcce.settings.update_code_repo()


@responses.activate
def test_settings_set_cert_console(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/console-certificate")
    pcce.settings.set_cert_console()


@responses.activate
def test_settings_list_alert(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/settings/custom-labels",
        json=[{"key": "value"} for i in range(10)],
    )
    resp = pcce.settings.list_alert()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_settings_add_alert(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/custom-labels")
    pcce.settings.add_alert()


@responses.activate
def test_settings_get_advanced_defender(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/defender", json={"key": "value"})
    resp = pcce.settings.get_advanced_defender()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_get_intelligence_stream(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/intelligence", json={"key": "value"})
    resp = pcce.settings.get_intelligence_stream()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_intelligence_stream(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/intelligence")
    pcce.settings.add_intelligence_stream()


@responses.activate
def test_settings_get_ldap_integration(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/ldap", json={"key": "value"})
    resp = pcce.settings.get_ldap_integration()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_ldap_integration(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/ldap")
    pcce.settings.add_ldap_integration()


@responses.activate
def test_settings_get_licence(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/license", json={"key": "value"})
    resp = pcce.settings.get_licence()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_license(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/license")
    pcce.settings.add_license()


@responses.activate
def test_settings_get_logging(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/logging", json={"key": "value"})
    resp = pcce.settings.get_logging()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_logging(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/logging")
    pcce.settings.add_logging()


@responses.activate
def test_settings_get_logon(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/logon", json={"key": "value"})
    resp = pcce.settings.get_logon()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_logon(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/logon")
    pcce.settings.add_logon()


@responses.activate
def test_settings_get_oauth(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/oauth", json={"key": "value"})
    resp = pcce.settings.get_oauth()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_oauth(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/oauth")
    pcce.settings.add_oauth()


@responses.activate
def test_settings_get_openid(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/oidc", json={"key": "value"})
    resp = pcce.settings.get_openid()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_openid(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/oidc")
    pcce.settings.add_openid()


@responses.activate
def test_settings_get_proxy(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/proxy", json={"key": "value"})
    resp = pcce.settings.get_proxy()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_proxy(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/proxy")
    pcce.settings.add_proxy()


@responses.activate
def test_settings_get_registry(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/registry", json={"key": "value"})
    resp = pcce.settings.get_registry()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_registry(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/registry")
    pcce.settings.add_registry()


@responses.activate
def test_settings_update_registry(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/settings/registry")
    pcce.settings.update_registry()


@responses.activate
def test_settings_get_saml(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/saml", json={"key": "value"})
    resp = pcce.settings.get_saml()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_saml(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/saml")
    pcce.settings.add_saml()


@responses.activate
def test_settings_get_scan(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/scan", json={"key": "value"})
    resp = pcce.settings.get_scan()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/scan")
    pcce.settings.add_scan()


@responses.activate
def test_settings_get_tas(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/tas", json={"key": "value"})
    resp = pcce.settings.get_tas()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_add_tas(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/tas")
    pcce.settings.add_tas()


@responses.activate
def test_settings_get_telemetry(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/telemetry", json={"key": "value"})
    resp = pcce.settings.get_telemetry()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_set_telemetry(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/settings/telemetry")
    pcce.settings.set_telemetry(enabled=True)


@responses.activate
def test_settings_get_vm_image(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/vm", json={"key": "value"})
    resp = pcce.settings.get_vm_image()
    assert resp == {"key": "value"}


@responses.activate
def test_settings_update_vm_image(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/settings/vm")
    pcce.settings.update_vm_image(
        data=[
            {
                "version": "aws",
                "region": "us-east-1",
                "credentialID": "IAM Role",
                "collections": [{"name": "All"}],
                "cap": 5,
                "scanners": 1,
                "consoleAddr": "127.0.0.1",
            }
        ]
    )


@responses.activate
def test_settings_get_wildfire(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/settings/wildfire", json={"key": "value"})
    resp = pcce.settings.get_wildfire()
    assert resp == {"key": "value"}
