"""
Utilities
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from pcce.utils.file import download


class UtilAPI(APIEndpoint):
    """Utilities"""

    _path = "api/v1/util"

    def download_jenkins_plugin(self) -> BytesIO:
        """
        Downloads the Prisma Cloud Compute Jenkins plugin.
        """
        resp = self._get("prisma-cloud-jenkins-plugin.hpi", stream=True)
        return download(response=resp)

    def download_vmware_tas_title(self) -> BytesIO:
        """
        Downloads the VMware Tanzu Application Service tile for Prisma Cloud Compute.
        """
        resp = self._get("tas-tile", stream=True)
        return download(response=resp)

    def download_arm64_twistcli_linux(self) -> BytesIO:
        """
        Downloads the twistcli binary executable for ARM64 bit Linux platforms.
        """
        resp = self._get("arm64/twistcli", stream=True)
        return download(response=resp)

    def download_arm64_twistcli_macos(self) -> BytesIO:
        """
        Downloads the twistcli binary executable for MacOS platforms based on ARM64 architecture.
        """
        resp = self._get("osx/arm64/twistcli", stream=True)
        return download(response=resp)

    def download_twistcli_macos(self) -> BytesIO:
        """
        Downloads the twistcli binary executable for MacOS platforms.
        """
        resp = self._get("osx/twistcli", stream=True)
        return download(response=resp)

    def download_twistcli_linux(self) -> BytesIO:
        """
        Downloads the twistcli binary executable for Linux platforms.
        """
        resp = self._get("twistcli", stream=True)
        return download(response=resp)

    def download_twistcli_windows(self) -> BytesIO:
        """
        Downloads the twistcli binary executable for Windows platforms.
        """
        resp = self._get("windows/twistcli.exe", stream=True)
        return download(response=resp)
