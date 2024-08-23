from __future__ import annotations

import responses


@responses.activate
def test_feeds_get_custom_vuls(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/feeds/custom/custom-vulnerabilities", json={"key": "value"}
    )
    resp = pcce.feeds.get_custom_vuls()
    assert resp == {"key": "value"}


@responses.activate
def test_feeds_set_custom_vuls(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/feeds/custom/custom-vulnerabilities")
    pcce.feeds.set_custom_vuls(
        data={
            "_id": "string",
            "digest": "string",
            "rules": [
                {
                    "_id": "string",
                    "maxVersionInclusive": "string",
                    "md5": "string",
                    "minVersionInclusive": "string",
                    "name": "string",
                    "package": "string",
                    "type": "unknown",
                }
            ],
        }
    )


@responses.activate
def test_feeds_get_custom_malware(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/feeds/custom/malware", json={"key": "value"})
    resp = pcce.feeds.get_custom_malware()
    assert resp == {"key": "value"}


@responses.activate
def test_feeds_set_custom_malware(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/feeds/custom/malware")
    pcce.feeds.set_custom_malware(
        data={
            "_id": "string",
            "digest": "string",
            "feed": [{"allowed": True, "md5": "string", "modified": 0, "name": "string"}],
            "modified": "2024-07-12T09:46:19.435Z",
        }
    )
