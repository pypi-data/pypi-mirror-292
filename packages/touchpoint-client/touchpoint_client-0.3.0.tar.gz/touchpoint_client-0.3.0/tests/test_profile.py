import asyncio
import pytest

pytest_plugins = ("pytest_asyncio",)


def test_profile(default_client):
    profile = default_client.profile.profile()
    keys = [
        "id",
        "account_id",
        "username",
        "global_role",
        "created_on",
        "active",
        "is_confirmed",
        "two_factor",
        "modified_on",
        "personal_settings",
        "projects",
        "group_projects",
    ]
    for k in keys:
        assert k in profile, f"{k} not in profile"


@pytest.mark.asyncio(loop_scope="session")
async def test_profile_async(default_client_async):
    profile = await default_client_async.profile.profile()
    keys = [
        "id",
        "account_id",
        "username",
        "global_role",
        "created_on",
        "active",
        "is_confirmed",
        "two_factor",
        "modified_on",
        "personal_settings",
        "projects",
        "group_projects",
    ]
    for k in keys:
        assert k in profile, f"{k} not in profile"


def test_account(default_client):
    account = default_client.profile.account()
    keys = [
        "id",
        "account_settings",
        "global_account",
        "created_on",
        "modified_on",
        "active",
        "name",
        "type",
        "limits",
    ]
    for k in keys:
        assert k in account, f"{k} not in account"


@pytest.mark.asyncio(loop_scope="session")
async def test_account_async(default_client_async):
    account = await default_client_async.profile.account()
    keys = [
        "id",
        "account_settings",
        "global_account",
        "created_on",
        "modified_on",
        "active",
        "name",
        "type",
        "limits",
    ]
    for k in keys:
        assert k in account, f"{k} not in account"
