"""GiantContext Python SDK.

Auto-generated from OpenAPI spec. Do not edit manually.
Run "pnpm generate:sdk" to regenerate.
"""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import quote

import httpx

__version__ = "1.0.0"
__all__ = ["GiantContext", "create_giant_context", "GiantContextConfig"]


# ============================================================================
# Configuration
# ============================================================================


class GiantContextConfig:
    """Configuration for the GiantContext SDK."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.giantcontext.com",
        timeout: float = 30.0,
    ):
        """Initialize SDK configuration.

        Args:
            api_key: Your API key (starts with gct_)
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout


# ============================================================================
# HTTP Client
# ============================================================================


class GiantContextClient:
    """Internal HTTP client with token management."""

    def __init__(self, config: GiantContextConfig):
        self._config = config
        self._jwt_token: str | None = None
        self._token_expires_at: float = 0
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={"Content-Type": "application/json"},
        )

    async def _get_token(self) -> str:
        """Exchange API key for JWT token (cached until expiry)."""
        # Return cached token if still valid (with 60s buffer)
        if self._jwt_token and time.time() < self._token_expires_at - 60:
            return self._jwt_token

        # Exchange API key for JWT
        response = await self._client.post(
            "/auth/token",
            json={"apiKey": self._config.api_key},
        )
        response.raise_for_status()
        data = response.json()

        self._jwt_token = data["token"]
        # Parse ISO timestamp to epoch
        from datetime import datetime

        expires_at = datetime.fromisoformat(data["expiresAt"].replace("Z", "+00:00"))
        self._token_expires_at = expires_at.timestamp()

        return self._jwt_token

    async def request(
        self,
        endpoint: str,
        method: str = "GET",
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an authenticated request."""
        token = await self._get_token()

        response = await self._client.request(
            method=method,
            url=endpoint,
            json=json,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()

        if response.status_code == 204:
            return None
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


# ============================================================================
# Base Resource
# ============================================================================


class BaseResource:
    """Base class for API resources."""

    def __init__(self, client: GiantContextClient):
        self._client = client

    async def _request(
        self,
        endpoint: str,
        method: str = "GET",
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an authenticated request."""
        return await self._client.request(endpoint, method, json, params)


# ============================================================================
# Resource Classes
# ============================================================================


class APIKeysResource(BaseResource):
    """API Keys API methods."""

    async def list_my_api_keys(self) -> dict[str, Any]:
        """Get my API keys

        GET /me/api-keys
        """
        endpoint = "/me/api-keys"
        return await self._request(endpoint, method="GET")

    async def list_organization_api_keys(self, id: str) -> dict[str, Any]:
        """Get organization API keys

        GET /organizations/{id}/api-keys
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/api-keys"
        return await self._request(endpoint, method="GET")


class AppMembersResource(BaseResource):
    """App Members API methods."""

    async def get_app_member(
        self, id: str, project_id: str, app_id: str, member_id: str
    ) -> dict[str, Any]:
        """Get an app member by ID

        GET /organizations/{id}/projects/{projectId}/apps/{appId}/members/{memberId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/{quote(str(app_id), safe='')}/members/{quote(str(member_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_app_members(
        self, id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get members of an app

        GET /organizations/{id}/projects/{projectId}/apps/{appId}/members
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/{quote(str(app_id), safe='')}/members"
        return await self._request(endpoint, method="GET")


class BugReportsResource(BaseResource):
    """Bug Reports API methods."""

    async def list_my_bug_reports(self) -> dict[str, Any]:
        """Get my bug reports

        GET /me/bug-reports
        """
        endpoint = "/me/bug-reports"
        return await self._request(endpoint, method="GET")

    async def get_bug_report_comments(self, id: str) -> dict[str, Any]:
        """Get comments for a bug report

        GET /me/bug-reports/{id}/comments
        """
        endpoint = f"/me/bug-reports/{quote(str(id), safe='')}/comments"
        return await self._request(endpoint, method="GET")


class CRMResource(BaseResource):
    """CRM API methods."""

    async def get_crm_activity(
        self, organization_id: str, project_id: str, app_id: str, activity_id: str
    ) -> dict[str, Any]:
        """Get activity

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/activities/{activityId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/activities/{quote(str(activity_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_crm_activities_list(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Get activities

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/activities"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def log_crm_activity(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Log activity

        POST /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/activities"
        return await self._request(endpoint, method="POST", json=data)

    async def get_crm_company_activities(
        self, organization_id: str, project_id: str, app_id: str, company_id: str
    ) -> list[dict[str, Any]]:
        """Get activities for a company

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/companies/{companyId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/companies/{quote(str(company_id), safe='')}/activities"
        return await self._request(endpoint, method="GET")

    async def get_crm_company_contacts(
        self, organization_id: str, project_id: str, app_id: str, company_id: str
    ) -> list[dict[str, Any]]:
        """Get contacts for a company

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/companies/{companyId}/contacts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/companies/{quote(str(company_id), safe='')}/contacts"
        return await self._request(endpoint, method="GET")

    async def get_crm_company(
        self, organization_id: str, project_id: str, app_id: str, company_id: str
    ) -> dict[str, Any]:
        """Get company

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/companies/{companyId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/companies/{quote(str(company_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_crm_companies_list(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Get companies

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/companies
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/companies"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_crm_contact_activities(
        self, organization_id: str, project_id: str, app_id: str, contact_id: str
    ) -> list[dict[str, Any]]:
        """Get activities for a contact

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/activities"
        return await self._request(endpoint, method="GET")

    async def set_crm_contact_field(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        contact_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Set contact field

        PUT /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}/fields
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/fields"
        return await self._request(endpoint, method="PUT", json=data)

    async def get_crm_contact(
        self, organization_id: str, project_id: str, app_id: str, contact_id: str
    ) -> dict[str, Any]:
        """Get contact

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def update_crm_contact(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        contact_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update contact

        PUT /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}"
        return await self._request(endpoint, method="PUT", json=data)

    async def tag_crm_contact(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        contact_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Tag contact

        POST /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}/tags
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/tags"
        return await self._request(endpoint, method="POST", json=data)

    async def untag_crm_contact(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        contact_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Untag contact

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}/tags
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/tags"
        return await self._request(endpoint, method="DELETE", json=data)

    async def get_crm_contacts_list(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Get contacts

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_crm_contact(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create contact

        POST /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts"
        return await self._request(endpoint, method="POST", json=data)


class ChatResource(BaseResource):
    """Chat API methods."""

    async def get_chat_conversation(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        conversation_id: str,
        cursor: str | None = None,
        cursor_id: str | None = None,
        direction: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get chat conversation with paginated messages

        GET /organizations/{organizationId}/projects/{projectId}/apps/chat/{appId}/conversations/{conversationId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/chat/{quote(str(app_id), safe='')}/conversations/{quote(str(conversation_id), safe='')}"
        params = {
            "cursor": cursor,
            "cursorId": cursor_id,
            "direction": direction,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_chat_conversations(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Get all chat conversations

        GET /organizations/{organizationId}/projects/{projectId}/apps/chat/{appId}/conversations
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/chat/{quote(str(app_id), safe='')}/conversations"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class DevelopersResource(BaseResource):
    """Developers API methods."""

    async def get_developers_doc_category(
        self, organization_id: str, project_id: str, app_id: str, category_id: str
    ) -> dict[str, Any]:
        """Get developer doc category

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/categories/{categoryId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/categories/{quote(str(category_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_developers_doc_categories(
        self, organization_id: str, project_id: str, app_id: str
    ) -> list[dict[str, Any]]:
        """Get developer doc categories

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/categories
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/categories"
        return await self._request(endpoint, method="GET")

    async def get_developers_doc(
        self, organization_id: str, project_id: str, app_id: str, doc_id: str
    ) -> dict[str, Any]:
        """Get developer doc

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/docs/{docId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/docs/{quote(str(doc_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_developers_docs(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        category_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get developer docs

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/docs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/docs"
        params = {
            "page": page,
            "pageSize": page_size,
            "categoryId": category_id,
            "status": status,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_developers_sync_logs(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """List developer sync logs

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/sync-logs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/sync-logs"
        return await self._request(endpoint, method="GET")


class DraftsResource(BaseResource):
    """Drafts API methods."""

    async def generate_draft(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate AI content draft

        POST /drafts/generate
        """
        endpoint = "/drafts/generate"
        return await self._request(endpoint, method="POST", json=data)

    async def edit_draft(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an edit draft

        POST /drafts/edit
        """
        endpoint = "/drafts/edit"
        return await self._request(endpoint, method="POST", json=data)

    async def unarchive_draft(
        self, id: str, project_id: str, draft_id: str
    ) -> dict[str, Any]:
        """Unarchive a draft

        POST /organizations/{id}/projects/{projectId}/mind/drafts/{draftId}/unarchive
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts/{quote(str(draft_id), safe='')}/unarchive"
        return await self._request(endpoint, method="POST")

    async def archive_draft(
        self, id: str, project_id: str, draft_id: str
    ) -> dict[str, Any]:
        """Archive a draft

        POST /organizations/{id}/projects/{projectId}/mind/drafts/{draftId}/archive
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts/{quote(str(draft_id), safe='')}/archive"
        return await self._request(endpoint, method="POST")

    async def get_draft(
        self, id: str, project_id: str, draft_id: str
    ) -> dict[str, Any]:
        """Get a draft by ID

        GET /organizations/{id}/projects/{projectId}/mind/drafts/{draftId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts/{quote(str(draft_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_draft(
        self, id: str, project_id: str, draft_id: str
    ) -> dict[str, Any]:
        """Delete a draft

        DELETE /organizations/{id}/projects/{projectId}/mind/drafts/{draftId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts/{quote(str(draft_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_drafts(
        self,
        id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        include_archived: str | None = None,
    ) -> dict[str, Any]:
        """List drafts for a project

        GET /organizations/{id}/projects/{projectId}/mind/drafts
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "includeArchived": include_archived,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class EmailResource(BaseResource):
    """Email API methods."""

    async def send_transactional_email(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Send transactional email

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/actions/send
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/actions/send"
        return await self._request(endpoint, method="POST", json=data)

    async def get_contact_email_timeline(
        self, organization_id: str, project_id: str, app_id: str, contact_id: str
    ) -> dict[str, Any]:
        """Contact email timeline

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/contacts/{contactId}/timeline
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/timeline"
        return await self._request(endpoint, method="GET")

    async def get_email(
        self, organization_id: str, project_id: str, app_id: str, email_id: str
    ) -> dict[str, Any]:
        """Get email template

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_email_recipient(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        email_id: str,
        recipient_id: str,
    ) -> dict[str, Any]:
        """Get email recipient

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}/recipients/{recipientId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}/recipients/{quote(str(recipient_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def unsubscribe_email_recipient(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        email_id: str,
        recipient_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Unsubscribe a recipient

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}/recipients/{recipientId}/unsubscribe
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}/recipients/{quote(str(recipient_id), safe='')}/unsubscribe"
        return await self._request(endpoint, method="POST", json=data)

    async def get_email_recipients(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        email_id: str,
        page: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """List email recipients

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}/recipients
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}/recipients"
        params = {
            "page": page,
            "pageSize": page_size,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def subscribe_email_recipient(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        email_id: str,
        data: dict[str, Any],
    ) -> Any:
        """Subscribe a contact

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}/recipients
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}/recipients"
        return await self._request(endpoint, method="POST", json=data)

    async def get_emails(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get email templates

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_email_footer(
        self, organization_id: str, project_id: str, app_id: str, footer_id: str
    ) -> dict[str, Any]:
        """Get email footer

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/footers/{footerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/footers/{quote(str(footer_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_email_footers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get email footers

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/footers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/footers"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_email_header(
        self, organization_id: str, project_id: str, app_id: str, header_id: str
    ) -> dict[str, Any]:
        """Get email header

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/headers/{headerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/headers/{quote(str(header_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_email_headers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get email headers

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/headers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/headers"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_email_send(
        self, organization_id: str, project_id: str, app_id: str, send_id: str
    ) -> dict[str, Any]:
        """Get email send with events

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/sends/{sendId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/sends/{quote(str(send_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def update_email_send(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        send_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update send

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/sends/{sendId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/sends/{quote(str(send_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def get_email_sends(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        email_id: str | None = None,
        contact_id: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """List email sends

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/sends
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/sends"
        params = {
            "page": page,
            "pageSize": page_size,
            "emailId": email_id,
            "contactId": contact_id,
            "status": status,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_email_send(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a planned send

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/sends
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/sends"
        return await self._request(endpoint, method="POST", json=data)


class FeatureRequestsResource(BaseResource):
    """Feature Requests API methods."""

    async def get_popular_feature_requests(
        self,
        limit: str | None = None,
        offset: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Get popular feature requests

        GET /me/feature-requests/popular
        """
        endpoint = "/me/feature-requests/popular"
        params = {
            "limit": limit,
            "offset": offset,
            "status": status,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_my_feature_requests(self) -> dict[str, Any]:
        """Get my feature requests

        GET /me/feature-requests
        """
        endpoint = "/me/feature-requests"
        return await self._request(endpoint, method="GET")

    async def get_feature_request_comments(self, id: str) -> dict[str, Any]:
        """Get comments for a feature request

        GET /me/feature-requests/{id}/comments
        """
        endpoint = f"/me/feature-requests/{quote(str(id), safe='')}/comments"
        return await self._request(endpoint, method="GET")


class FormsResource(BaseResource):
    """Forms API methods."""

    async def get_form(
        self, organization_id: str, project_id: str, app_id: str, form_id: str
    ) -> dict[str, Any]:
        """Get form

        GET /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms/{formId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms/{quote(str(form_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_form_submission(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        form_id: str,
        submission_id: str,
    ) -> dict[str, Any]:
        """Get form submission

        GET /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms/{formId}/submissions/{submissionId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms/{quote(str(form_id), safe='')}/submissions/{quote(str(submission_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_form_submissions(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        form_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Get form submissions

        GET /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms/{formId}/submissions
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms/{quote(str(form_id), safe='')}/submissions"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_forms_list(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Get forms

        GET /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class HealthResource(BaseResource):
    """Health API methods."""

    async def get_health_echo(self) -> dict[str, Any]:
        """Verify LLM connectivity

        GET /health/echo
        """
        endpoint = "/health/echo"
        return await self._request(endpoint, method="GET")


class IdeasResource(BaseResource):
    """Ideas API methods."""

    async def approve_idea(
        self, id: str, project_id: str, idea_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Approve a Mind idea

        POST /organizations/{id}/projects/{projectId}/mind/ideas/{ideaId}/approve
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas/{quote(str(idea_id), safe='')}/approve"
        return await self._request(endpoint, method="POST", json=data)

    async def dismiss_idea(
        self, id: str, project_id: str, idea_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Dismiss a Mind idea

        POST /organizations/{id}/projects/{projectId}/mind/ideas/{ideaId}/dismiss
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas/{quote(str(idea_id), safe='')}/dismiss"
        return await self._request(endpoint, method="POST", json=data)

    async def get_idea(self, id: str, project_id: str, idea_id: str) -> dict[str, Any]:
        """Get a Mind idea

        GET /organizations/{id}/projects/{projectId}/mind/ideas/{ideaId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas/{quote(str(idea_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_ideas(
        self,
        id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """List Mind ideas for a project

        GET /organizations/{id}/projects/{projectId}/mind/ideas
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def trigger_ideation(
        self, id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Trigger Mind ideation for a project

        POST /organizations/{id}/projects/{projectId}/mind/ideas
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas"
        return await self._request(endpoint, method="POST", json=data)


class InvitationsResource(BaseResource):
    """Invitations API methods."""

    async def get_organization_invitation(
        self, id: str, invitation_id: str
    ) -> dict[str, Any]:
        """Get an invitation by ID

        GET /organizations/{id}/invitations/{invitationId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/invitations/{quote(str(invitation_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_organization_invitations(self, id: str) -> dict[str, Any]:
        """Get organization invitations

        GET /organizations/{id}/invitations
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/invitations"
        return await self._request(endpoint, method="GET")


class KBResource(BaseResource):
    """KB API methods."""

    async def get_kb_article(
        self, organization_id: str, project_id: str, app_id: str, article_id: str
    ) -> dict[str, Any]:
        """Get KB article

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/articles/{articleId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/articles/{quote(str(article_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_kb_articles(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        category_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get KB articles

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/articles
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/articles"
        params = {
            "page": page,
            "pageSize": page_size,
            "categoryId": category_id,
            "status": status,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_kb_category(
        self, organization_id: str, project_id: str, app_id: str, category_id: str
    ) -> dict[str, Any]:
        """Get KB category

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/categories/{categoryId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/categories/{quote(str(category_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_kb_categories(
        self, organization_id: str, project_id: str, app_id: str
    ) -> list[dict[str, Any]]:
        """Get KB categories

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/categories
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/categories"
        return await self._request(endpoint, method="GET")

    async def get_kb_settings(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get KB settings

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/settings
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/settings"
        return await self._request(endpoint, method="GET")


class MeResource(BaseResource):
    """Me API methods."""

    async def get_my_suspension_messages(self) -> list[dict[str, Any]]:
        """Get my suspension appeal messages

        GET /me/suspension-messages
        """
        endpoint = "/me/suspension-messages"
        return await self._request(endpoint, method="GET")

    async def get_my_notifications(
        self,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Get my notifications

        GET /me/notifications
        """
        endpoint = "/me/notifications"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "status": status,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_my_organizations(self) -> list[dict[str, Any]]:
        """Get organizations I belong to

        GET /me/organizations
        """
        endpoint = "/me/organizations"
        return await self._request(endpoint, method="GET")

    async def get_my_invitations(self) -> dict[str, Any]:
        """Get my pending invitations

        GET /me/invitations
        """
        endpoint = "/me/invitations"
        return await self._request(endpoint, method="GET")

    async def get_my_activities(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get my activity history

        GET /me/activities
        """
        endpoint = "/me/activities"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_me(self) -> dict[str, Any]:
        """Get current user profile and permissions

        GET /me
        """
        endpoint = "/me"
        return await self._request(endpoint, method="GET")


class NotificationsResource(BaseResource):
    """Notifications API methods."""

    async def send_notification(self, data: dict[str, Any]) -> dict[str, Any]:
        """Send a notification

        POST /notifications/send
        """
        endpoint = "/notifications/send"
        return await self._request(endpoint, method="POST", json=data)


class OrganizationMembersResource(BaseResource):
    """Organization Members API methods."""

    async def get_member_project_memberships(
        self, id: str, member_id: str
    ) -> list[dict[str, Any]]:
        """Get member project memberships

        GET /organizations/{id}/members/{memberId}/project-memberships
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/members/{quote(str(member_id), safe='')}/project-memberships"
        return await self._request(endpoint, method="GET")

    async def get_organization_member_activities(
        self,
        id: str,
        member_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get member activities

        GET /organizations/{id}/members/{memberId}/activities
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/members/{quote(str(member_id), safe='')}/activities"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_organization_member(self, id: str, member_id: str) -> dict[str, Any]:
        """Get a member by ID

        GET /organizations/{id}/members/{memberId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/members/{quote(str(member_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_organization_members(
        self,
        id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get organization members

        GET /organizations/{id}/members
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/members"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class OrganizationsResource(BaseResource):
    """Organizations API methods."""

    async def get_service_account(self, id: str, account_id: str) -> dict[str, Any]:
        """Get a service account

        GET /organizations/{id}/service-accounts/{accountId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/service-accounts/{quote(str(account_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_service_accounts(self, id: str) -> dict[str, Any]:
        """Get organization service accounts

        GET /organizations/{id}/service-accounts
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/service-accounts"
        return await self._request(endpoint, method="GET")

    async def get_organization_by_slug(self, slug: str) -> dict[str, Any]:
        """Get organization by slug

        GET /organizations/by-slug/{slug}
        """
        endpoint = f"/organizations/by-slug/{quote(str(slug), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_organization(self, id: str) -> dict[str, Any]:
        """Get an organization by ID

        GET /organizations/{id}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}"
        return await self._request(endpoint, method="GET")


class ProjectAppsResource(BaseResource):
    """Project Apps API methods."""

    async def get_project_app_by_slug(
        self, id: str, project_id: str, app_slug: str
    ) -> dict[str, Any]:
        """Get a project app by slug

        GET /organizations/{id}/projects/{projectId}/apps/by-slug/{appSlug}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/by-slug/{quote(str(app_slug), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_project_app(
        self, id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get a project app by ID

        GET /organizations/{id}/projects/{projectId}/apps/{appId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/{quote(str(app_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_deleted_project_apps(
        self, id: str, project_id: str
    ) -> list[dict[str, Any]]:
        """Get deleted apps in trash

        GET /organizations/{id}/projects/{projectId}/apps/trash
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/trash"
        return await self._request(endpoint, method="GET")

    async def get_project_apps(self, id: str, project_id: str) -> dict[str, Any]:
        """Get apps in a project

        GET /organizations/{id}/projects/{projectId}/apps
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/apps"
        return await self._request(endpoint, method="GET")


class ProjectBrandingResource(BaseResource):
    """Project Branding API methods."""

    async def get_project_branding(
        self, id: str, project_id: str, branding_id: str
    ) -> dict[str, Any]:
        """Get project branding

        GET /organizations/{id}/projects/{projectId}/brandings/{brandingId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/brandings/{quote(str(branding_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_project_brandings(self, id: str, project_id: str) -> dict[str, Any]:
        """Get project brandings

        GET /organizations/{id}/projects/{projectId}/brandings
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/brandings"
        return await self._request(endpoint, method="GET")


class ProjectDomainsResource(BaseResource):
    """Project Domains API methods."""

    async def get_domain_verification_instructions(
        self, id: str, project_id: str, domain_id: str
    ) -> dict[str, Any]:
        """Get domain verification instructions

        GET /organizations/{id}/projects/{projectId}/domains/{domainId}/verification
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/domains/{quote(str(domain_id), safe='')}/verification"
        return await self._request(endpoint, method="GET")

    async def list_project_domains(
        self, id: str, project_id: str
    ) -> list[dict[str, Any]]:
        """Get all domains for a project

        GET /organizations/{id}/projects/{projectId}/domains
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/domains"
        return await self._request(endpoint, method="GET")


class ProjectFilesResource(BaseResource):
    """Project Files API methods."""

    async def get_file_references(
        self, id: str, project_id: str, file_id: str
    ) -> list[dict[str, Any]]:
        """Get all places where a file is referenced

        GET /organizations/{id}/projects/{projectId}/files/{fileId}/references
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}/references"
        return await self._request(endpoint, method="GET")

    async def get_file_folder(
        self, id: str, project_id: str, folder_id: str
    ) -> dict[str, Any]:
        """Get a file folder

        GET /organizations/{id}/projects/{projectId}/files/folders/{folderId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/folders/{quote(str(folder_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def replace_file_content(
        self, id: str, project_id: str, file_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Replace file content

        PUT /organizations/{id}/projects/{projectId}/files/{fileId}/content
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}/content"
        return await self._request(endpoint, method="PUT", json=data)

    async def open_file(self, id: str, project_id: str, file_id: str) -> dict[str, Any]:
        """Read file content

        GET /organizations/{id}/projects/{projectId}/files/{fileId}/open
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}/open"
        return await self._request(endpoint, method="GET")

    async def get_file(self, id: str, project_id: str, file_id: str) -> dict[str, Any]:
        """Get a file

        GET /organizations/{id}/projects/{projectId}/files/{fileId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_file_folders(self, id: str, project_id: str) -> list[dict[str, Any]]:
        """Get file folders in a project

        GET /organizations/{id}/projects/{projectId}/files/folders
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/folders"
        return await self._request(endpoint, method="GET")

    async def search_files(
        self, id: str, project_id: str, query: str, limit: str | None = None
    ) -> list[dict[str, Any]]:
        """Search files by content

        GET /organizations/{id}/projects/{projectId}/files/search
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/search"
        params = {
            "query": query,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_file_trash(self, id: str, project_id: str) -> list[dict[str, Any]]:
        """Get items in trash

        GET /organizations/{id}/projects/{projectId}/files/trash
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/trash"
        return await self._request(endpoint, method="GET")

    async def save_file(
        self, id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Save a file from text or image content

        POST /organizations/{id}/projects/{projectId}/files/save
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files/save"
        return await self._request(endpoint, method="POST", json=data)

    async def get_files(
        self,
        id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        folder_id: str | None = None,
        mime_type: str | None = None,
    ) -> dict[str, Any]:
        """Get files in a project

        GET /organizations/{id}/projects/{projectId}/files
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/files"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "folderId": folder_id,
            "mimeType": mime_type,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ProjectLegalDocumentsResource(BaseResource):
    """Project Legal Documents API methods."""

    async def get_project_legal_document(
        self, id: str, project_id: str, document_id: str
    ) -> dict[str, Any]:
        """Get a project legal document by ID

        GET /organizations/{id}/projects/{projectId}/legal/{documentId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/legal/{quote(str(document_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_project_legal_documents(
        self, id: str, project_id: str
    ) -> dict[str, Any]:
        """List project legal documents

        GET /organizations/{id}/projects/{projectId}/legal
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/legal"
        return await self._request(endpoint, method="GET")


class ProjectMembersResource(BaseResource):
    """Project Members API methods."""

    async def get_project_member(
        self, id: str, project_id: str, member_id: str
    ) -> dict[str, Any]:
        """Get a project member by ID

        GET /organizations/{id}/projects/{projectId}/members/{memberId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/members/{quote(str(member_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_project_members(
        self,
        id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """Get project members

        GET /organizations/{id}/projects/{projectId}/members
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/members"
        params = {
            "page": page,
            "pageSize": page_size,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ProjectTrashResource(BaseResource):
    """Project Trash API methods."""

    async def get_project_trash_item(
        self, id: str, project_id: str, trash_id: str
    ) -> dict[str, Any]:
        """Get a single trash item

        GET /organizations/{id}/projects/{projectId}/trash/{trashId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/trash/{quote(str(trash_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_project_trash(
        self,
        id: str,
        project_id: str,
        type: str | None = None,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Get all items in project trash

        GET /organizations/{id}/projects/{projectId}/trash
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/trash"
        params = {
            "type": type,
            "page": page,
            "pageSize": page_size,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ProjectWorkflowsResource(BaseResource):
    """Project Workflows API methods."""

    async def get_workflow_run(
        self, id: str, project_id: str, run_id: str
    ) -> dict[str, Any]:
        """Get a workflow run and its tasks

        GET /organizations/{id}/projects/{projectId}/workflows/runs/{runId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/workflows/runs/{quote(str(run_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def dismiss_workflow_run(
        self, id: str, project_id: str, run_id: str
    ) -> dict[str, Any]:
        """Dismiss a workflow run

        DELETE /organizations/{id}/projects/{projectId}/workflows/runs/{runId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/workflows/runs/{quote(str(run_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_workflow_runs(
        self,
        id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        status: str | None = None,
        type: str | None = None,
        include_dismissed: str | None = None,
    ) -> dict[str, Any]:
        """List workflow runs

        GET /organizations/{id}/projects/{projectId}/workflows/runs
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/workflows/runs"
        params = {
            "page": page,
            "pageSize": page_size,
            "status": status,
            "type": type,
            "includeDismissed": include_dismissed,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_workflow_run(
        self, id: str, project_id: str, data: dict[str, Any]
    ) -> Any:
        """Start a workflow run

        POST /organizations/{id}/projects/{projectId}/workflows/runs
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/workflows/runs"
        return await self._request(endpoint, method="POST", json=data)


class ProjectsResource(BaseResource):
    """Projects API methods."""

    async def get_project_by_slug(self, id: str, project_slug: str) -> dict[str, Any]:
        """Get project by slug

        GET /organizations/{id}/projects/by-slug/{projectSlug}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/by-slug/{quote(str(project_slug), safe='')}"
        return await self._request(endpoint, method="GET")

    async def search_project(
        self,
        id: str,
        project_id: str,
        query: str,
        limit: str | None = None,
        source_types: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search project knowledge

        GET /organizations/{id}/projects/{projectId}/search
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/search"
        params = {
            "query": query,
            "limit": limit,
            "sourceTypes": source_types,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_project_urls(self, id: str, project_id: str) -> dict[str, Any]:
        """Get all project URLs

        GET /organizations/{id}/projects/{projectId}/urls
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}/urls"
        return await self._request(endpoint, method="GET")

    async def get_project(self, id: str, project_id: str) -> dict[str, Any]:
        """Get a project by ID

        GET /organizations/{id}/projects/{projectId}
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects/{quote(str(project_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_projects(
        self,
        id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Get projects in an organization

        GET /organizations/{id}/projects
        """
        endpoint = f"/organizations/{quote(str(id), safe='')}/projects"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class WebsiteResource(BaseResource):
    """Website API methods."""

    async def get_website_consent_settings(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get consent settings

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/consent
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/consent"
        return await self._request(endpoint, method="GET")

    async def get_website_dialog(
        self, organization_id: str, project_id: str, app_id: str, dialog_id: str
    ) -> dict[str, Any]:
        """Get dialog

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/dialogs/{dialogId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/dialogs/{quote(str(dialog_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_website_dialogs(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get dialogs

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/dialogs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/dialogs"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_custom_domain(
        self, organization_id: str, project_id: str, app_id: str, domain_id: str
    ) -> dict[str, Any]:
        """Get custom domain

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/domains/{domainId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/domains/{quote(str(domain_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_website_custom_domains(
        self, organization_id: str, project_id: str, app_id: str
    ) -> list[dict[str, Any]]:
        """Get custom domains

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/domains
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/domains"
        return await self._request(endpoint, method="GET")

    async def get_website_footer(
        self, organization_id: str, project_id: str, app_id: str, footer_id: str
    ) -> dict[str, Any]:
        """Get website footer

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/footers/{footerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/footers/{quote(str(footer_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_website_footers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get website footers

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/footers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/footers"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_header(
        self, organization_id: str, project_id: str, app_id: str, header_id: str
    ) -> dict[str, Any]:
        """Get website header

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/headers/{headerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/headers/{quote(str(header_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_website_headers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get website headers

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/headers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/headers"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_layout(
        self, organization_id: str, project_id: str, app_id: str, layout_id: str
    ) -> dict[str, Any]:
        """Get website layout

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/layouts/{layoutId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/layouts/{quote(str(layout_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_website_layouts(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get website layouts

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/layouts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/layouts"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_page(
        self, organization_id: str, project_id: str, app_id: str, page_id: str
    ) -> dict[str, Any]:
        """Get website page

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/pages/{pageId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/pages/{quote(str(page_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_website_pages(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get website pages

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/pages
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/pages"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_post(
        self, organization_id: str, project_id: str, app_id: str, post_id: str
    ) -> dict[str, Any]:
        """Get blog post

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/posts/{postId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/posts/{quote(str(post_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_website_posts(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get blog posts

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/posts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/posts"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_app_settings(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get website settings

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/settings
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/settings"
        return await self._request(endpoint, method="GET")

    async def get_website_sidebar(
        self, organization_id: str, project_id: str, app_id: str, sidebar_id: str
    ) -> dict[str, Any]:
        """Get website sidebar

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/sidebars/{sidebarId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/sidebars/{quote(str(sidebar_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_website_sidebars(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        search: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get website sidebars

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/sidebars
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/sidebars"
        params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_tags(
        self, organization_id: str, project_id: str, app_id: str
    ) -> list[str]:
        """Get website tags

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/tags
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/tags"
        return await self._request(endpoint, method="GET")

    async def get_website_tracking_settings(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get tracking settings

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/tracking
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/tracking"
        return await self._request(endpoint, method="GET")

    async def get_website_urls(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get existing website page URLs

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/urls
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/urls"
        return await self._request(endpoint, method="GET")


# ============================================================================
# Main SDK Class
# ============================================================================


class GiantContext:
    """GiantContext SDK client.

    Example:
        >>> async with create_giant_context(api_key="gct_...") as gc:
        ...     orgs = await gc.organizations.get_organizations()
        ...     print(orgs)
    """

    api_keys: APIKeysResource
    app_members: AppMembersResource
    bug_reports: BugReportsResource
    crm: CRMResource
    chat: ChatResource
    developers: DevelopersResource
    drafts: DraftsResource
    email: EmailResource
    feature_requests: FeatureRequestsResource
    forms: FormsResource
    health: HealthResource
    ideas: IdeasResource
    invitations: InvitationsResource
    kb: KBResource
    me: MeResource
    notifications: NotificationsResource
    organization_members: OrganizationMembersResource
    organizations: OrganizationsResource
    project_apps: ProjectAppsResource
    project_branding: ProjectBrandingResource
    project_domains: ProjectDomainsResource
    project_files: ProjectFilesResource
    project_legal_documents: ProjectLegalDocumentsResource
    project_members: ProjectMembersResource
    project_trash: ProjectTrashResource
    project_workflows: ProjectWorkflowsResource
    projects: ProjectsResource
    website: WebsiteResource

    def __init__(self, config: GiantContextConfig):
        """Initialize the SDK with configuration."""
        self._client = GiantContextClient(config)
        self.api_keys = APIKeysResource(self._client)
        self.app_members = AppMembersResource(self._client)
        self.bug_reports = BugReportsResource(self._client)
        self.crm = CRMResource(self._client)
        self.chat = ChatResource(self._client)
        self.developers = DevelopersResource(self._client)
        self.drafts = DraftsResource(self._client)
        self.email = EmailResource(self._client)
        self.feature_requests = FeatureRequestsResource(self._client)
        self.forms = FormsResource(self._client)
        self.health = HealthResource(self._client)
        self.ideas = IdeasResource(self._client)
        self.invitations = InvitationsResource(self._client)
        self.kb = KBResource(self._client)
        self.me = MeResource(self._client)
        self.notifications = NotificationsResource(self._client)
        self.organization_members = OrganizationMembersResource(self._client)
        self.organizations = OrganizationsResource(self._client)
        self.project_apps = ProjectAppsResource(self._client)
        self.project_branding = ProjectBrandingResource(self._client)
        self.project_domains = ProjectDomainsResource(self._client)
        self.project_files = ProjectFilesResource(self._client)
        self.project_legal_documents = ProjectLegalDocumentsResource(self._client)
        self.project_members = ProjectMembersResource(self._client)
        self.project_trash = ProjectTrashResource(self._client)
        self.project_workflows = ProjectWorkflowsResource(self._client)
        self.projects = ProjectsResource(self._client)
        self.website = WebsiteResource(self._client)

    async def close(self):
        """Close the SDK client."""
        await self._client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


def create_giant_context(
    api_key: str,
    base_url: str = "https://api.giantcontext.com",
    timeout: float = 30.0,
) -> GiantContext:
    """Create a GiantContext SDK instance.

    Args:
        api_key: Your API key (starts with gct_)
        base_url: Base URL for the API
        timeout: Request timeout in seconds

    Returns:
        GiantContext SDK instance

    Example:
        >>> gc = create_giant_context(api_key="gct_...")
        >>> orgs = await gc.organizations.get_organizations()
    """
    config = GiantContextConfig(api_key=api_key, base_url=base_url, timeout=timeout)
    return GiantContext(config)
