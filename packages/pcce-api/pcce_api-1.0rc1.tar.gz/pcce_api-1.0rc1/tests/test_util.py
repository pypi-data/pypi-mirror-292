from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_util_download_jenkins_plugin(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/util/prisma-cloud-jenkins-plugin.hpi", body=fobj.read())
    fobj.seek(0)
    resp = pcce.util.download_jenkins_plugin()
    assert resp.read() == fobj.read()


@responses.activate
def test_util_download_vmware_tas_title(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/util/tas-tile", body=fobj.read())
    fobj.seek(0)
    resp = pcce.util.download_vmware_tas_title()
    assert resp.read() == fobj.read()


@responses.activate
def test_util_download_arm64_twistcli_linux(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/util/arm64/twistcli", body=fobj.read())
    fobj.seek(0)
    resp = pcce.util.download_arm64_twistcli_linux()
    assert resp.read() == fobj.read()


@responses.activate
def test_util_download_arm64_twistcli_macos(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/util/osx/arm64/twistcli", body=fobj.read())
    fobj.seek(0)
    resp = pcce.util.download_arm64_twistcli_macos()
    assert resp.read() == fobj.read()


@responses.activate
def test_util_download_twistcli_macos(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/util/osx/twistcli", body=fobj.read())
    fobj.seek(0)
    resp = pcce.util.download_twistcli_macos()
    assert resp.read() == fobj.read()


@responses.activate
def test_util_download_twistcli_linux(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/util/twistcli", body=fobj.read())
    fobj.seek(0)
    resp = pcce.util.download_twistcli_linux()
    assert resp.read() == fobj.read()


@responses.activate
def test_util_download_twistcli_windows(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/util/windows/twistcli.exe", body=fobj.read())
    fobj.seek(0)
    resp = pcce.util.download_twistcli_windows()
    assert resp.read() == fobj.read()
