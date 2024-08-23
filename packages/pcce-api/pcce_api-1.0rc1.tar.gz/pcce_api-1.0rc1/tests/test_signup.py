from __future__ import annotations

import responses


@responses.activate
def test_signup_create_admin_account(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/signup")
    pcce.signup.create_admin_account(username="string", password="string")
