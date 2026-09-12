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

    async def list_my_api_keys(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        """List your own API keys across organizations; never returns the secret value

        GET /me/api-keys
        """
        endpoint = "/me/api-keys"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "organizationId": organization_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_organization_api_keys(
        self,
        organization_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """List all API keys in an organization; metadata only, no secret values

        GET /organizations/{organizationId}/api-keys
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/api-keys"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "userId": user_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class AppMembersResource(BaseResource):
    """App Members API methods."""

    async def get_app_member(
        self, organization_id: str, project_id: str, app_id: str, member_id: str
    ) -> dict[str, Any]:
        """Get an app member by ID

        GET /organizations/{organizationId}/projects/{projectId}/apps/{appId}/members/{memberId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/{quote(str(app_id), safe='')}/members/{quote(str(member_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_app_members(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        role: str | None = None,
    ) -> dict[str, Any]:
        """List users with explicit app-level roles, excluding inherited org and project access

        GET /organizations/{organizationId}/projects/{projectId}/apps/{appId}/members
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/{quote(str(app_id), safe='')}/members"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "role": role,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class BriefsResource(BaseResource):
    """Briefs API methods."""

    async def approve_brief(
        self, organization_id: str, project_id: str, brief_id: str
    ) -> dict[str, Any]:
        """Approve a ready brief, which starts draft generation from its draft prompt

        POST /organizations/{organizationId}/projects/{projectId}/mind/briefs/{briefId}/approve
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/briefs/{quote(str(brief_id), safe='')}/approve"
        return await self._request(endpoint, method="POST")

    async def reject_brief(
        self, organization_id: str, project_id: str, brief_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Reject a ready brief so it never reaches draft generation

        POST /organizations/{organizationId}/projects/{projectId}/mind/briefs/{briefId}/reject
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/briefs/{quote(str(brief_id), safe='')}/reject"
        return await self._request(endpoint, method="POST", json=data)

    async def get_brief(
        self, organization_id: str, project_id: str, brief_id: str
    ) -> dict[str, Any]:
        """Get one brief's full paper trail from idea to draft prompt

        GET /organizations/{organizationId}/projects/{projectId}/mind/briefs/{briefId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/briefs/{quote(str(brief_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_briefs(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        status: str | None = None,
        content_type: str | None = None,
        target_content_type: str | None = None,
        idea_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
    ) -> dict[str, Any]:
        """List Mind briefs for a project

        GET /organizations/{organizationId}/projects/{projectId}/mind/briefs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/briefs"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "status": status,
            "contentType": content_type,
            "targetContentType": target_content_type,
            "ideaId": idea_id,
            "createdAt": created_at,
            "updatedAt": updated_at,
            "startedAt": started_at,
            "completedAt": completed_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class BugReportsResource(BaseResource):
    """Bug Reports API methods."""

    async def list_my_bug_reports(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        source: str | None = None,
        report_count: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List bug reports you filed, with severity, status and GitHub issue link

        GET /me/bug-reports
        """
        endpoint = "/me/bug-reports"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "severity": severity,
            "source": source,
            "reportCount": report_count,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_bug_report_comments(
        self,
        bug_report_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        author: str | None = None,
        source: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List comments for a bug report

        GET /me/bug-reports/{bugReportId}/comments
        """
        endpoint = f"/me/bug-reports/{quote(str(bug_report_id), safe='')}/comments"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "author": author,
            "source": source,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class BuilderResource(BaseResource):
    """Builder API methods."""

    async def get_content_types(self) -> dict[str, Any]:
        """Get every content type and the blocks allowed in it

        GET /builder/content-types
        """
        endpoint = "/builder/content-types"
        return await self._request(endpoint, method="GET")

    async def get_block_styles(self) -> dict[str, Any]:
        """Get the styles schema shared by every block

        GET /builder/styles
        """
        endpoint = "/builder/styles"
        return await self._request(endpoint, method="GET")

    async def get_block(self, block_type: str, content_type: str) -> dict[str, Any]:
        """Get one block type's own fields and hints; shared styles come from getBlockStyles

        GET /builder/blocks/{blockType}
        """
        endpoint = f"/builder/blocks/{quote(str(block_type), safe='')}"
        params = {
            "contentType": content_type,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def delete_section(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Delete a section and every block inside it; recoverable from version history

        POST /organizations/{organizationId}/projects/{projectId}/content/sections/delete
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/sections/delete"
        return await self._request(endpoint, method="POST", json=data)

    async def insert_section(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert a section into a content tree

        POST /organizations/{organizationId}/projects/{projectId}/content/sections/insert
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/sections/insert"
        return await self._request(endpoint, method="POST", json=data)

    async def update_section(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a section's own properties; blocks stay untouched and columns cannot be patched

        POST /organizations/{organizationId}/projects/{projectId}/content/sections/update
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/sections/update"
        return await self._request(endpoint, method="POST", json=data)

    async def delete_block(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Delete a block, returning it; the prior tree stays in version history

        POST /organizations/{organizationId}/projects/{projectId}/content/blocks/delete
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/blocks/delete"
        return await self._request(endpoint, method="POST", json=data)

    async def insert_block(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert a block into a content tree

        POST /organizations/{organizationId}/projects/{projectId}/content/blocks/insert
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/blocks/insert"
        return await self._request(endpoint, method="POST", json=data)

    async def update_block(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a block's data and/or styles by merging only the fields you send; null clears a field

        POST /organizations/{organizationId}/projects/{projectId}/content/blocks/update
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/blocks/update"
        return await self._request(endpoint, method="POST", json=data)

    async def move_section(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Move a section before or after a sibling, or append it at the end

        POST /organizations/{organizationId}/projects/{projectId}/content/sections/move
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/sections/move"
        return await self._request(endpoint, method="POST", json=data)

    async def move_block(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Move a block beside a sibling or into a section, leaving its data unchanged

        POST /organizations/{organizationId}/projects/{projectId}/content/blocks/move
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/blocks/move"
        return await self._request(endpoint, method="POST", json=data)

    async def set_content_visibility(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Set whether content is listed and whether it requires a signed-in reader

        POST /organizations/{organizationId}/projects/{projectId}/content/visibility
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/visibility"
        return await self._request(endpoint, method="POST", json=data)

    async def unpublish_content(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Return a published item to draft — status only, never the body

        POST /organizations/{organizationId}/projects/{projectId}/content/unpublish
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/unpublish"
        return await self._request(endpoint, method="POST", json=data)

    async def publish_content(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Publish a page, post, article, doc or email — status only, never the body

        POST /organizations/{organizationId}/projects/{projectId}/content/publish
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/publish"
        return await self._request(endpoint, method="POST", json=data)

    async def search_content(
        self,
        organization_id: str,
        project_id: str,
        query: str | None = None,
        block_types: str | None = None,
        content_types: str | None = None,
        status: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Find a string or a block type inside content

        GET /organizations/{organizationId}/projects/{projectId}/content/search
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/search"
        params = {
            "query": query,
            "blockTypes": block_types,
            "contentTypes": content_types,
            "status": status,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_content(
        self, organization_id: str, project_id: str, content_type: str, content_id: str
    ) -> dict[str, Any]:
        """Get a content tree for editing

        GET /organizations/{organizationId}/projects/{projectId}/content
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content"
        params = {
            "contentType": content_type,
            "contentId": content_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class CRMResource(BaseResource):
    """CRM API methods."""

    async def get_crm_activity(
        self, organization_id: str, project_id: str, app_id: str, activity_id: str
    ) -> dict[str, Any]:
        """Get one activity's description, writing app and JSON data payload

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/activities/{activityId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/activities/{quote(str(activity_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_crm_activities(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        contact_id: str | None = None,
        company_id: str | None = None,
        written_by: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List the activity timeline for a whole CRM app, newest first, searchable

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/activities"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "contactId": contact_id,
            "companyId": company_id,
            "writtenBy": written_by,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def log_crm_activity(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Log a past-tense sentence onto a contact or company timeline, append-only

        POST /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/activities"
        return await self._request(endpoint, method="POST", json=data)

    async def list_crm_company_activities(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        company_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        written_by: str | None = None,
        contact_id: str | None = None,
    ) -> dict[str, Any]:
        """List a company's activity timeline, newest first, whatever app logged it

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/companies/{companyId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/companies/{quote(str(company_id), safe='')}/activities"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "writtenBy": written_by,
            "contactId": contact_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_crm_company_contacts(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        company_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        source: str | None = None,
        title: str | None = None,
        department: str | None = None,
        email: str | None = None,
        email_subscribed: str | None = None,
    ) -> dict[str, Any]:
        """List contacts linked to one company, paginated, alphabetical by last name

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/companies/{companyId}/contacts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/companies/{quote(str(company_id), safe='')}/contacts"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "source": source,
            "title": title,
            "department": department,
            "email": email,
            "emailSubscribed": email_subscribed,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_crm_company(
        self, organization_id: str, project_id: str, app_id: str, company_id: str
    ) -> dict[str, Any]:
        """Get one company with its profile fields and count of linked contacts

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/companies/{companyId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/companies/{quote(str(company_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_crm_companies(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        industry: str | None = None,
        size: str | None = None,
        email: str | None = None,
        website: str | None = None,
    ) -> dict[str, Any]:
        """List companies in one CRM app, alphabetical by name, each with contact count

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/companies
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/companies"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "industry": industry,
            "size": size,
            "email": email,
            "website": website,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_crm_contact_activities(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        contact_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        written_by: str | None = None,
        company_id: str | None = None,
    ) -> dict[str, Any]:
        """List a contact's activity timeline, newest first, including rows written by other apps

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/activities"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "writtenBy": written_by,
            "companyId": company_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def set_crm_contact_field(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        contact_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Set one key in a contact's custom properties, merging without clobbering siblings

        PUT /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}/fields
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/fields"
        return await self._request(endpoint, method="PUT", json=data)

    async def get_crm_contact(
        self, organization_id: str, project_id: str, app_id: str, contact_id: str
    ) -> dict[str, Any]:
        """Get one contact with all fields, tags and its linked company

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

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def tag_crm_contact(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        contact_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Tag one contact with a single free-form string, idempotent, returns the contact

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
        """Untag one contact, one tag per call, idempotent, returns the updated contact

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts/{contactId}/tags
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/tags"
        return await self._request(endpoint, method="DELETE", json=data)

    async def list_crm_contacts(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        company_id: str | None = None,
        status: str | None = None,
        source: str | None = None,
        title: str | None = None,
        department: str | None = None,
        email: str | None = None,
        email_subscribed: str | None = None,
        locale: str | None = None,
    ) -> dict[str, Any]:
        """List contacts in one CRM app, alphabetical by last name, search supported

        GET /organizations/{organizationId}/projects/{projectId}/apps/crm/{appId}/contacts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/crm/{quote(str(app_id), safe='')}/contacts"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "companyId": company_id,
            "status": status,
            "source": source,
            "title": title,
            "department": department,
            "email": email,
            "emailSubscribed": email_subscribed,
            "locale": locale,
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

    async def reply_to_chat_conversation(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        conversation_id: str,
        data: dict[str, Any],
    ) -> Any:
        """Reply into a chat conversation as a human operator

        POST /organizations/{organizationId}/projects/{projectId}/apps/chat/{appId}/conversations/{conversationId}/reply
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/chat/{quote(str(app_id), safe='')}/conversations/{quote(str(conversation_id), safe='')}/reply"
        return await self._request(endpoint, method="POST", json=data)

    async def take_over_chat_conversation(
        self, organization_id: str, project_id: str, app_id: str, conversation_id: str
    ) -> dict[str, Any]:
        """Take over a chat conversation from the AI

        POST /organizations/{organizationId}/projects/{projectId}/apps/chat/{appId}/conversations/{conversationId}/takeover
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/chat/{quote(str(app_id), safe='')}/conversations/{quote(str(conversation_id), safe='')}/takeover"
        return await self._request(endpoint, method="POST")

    async def release_chat_conversation(
        self, organization_id: str, project_id: str, app_id: str, conversation_id: str
    ) -> Any:
        """Release a chat conversation back to the AI

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/chat/{appId}/conversations/{conversationId}/takeover
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/chat/{quote(str(app_id), safe='')}/conversations/{quote(str(conversation_id), safe='')}/takeover"
        return await self._request(endpoint, method="DELETE")

    async def list_chat_conversations(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        visitor_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """List every visitor conversation in a chat app, most recently updated first

        GET /organizations/{organizationId}/projects/{projectId}/apps/chat/{appId}/conversations
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/chat/{quote(str(app_id), safe='')}/conversations"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "visitorId": visitor_id,
            "userId": user_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_chat_escalations(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        visitor_email: str | None = None,
    ) -> dict[str, Any]:
        """List every escalation in a chat app, newest first

        GET /organizations/{organizationId}/projects/{projectId}/apps/chat/{appId}/escalations
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/chat/{quote(str(app_id), safe='')}/escalations"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "visitorEmail": visitor_email,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ContentVersionsResource(BaseResource):
    """Content Versions API methods."""

    async def restore_content_version(
        self, organization_id: str, project_id: str, version_id: str
    ) -> dict[str, Any]:
        """Restore an entity to an older version; non-destructive, forward history is kept

        POST /organizations/{organizationId}/projects/{projectId}/content-versions/{versionId}/restore
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content-versions/{quote(str(version_id), safe='')}/restore"
        return await self._request(endpoint, method="POST")

    async def get_content_version(
        self, organization_id: str, project_id: str, version_id: str
    ) -> dict[str, Any]:
        """Get one version's full content snapshot, which the list tool omits

        GET /organizations/{organizationId}/projects/{projectId}/content-versions/{versionId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content-versions/{quote(str(version_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_content_versions(
        self,
        organization_id: str,
        project_id: str,
        content_type: str,
        content_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        source: str | None = None,
        created_by: str | None = None,
        version: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List one entity's edit history newest first; metadata only, no content snapshots

        GET /organizations/{organizationId}/projects/{projectId}/content-versions
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content-versions"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "source": source,
            "createdBy": created_by,
            "version": version,
            "createdAt": created_at,
            "contentType": content_type,
            "contentId": content_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class DevelopersResource(BaseResource):
    """Developers API methods."""

    async def get_developers_doc_category(
        self, organization_id: str, project_id: str, app_id: str, category_id: str
    ) -> dict[str, Any]:
        """Get one category's own fields; its docs come from listDevelopersDocs with categoryId

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/categories/{categoryId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/categories/{quote(str(category_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_developers_doc_category(
        self, organization_id: str, project_id: str, app_id: str, category_id: str
    ) -> dict[str, Any]:
        """Delete developer doc category

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/categories/{categoryId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/categories/{quote(str(category_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def update_developers_doc_category_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        category_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a category's name and description; cannot re-slug or re-parent it

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/categories/{categoryId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/categories/{quote(str(category_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def list_developers_doc_categories(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        slug: str | None = None,
        icon: str | None = None,
    ) -> dict[str, Any]:
        """List doc categories as a nested tree, sorted by display order

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/categories
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/categories"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "slug": slug,
            "icon": icon,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_developers_doc_category(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a doc category before the docs that reference it; slug must be unique

        POST /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/categories
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/categories"
        return await self._request(endpoint, method="POST", json=data)

    async def get_developers_doc(
        self, organization_id: str, project_id: str, app_id: str, doc_id: str
    ) -> dict[str, Any]:
        """Get one doc with its full content, SEO and category ids

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/docs/{docId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/docs/{quote(str(doc_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_developers_doc(
        self, organization_id: str, project_id: str, app_id: str, doc_id: str
    ) -> dict[str, Any]:
        """Delete developer doc

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/docs/{docId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/docs/{quote(str(doc_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def update_developers_doc_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        doc_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a doc's name, title, slug, SEO, excerpt, featured image and tags; cannot publish or edit content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/docs/{docId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/docs/{quote(str(doc_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def list_developers_docs(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        is_listed: str | None = None,
        category_id: str | None = None,
    ) -> dict[str, Any]:
        """List docs in a developer portal, newest first; pass lite=true to skip huge content

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/docs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/docs"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "isListed": is_listed,
            "categoryId": category_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_developers_doc(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a doc; slug must be unique, status defaults to draft, isListed to true

        POST /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/docs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/docs"
        return await self._request(endpoint, method="POST", json=data)

    async def update_developers_landing_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        data: dict[str, Any],
        locale: str | None = None,
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Update the landing page's SEO title, description and image; not its content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/landing
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/landing"
        params = {
            "locale": locale,
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="PATCH", json=data, params=params)

    async def get_developers_redirect(
        self, organization_id: str, project_id: str, app_id: str, redirect_id: str
    ) -> dict[str, Any]:
        """Get one URL redirect by id

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/redirects/{redirectId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/redirects/{quote(str(redirect_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_developers_redirects(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        source: str | None = None,
        status: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a developer portal's URL redirects, newest first, with from, to, status and source

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/redirects
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/redirects"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "source": source,
            "status": status,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_developers_sync_logs(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get the SDK and OpenAPI sync status and recent runs; diagnostic only, starts nothing

        GET /organizations/{organizationId}/projects/{projectId}/apps/developers/{appId}/sync-logs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/developers/{quote(str(app_id), safe='')}/sync-logs"
        return await self._request(endpoint, method="GET")


class DraftsResource(BaseResource):
    """Drafts API methods."""

    async def unarchive_draft(
        self, organization_id: str, project_id: str, draft_id: str
    ) -> dict[str, Any]:
        """Unarchive a draft back into the default list; already-unarchived is a no-op

        POST /organizations/{organizationId}/projects/{projectId}/mind/drafts/{draftId}/unarchive
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts/{quote(str(draft_id), safe='')}/unarchive"
        return await self._request(endpoint, method="POST")

    async def archive_draft(
        self, organization_id: str, project_id: str, draft_id: str
    ) -> dict[str, Any]:
        """Archive an accepted draft to hide it from the default list without deleting

        POST /organizations/{organizationId}/projects/{projectId}/mind/drafts/{draftId}/archive
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts/{quote(str(draft_id), safe='')}/archive"
        return await self._request(endpoint, method="POST")

    async def generate_edit_draft(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate AI edits to existing content; async, returns a pending draftId to poll

        POST /organizations/{organizationId}/projects/{projectId}/drafts/generate/edit
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/drafts/generate/edit"
        return await self._request(endpoint, method="POST", json=data)

    async def get_draft(
        self,
        organization_id: str,
        project_id: str,
        draft_id: str,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """Get one draft with its prompt, generated content and status; poll while pending

        GET /organizations/{organizationId}/projects/{projectId}/mind/drafts/{draftId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts/{quote(str(draft_id), safe='')}"
        params = {
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def delete_draft(
        self, organization_id: str, project_id: str, draft_id: str
    ) -> dict[str, Any]:
        """Delete a rejected, failed or cancelled draft permanently; other statuses return 409

        DELETE /organizations/{organizationId}/projects/{projectId}/mind/drafts/{draftId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts/{quote(str(draft_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def generate_new_draft(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate new content from a prompt; async, takes 5-15 minutes, nothing publishes yet

        POST /organizations/{organizationId}/projects/{projectId}/drafts/generate/new
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/drafts/generate/new"
        return await self._request(endpoint, method="POST", json=data)

    async def create_edit_draft(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a copy-on-write draft of existing content for manual editing, no AI

        POST /organizations/{organizationId}/projects/{projectId}/drafts/edit
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/drafts/edit"
        return await self._request(endpoint, method="POST", json=data)

    async def list_drafts(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        name: str | None = None,
        prompt: str | None = None,
        content_type: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        include_archived: str | None = None,
    ) -> dict[str, Any]:
        """List a project's drafts newest first; archived hidden unless includeArchived

        GET /organizations/{organizationId}/projects/{projectId}/mind/drafts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/drafts"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "name": name,
            "prompt": prompt,
            "contentType": content_type,
            "createdAt": created_at,
            "updatedAt": updated_at,
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
        """Get one contact's sent and planned emails with per-send opens and clicks

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/contacts/{contactId}/timeline
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/contacts/{quote(str(contact_id), safe='')}/timeline"
        return await self._request(endpoint, method="GET")

    async def get_email(
        self, organization_id: str, project_id: str, app_id: str, email_id: str
    ) -> dict[str, Any]:
        """Get one email with its full content blocks and header/footer links

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_email(
        self, organization_id: str, project_id: str, app_id: str, email_id: str
    ) -> dict[str, Any]:
        """Delete email

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def update_email_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        email_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an email's name, slug, subject and send-trigger sentence, not content or status

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

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
        """Unsubscribe a contact from one email; the row is kept for resubscribe

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}/recipients/{recipientId}/unsubscribe
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}/recipients/{quote(str(recipient_id), safe='')}/unsubscribe"
        return await self._request(endpoint, method="POST", json=data)

    async def list_email_recipients(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        email_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        contact_id: str | None = None,
        subscribed_at: str | None = None,
        unsubscribed_at: str | None = None,
    ) -> dict[str, Any]:
        """List one email's subscribers, including past unsubscribes, newest subscription first

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}/recipients
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}/recipients"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "contactId": contact_id,
            "subscribedAt": subscribed_at,
            "unsubscribedAt": unsubscribed_at,
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
        """Subscribe a CRM contact to one email; resubscribes if previously unsubscribed

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails/{emailId}/recipients
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails/{quote(str(email_id), safe='')}/recipients"
        return await self._request(endpoint, method="POST", json=data)

    async def list_emails(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        slug: str | None = None,
        name: str | None = None,
        header_id: str | None = None,
        footer_id: str | None = None,
    ) -> dict[str, Any]:
        """List emails in an email app, newest first; pass lite=true to skip content

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/emails
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/emails"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "slug": slug,
            "name": name,
            "headerId": header_id,
            "footerId": footer_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_email_footer(
        self, organization_id: str, project_id: str, app_id: str, footer_id: str
    ) -> dict[str, Any]:
        """Get one footer's block content in full; listEmailFooters lite=true returns metadata only

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/footers/{footerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/footers/{quote(str(footer_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_email_footer(
        self, organization_id: str, project_id: str, app_id: str, footer_id: str
    ) -> dict[str, Any]:
        """Delete email footer

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/footers/{footerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/footers/{quote(str(footer_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_email_footers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """List footers in an email app, newest first; pass lite=true to skip content

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/footers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/footers"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_email_footer(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a footer shell; only name is required, add blocks afterwards

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/footers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/footers"
        return await self._request(endpoint, method="POST", json=data)

    async def get_email_header(
        self, organization_id: str, project_id: str, app_id: str, header_id: str
    ) -> dict[str, Any]:
        """Get one header's full block tree; no lite mode, so expect heavy output

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/headers/{headerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/headers/{quote(str(header_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_email_header(
        self, organization_id: str, project_id: str, app_id: str, header_id: str
    ) -> dict[str, Any]:
        """Delete email header

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/headers/{headerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/headers/{quote(str(header_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_email_headers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List headers in an email app, newest first; pass lite=true to skip content

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/headers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/headers"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_email_header(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a header shell; only name is required, add blocks afterwards

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/headers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/headers"
        return await self._request(endpoint, method="POST", json=data)

    async def get_email_send(
        self, organization_id: str, project_id: str, app_id: str, send_id: str
    ) -> dict[str, Any]:
        """Get one send with its full delivery and engagement event log

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
        """Update a send to reschedule or cancel; only planned and queued rows accept edits

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/sends/{sendId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/sends/{quote(str(send_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def list_email_sends(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        email_id: str | None = None,
        contact_id: str | None = None,
        status: str | None = None,
        locale: str | None = None,
        recipient_email: str | None = None,
    ) -> dict[str, Any]:
        """List past, queued and planned sends across the app, filterable by email or contact

        GET /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/sends
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/sends"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "emailId": email_id,
            "contactId": contact_id,
            "status": status,
            "locale": locale,
            "recipientEmail": recipient_email,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_email_send(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a send for one contact; defaults to planned, which sends nothing until queued

        POST /organizations/{organizationId}/projects/{projectId}/apps/email/{appId}/sends
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/email/{quote(str(app_id), safe='')}/sends"
        return await self._request(endpoint, method="POST", json=data)


class FeatureRequestsResource(BaseResource):
    """Feature Requests API methods."""

    async def list_popular_feature_requests(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        vote_count: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List everyone's feature requests ranked by votes, showing whether you voted

        GET /me/feature-requests/popular
        """
        endpoint = "/me/feature-requests/popular"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "priority": priority,
            "voteCount": vote_count,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_my_feature_requests(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        source: str | None = None,
        vote_count: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List feature requests you filed, with status, vote count and GitHub issue link

        GET /me/feature-requests
        """
        endpoint = "/me/feature-requests"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "priority": priority,
            "source": source,
            "voteCount": vote_count,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_feature_request_comments(
        self,
        feature_request_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        author: str | None = None,
        source: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List comments for a feature request

        GET /me/feature-requests/{featureRequestId}/comments
        """
        endpoint = (
            f"/me/feature-requests/{quote(str(feature_request_id), safe='')}/comments"
        )
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "author": author,
            "source": source,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class FormsResource(BaseResource):
    """Forms API methods."""

    async def get_form(
        self, organization_id: str, project_id: str, app_id: str, form_id: str
    ) -> dict[str, Any]:
        """Get one form's fields, settings and content blocks in Builder format

        GET /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms/{formId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms/{quote(str(form_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_form(
        self, organization_id: str, project_id: str, app_id: str, form_id: str
    ) -> dict[str, Any]:
        """Delete form

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms/{formId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms/{quote(str(form_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def update_form_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        form_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a form's name and description; cannot re-slug it or change fields

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms/{formId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms/{quote(str(form_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def get_form_submission(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        form_id: str,
        submission_id: str,
    ) -> dict[str, Any]:
        """Get one submission's full answers plus its user agent, IP and referer

        GET /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms/{formId}/submissions/{submissionId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms/{quote(str(form_id), safe='')}/submissions/{quote(str(submission_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_form_submissions(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        form_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List one form's submissions, newest first, with submitted data and metadata

        GET /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms/{formId}/submissions
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms/{quote(str(form_id), safe='')}/submissions"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_forms(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        slug: str | None = None,
        is_active: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List forms in a Forms app with their fields and submission counts, newest first

        GET /organizations/{organizationId}/projects/{projectId}/apps/forms/{appId}/forms
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/forms/{quote(str(app_id), safe='')}/forms"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "slug": slug,
            "isActive": is_active,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class HealthResource(BaseResource):
    """Health API methods."""

    async def get_health_echo(self) -> dict[str, Any]:
        """Get a unique LLM-generated message, proving the AI pipeline is live

        GET /health/echo
        """
        endpoint = "/health/echo"
        return await self._request(endpoint, method="GET")


class IdeasResource(BaseResource):
    """Ideas API methods."""

    async def approve_idea(
        self, organization_id: str, project_id: str, idea_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Approve a pending idea to start content generation; a draft may follow automatically

        POST /organizations/{organizationId}/projects/{projectId}/mind/ideas/{ideaId}/approve
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas/{quote(str(idea_id), safe='')}/approve"
        return await self._request(endpoint, method="POST", json=data)

    async def dismiss_idea(
        self, organization_id: str, project_id: str, idea_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Dismiss a pending idea with an optional reason so Mind stops suggesting it

        POST /organizations/{organizationId}/projects/{projectId}/mind/ideas/{ideaId}/dismiss
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas/{quote(str(idea_id), safe='')}/dismiss"
        return await self._request(endpoint, method="POST", json=data)

    async def get_idea(
        self, organization_id: str, project_id: str, idea_id: str
    ) -> dict[str, Any]:
        """Get one idea's rationale, outline and similarity score before approving or dismissing

        GET /organizations/{organizationId}/projects/{projectId}/mind/ideas/{ideaId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas/{quote(str(idea_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_ideas(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        app_id: str | None = None,
        content_type: str | None = None,
        target_content_type: str | None = None,
        operation_key: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List Mind ideas for a project

        GET /organizations/{organizationId}/projects/{projectId}/mind/ideas
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "priority": priority,
            "appId": app_id,
            "contentType": content_type,
            "targetContentType": target_content_type,
            "operationKey": operation_key,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def trigger_ideation(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> Any:
        """Trigger Mind ideation for a project

        POST /organizations/{organizationId}/projects/{projectId}/mind/ideas
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/mind/ideas"
        return await self._request(endpoint, method="POST", json=data)


class InvitationsResource(BaseResource):
    """Invitations API methods."""

    async def get_organization_invitation(
        self, organization_id: str, invitation_id: str
    ) -> dict[str, Any]:
        """Get an invitation by ID

        GET /organizations/{organizationId}/invitations/{invitationId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/invitations/{quote(str(invitation_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_organization_invitations(
        self,
        organization_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        role: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        """List invitations sent by an organization: pending, accepted and expired, with role

        GET /organizations/{organizationId}/invitations
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/invitations"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "role": role,
            "email": email,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class KBResource(BaseResource):
    """KB API methods."""

    async def get_kb_article(
        self, organization_id: str, project_id: str, app_id: str, article_id: str
    ) -> dict[str, Any]:
        """Get one article including its full content tree, status, SEO and category ids

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/articles/{articleId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/articles/{quote(str(article_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_kb_article(
        self, organization_id: str, project_id: str, app_id: str, article_id: str
    ) -> dict[str, Any]:
        """Delete KB article

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/articles/{articleId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/articles/{quote(str(article_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def update_kb_article_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        article_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an article's name, title, slug, SEO fields, excerpt, tags and featured image; cannot publish or edit content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/articles/{articleId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/articles/{quote(str(article_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def list_kb_articles(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        slug: str | None = None,
        status: str | None = None,
        is_listed: str | None = None,
        category_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        published_at: str | None = None,
    ) -> dict[str, Any]:
        """List articles in one KB app, newest first; pass lite=true to omit huge content

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/articles
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/articles"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "slug": slug,
            "status": status,
            "isListed": is_listed,
            "categoryId": category_id,
            "createdAt": created_at,
            "updatedAt": updated_at,
            "publishedAt": published_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_kb_article(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create an article shell; publishing with content also ingests it for AI chat

        POST /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/articles
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/articles"
        return await self._request(endpoint, method="POST", json=data)

    async def get_kb_category(
        self, organization_id: str, project_id: str, app_id: str, category_id: str
    ) -> dict[str, Any]:
        """Get one category's name, slug, description, parent and order; not its articles

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/categories/{categoryId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/categories/{quote(str(category_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_kb_category(
        self, organization_id: str, project_id: str, app_id: str, category_id: str
    ) -> dict[str, Any]:
        """Delete KB category

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/categories/{categoryId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/categories/{quote(str(category_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def update_kb_category_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        category_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a category's name and description; cannot re-slug, reorder or re-parent it

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/categories/{categoryId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/categories/{quote(str(category_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def list_kb_categories(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        slug: str | None = None,
        icon: str | None = None,
    ) -> dict[str, Any]:
        """List a KB app's categories as a nested parent-child tree, roots paginated

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/categories
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/categories"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "slug": slug,
            "icon": icon,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_kb_category(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a category, optionally nested under a parent; order assigned automatically

        POST /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/categories
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/categories"
        return await self._request(endpoint, method="POST", json=data)

    async def update_kb_landing_meta(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update knowledge base landing page metadata

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/landing
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/landing"
        return await self._request(endpoint, method="PATCH", json=data)

    async def get_kb_redirect(
        self, organization_id: str, project_id: str, app_id: str, redirect_id: str
    ) -> dict[str, Any]:
        """Get one URL redirect by id

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/redirects/{redirectId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/redirects/{quote(str(redirect_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_kb_redirects(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        source: str | None = None,
        status: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a knowledge base's URL redirects, newest first, with from, to, status and source

        GET /organizations/{organizationId}/projects/{projectId}/apps/kb/{appId}/redirects
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/kb/{quote(str(app_id), safe='')}/redirects"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "source": source,
            "status": status,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class MeResource(BaseResource):
    """Me API methods."""

    async def list_my_suspension_messages(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        author_type: str | None = None,
        author_id: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List your suspension appeal thread, both your messages and admin replies

        GET /me/suspension-messages
        """
        endpoint = "/me/suspension-messages"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "authorType": author_type,
            "authorId": author_id,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_my_notifications(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        type: str | None = None,
    ) -> dict[str, Any]:
        """List the caller's notifications, filterable by read status and type

        GET /me/notifications
        """
        endpoint = "/me/notifications"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "type": type,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_my_organizations(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        slug: str | None = None,
        plan: str | None = None,
        subscription_status: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List organizations you belong to and your role in each

        GET /me/organizations
        """
        endpoint = "/me/organizations"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "slug": slug,
            "plan": plan,
            "subscriptionStatus": subscription_status,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_my_invitations(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        role: str | None = None,
    ) -> dict[str, Any]:
        """List pending org invitations addressed to the caller's email, with offered role

        GET /me/invitations
        """
        endpoint = "/me/invitations"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "role": role,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_my_activities(
        self,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> dict[str, Any]:
        """List activity by or affecting you, with the resource each touched, paginated

        GET /me/activities
        """
        endpoint = "/me/activities"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "action": action,
            "resourceType": resource_type,
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

    async def list_member_project_memberships(
        self,
        organization_id: str,
        member_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        role: str | None = None,
        joined_at: str | None = None,
    ) -> dict[str, Any]:
        """List all organization projects with one member's access level, null where none

        GET /organizations/{organizationId}/members/{memberId}/project-memberships
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/members/{quote(str(member_id), safe='')}/project-memberships"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "role": role,
            "joinedAt": joined_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_member_app_memberships(
        self,
        organization_id: str,
        member_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        app_type: str | None = None,
        role: str | None = None,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        """List every app with one member's role; project roles do not grant app access

        GET /organizations/{organizationId}/members/{memberId}/app-memberships
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/members/{quote(str(member_id), safe='')}/app-memberships"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "appType": app_type,
            "role": role,
            "projectId": project_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_organization_member_activities(
        self,
        organization_id: str,
        member_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> dict[str, Any]:
        """Get member activities

        GET /organizations/{organizationId}/members/{memberId}/activities
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/members/{quote(str(member_id), safe='')}/activities"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "action": action,
            "resourceType": resource_type,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_organization_member(
        self, organization_id: str, member_id: str
    ) -> dict[str, Any]:
        """Get one member's profile, role, title and join date by member UUID

        GET /organizations/{organizationId}/members/{memberId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/members/{quote(str(member_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_organization_members(
        self,
        organization_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        role: str | None = None,
        title: str | None = None,
        user_id: str | None = None,
        invited_by: str | None = None,
        joined_at: str | None = None,
        invited_at: str | None = None,
    ) -> dict[str, Any]:
        """List members of an organization with their roles, paginated and searchable

        GET /organizations/{organizationId}/members
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/members"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "role": role,
            "title": title,
            "userId": user_id,
            "invitedBy": invited_by,
            "joinedAt": joined_at,
            "invitedAt": invited_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class OrganizationsResource(BaseResource):
    """Organizations API methods."""

    async def get_service_account(
        self, organization_id: str, account_id: str
    ) -> dict[str, Any]:
        """Get a service account

        GET /organizations/{organizationId}/service-accounts/{accountId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/service-accounts/{quote(str(account_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_service_accounts(
        self,
        organization_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        email: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """List an organization's service accounts, newest first

        GET /organizations/{organizationId}/service-accounts
        """
        endpoint = (
            f"/organizations/{quote(str(organization_id), safe='')}/service-accounts"
        )
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "email": email,
            "createdAt": created_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_organization(self, organization_id: str) -> dict[str, Any]:
        """Get one organization's name, slug, plan, status and member count by ID

        GET /organizations/{organizationId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_organization_by_slug(self, slug: str) -> dict[str, Any]:
        """Get an organization from a URL slug when you have no ID

        GET /organizations/by-slug/{slug}
        """
        endpoint = f"/organizations/by-slug/{quote(str(slug), safe='')}"
        return await self._request(endpoint, method="GET")


class ProjectAppsResource(BaseResource):
    """Project Apps API methods."""

    async def get_project_app_by_slug(
        self, organization_id: str, project_id: str, app_slug: str
    ) -> dict[str, Any]:
        """Get a project app by slug

        GET /organizations/{organizationId}/projects/{projectId}/apps/by-slug/{appSlug}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/by-slug/{quote(str(app_slug), safe='')}"
        return await self._request(endpoint, method="GET")

    async def get_app_settings(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Read one app's settings, whatever kind of app it is

        GET /organizations/{organizationId}/projects/{projectId}/apps/{appId}/settings
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/{quote(str(app_id), safe='')}/settings"
        return await self._request(endpoint, method="GET")

    async def update_app_settings(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Change one app's settings, merging into what is already there

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/{appId}/settings
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/{quote(str(app_id), safe='')}/settings"
        return await self._request(endpoint, method="PATCH", json=data)

    async def get_project_app(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get a project app by ID

        GET /organizations/{organizationId}/projects/{projectId}/apps/{appId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/{quote(str(app_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_deleted_project_apps(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        slug: str | None = None,
        app_type: str | None = None,
        is_active: str | None = None,
    ) -> dict[str, Any]:
        """List soft-deleted apps in a project's trash, restorable or permanently deletable

        GET /organizations/{organizationId}/projects/{projectId}/apps/trash
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/trash"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "slug": slug,
            "appType": app_type,
            "isActive": is_active,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_project_apps(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        slug: str | None = None,
        app_type: str | None = None,
        is_active: str | None = None,
    ) -> dict[str, Any]:
        """List a project's active apps and their types to obtain the appId

        GET /organizations/{organizationId}/projects/{projectId}/apps
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "slug": slug,
            "appType": app_type,
            "isActive": is_active,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ProjectBrandingResource(BaseResource):
    """Project Branding API methods."""

    async def get_project_branding(
        self, organization_id: str, project_id: str, branding_id: str
    ) -> dict[str, Any]:
        """Get one branding profile's colors, fonts, logos and favicon

        GET /organizations/{organizationId}/projects/{projectId}/brandings/{brandingId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/brandings/{quote(str(branding_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_project_brandings(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        created_by: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a project's named branding profiles: colors, fonts, logos, favicon

        GET /organizations/{organizationId}/projects/{projectId}/brandings
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/brandings"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "createdBy": created_by,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ProjectDomainsResource(BaseResource):
    """Project Domains API methods."""

    async def get_domain_verification_instructions(
        self, organization_id: str, project_id: str, domain_id: str
    ) -> dict[str, Any]:
        """Get the exact DNS record the owner must add to verify a domain

        GET /organizations/{organizationId}/projects/{projectId}/domains/{domainId}/verification
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/domains/{quote(str(domain_id), safe='')}/verification"
        return await self._request(endpoint, method="GET")

    async def list_project_domains(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        app_id: str | None = None,
        app_type: str | None = None,
        hostname: str | None = None,
        is_generated: str | None = None,
        is_primary: str | None = None,
        is_verified: str | None = None,
        verification_status: str | None = None,
    ) -> dict[str, Any]:
        """List a project's manageable domains with verification status and owning app

        GET /organizations/{organizationId}/projects/{projectId}/domains
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/domains"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "appId": app_id,
            "appType": app_type,
            "hostname": hostname,
            "isGenerated": is_generated,
            "isPrimary": is_primary,
            "isVerified": is_verified,
            "verificationStatus": verification_status,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ProjectFilesResource(BaseResource):
    """Project Files API methods."""

    async def restore_file_trash_item(
        self, organization_id: str, project_id: str, item_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Restore an item from trash

        POST /organizations/{organizationId}/projects/{projectId}/files/trash/{itemId}/restore
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/trash/{quote(str(item_id), safe='')}/restore"
        return await self._request(endpoint, method="POST", json=data)

    async def list_file_references(
        self,
        organization_id: str,
        project_id: str,
        file_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        type: str | None = None,
        id: str | None = None,
    ) -> dict[str, Any]:
        """List places where a file is referenced

        GET /organizations/{organizationId}/projects/{projectId}/files/{fileId}/references
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}/references"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "type": type,
            "id": id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_file_folder(
        self, organization_id: str, project_id: str, folder_id: str
    ) -> dict[str, Any]:
        """Get one folder's name and parent; use listFiles with folderId to see its files

        GET /organizations/{organizationId}/projects/{projectId}/files/folders/{folderId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/folders/{quote(str(folder_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_file_folder(
        self, organization_id: str, project_id: str, folder_id: str
    ) -> dict[str, Any]:
        """Delete a file folder (files are moved to root)

        DELETE /organizations/{organizationId}/projects/{projectId}/files/folders/{folderId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/folders/{quote(str(folder_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def replace_file_content(
        self, organization_id: str, project_id: str, file_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Replace a text file's content in place; id, URL and references stay unchanged

        PUT /organizations/{organizationId}/projects/{projectId}/files/{fileId}/content
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}/content"
        return await self._request(endpoint, method="PUT", json=data)

    async def permanent_delete_file_trash_item(
        self, organization_id: str, project_id: str, item_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Permanently delete an item from trash

        DELETE /organizations/{organizationId}/projects/{projectId}/files/trash/{itemId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/trash/{quote(str(item_id), safe='')}"
        return await self._request(endpoint, method="DELETE", json=data)

    async def open_file(
        self, organization_id: str, project_id: str, file_id: str
    ) -> dict[str, Any]:
        """Open a file's content inline: text as string, images as base64, 10 MB cap

        GET /organizations/{organizationId}/projects/{projectId}/files/{fileId}/open
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}/open"
        return await self._request(endpoint, method="GET")

    async def empty_file_trash(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Empty trash (permanently delete old items)

        POST /organizations/{organizationId}/projects/{projectId}/files/trash/empty
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/trash/empty"
        return await self._request(endpoint, method="POST", json=data)

    async def get_file(
        self, organization_id: str, project_id: str, file_id: str
    ) -> dict[str, Any]:
        """Get one file's metadata only (URL, type, size, folder); openFile returns the content

        GET /organizations/{organizationId}/projects/{projectId}/files/{fileId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_file(
        self, organization_id: str, project_id: str, file_id: str
    ) -> dict[str, Any]:
        """Delete a file

        DELETE /organizations/{organizationId}/projects/{projectId}/files/{fileId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/{quote(str(file_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_file_folders(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        parent_id: str | None = None,
        name: str | None = None,
        created_by: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List file folders in a project

        GET /organizations/{organizationId}/projects/{projectId}/files/folders
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/folders"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "parentId": parent_id,
            "name": name,
            "createdBy": created_by,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def search_files(
        self,
        organization_id: str,
        project_id: str,
        query: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        mime_type: str | None = None,
        similarity: str | None = None,
        filename: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Search file contents by meaning; returns matching snippet and relevance score per file

        GET /organizations/{organizationId}/projects/{projectId}/files/search
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/search"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "mimeType": mime_type,
            "similarity": similarity,
            "filename": filename,
            "query": query,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_file_trash(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        type: str | None = None,
        mime_type: str | None = None,
        parent_id: str | None = None,
        deleted_by: str | None = None,
        deleted_at: str | None = None,
    ) -> dict[str, Any]:
        """List a project's trashed files and folders, restorable until permanently deleted

        GET /organizations/{organizationId}/projects/{projectId}/files/trash
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/trash"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "type": type,
            "mimeType": mime_type,
            "parentId": parent_id,
            "deletedBy": deleted_by,
            "deletedAt": deleted_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def save_file(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Save a file from text or image content

        POST /organizations/{organizationId}/projects/{projectId}/files/save
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files/save"
        return await self._request(endpoint, method="POST", json=data)

    async def list_files(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        is_public: str | None = None,
        grounding: str | None = None,
        mime_type: str | None = None,
        folder_id: str | None = None,
    ) -> dict[str, Any]:
        """List a project's files, with search, filtering and sorting

        GET /organizations/{organizationId}/projects/{projectId}/files
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/files"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "isPublic": is_public,
            "grounding": grounding,
            "mimeType": mime_type,
            "folderId": folder_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ProjectLegalDocumentsResource(BaseResource):
    """Project Legal Documents API methods."""

    async def publish_project_legal_document(
        self, organization_id: str, project_id: str, document_id: str
    ) -> dict[str, Any]:
        """Publish a draft project legal document

        POST /organizations/{organizationId}/projects/{projectId}/legal/{documentId}/publish
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/legal/{quote(str(document_id), safe='')}/publish"
        return await self._request(endpoint, method="POST")

    async def get_project_legal_document(
        self, organization_id: str, project_id: str, document_id: str
    ) -> dict[str, Any]:
        """Get a project legal document by ID

        GET /organizations/{organizationId}/projects/{projectId}/legal/{documentId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/legal/{quote(str(document_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def update_project_legal_document(
        self,
        organization_id: str,
        project_id: str,
        document_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a draft project legal document

        PATCH /organizations/{organizationId}/projects/{projectId}/legal/{documentId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/legal/{quote(str(document_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def list_project_legal_documents(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        type: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """List a project's legal document versions across all types, draft and published

        GET /organizations/{organizationId}/projects/{projectId}/legal
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/legal"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "type": type,
            "status": status,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_project_legal_document(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a new draft project legal document

        POST /organizations/{organizationId}/projects/{projectId}/legal
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/legal"
        return await self._request(endpoint, method="POST", json=data)


class ProjectMembersResource(BaseResource):
    """Project Members API methods."""

    async def get_project_member(
        self, organization_id: str, project_id: str, member_id: str
    ) -> dict[str, Any]:
        """Get a project member by ID

        GET /organizations/{organizationId}/projects/{projectId}/members/{memberId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/members/{quote(str(member_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_project_members(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        role: str | None = None,
        title: str | None = None,
        user_id: str | None = None,
        joined_at: str | None = None,
    ) -> dict[str, Any]:
        """List users added to a project with their roles

        GET /organizations/{organizationId}/projects/{projectId}/members
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/members"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "role": role,
            "title": title,
            "userId": user_id,
            "joinedAt": joined_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class ProjectTrashResource(BaseResource):
    """Project Trash API methods."""

    async def restore_project_trash_batch(
        self, organization_id: str, project_id: str, batch_id: str
    ) -> dict[str, Any]:
        """Restore a trash batch

        POST /organizations/{organizationId}/projects/{projectId}/trash/batches/{batchId}/restore
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/trash/batches/{quote(str(batch_id), safe='')}/restore"
        return await self._request(endpoint, method="POST")

    async def restore_project_trash_item(
        self, organization_id: str, project_id: str, trash_id: str
    ) -> dict[str, Any]:
        """Restore an item from trash

        POST /organizations/{organizationId}/projects/{projectId}/trash/{trashId}/restore
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/trash/{quote(str(trash_id), safe='')}/restore"
        return await self._request(endpoint, method="POST")

    async def get_project_trash_item(
        self, organization_id: str, project_id: str, trash_id: str
    ) -> dict[str, Any]:
        """Get one trashed item's entity type, deletion metadata and stored data snapshot

        GET /organizations/{organizationId}/projects/{projectId}/trash/{trashId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/trash/{quote(str(trash_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def permanent_delete_project_trash_item(
        self, organization_id: str, project_id: str, trash_id: str
    ) -> dict[str, Any]:
        """Permanently delete an item from trash

        DELETE /organizations/{organizationId}/projects/{projectId}/trash/{trashId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/trash/{quote(str(trash_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_project_trash(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        entity_type: str | None = None,
    ) -> dict[str, Any]:
        """List soft-deleted items across a whole project, filterable by entity type

        GET /organizations/{organizationId}/projects/{projectId}/trash
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/trash"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "entityType": entity_type,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def empty_project_trash(
        self, organization_id: str, project_id: str
    ) -> dict[str, Any]:
        """Empty all items from trash

        DELETE /organizations/{organizationId}/projects/{projectId}/trash
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/trash"
        return await self._request(endpoint, method="DELETE")


class ProjectWorkflowsResource(BaseResource):
    """Project Workflows API methods."""

    async def get_workflow_run(
        self, organization_id: str, project_id: str, run_id: str
    ) -> dict[str, Any]:
        """Get a workflow run and its tasks

        GET /organizations/{organizationId}/projects/{projectId}/workflows/runs/{runId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/workflows/runs/{quote(str(run_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def dismiss_workflow_run(
        self, organization_id: str, project_id: str, run_id: str
    ) -> dict[str, Any]:
        """Dismiss a workflow run

        DELETE /organizations/{organizationId}/projects/{projectId}/workflows/runs/{runId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/workflows/runs/{quote(str(run_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_workflow_runs(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        type: str | None = None,
        created_at: str | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
        include_dismissed: str | None = None,
    ) -> dict[str, Any]:
        """List workflow runs

        GET /organizations/{organizationId}/projects/{projectId}/workflows/runs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/workflows/runs"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "type": type,
            "createdAt": created_at,
            "startedAt": started_at,
            "completedAt": completed_at,
            "includeDismissed": include_dismissed,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_workflow_run(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> Any:
        """Start a workflow run

        POST /organizations/{organizationId}/projects/{projectId}/workflows/runs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/workflows/runs"
        return await self._request(endpoint, method="POST", json=data)


class ProjectsResource(BaseResource):
    """Projects API methods."""

    async def get_project_by_slug(
        self, organization_id: str, project_slug: str
    ) -> dict[str, Any]:
        """Get one project from its URL slug, same object as the by-ID lookup

        GET /organizations/{organizationId}/projects/by-slug/{projectSlug}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/by-slug/{quote(str(project_slug), safe='')}"
        return await self._request(endpoint, method="GET")

    async def search_sources(
        self,
        organization_id: str,
        project_id: str,
        query: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
        similarity: str | None = None,
        limit: str | None = None,
        source_types: str | None = None,
    ) -> dict[str, Any]:
        """Search project material by meaning, not literal text; returns ranked cited excerpts

        GET /organizations/{organizationId}/projects/{projectId}/search
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/search"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "sourceType": source_type,
            "sourceId": source_id,
            "similarity": similarity,
            "query": query,
            "limit": limit,
            "sourceTypes": source_types,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def list_project_urls(
        self,
        organization_id: str,
        project_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        app: str | None = None,
        type: str | None = None,
        id: str | None = None,
        path: str | None = None,
    ) -> dict[str, Any]:
        """List resolved paths for all published content, for building links and menus

        GET /organizations/{organizationId}/projects/{projectId}/urls
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/urls"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "app": app,
            "type": type,
            "id": id,
            "path": path,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_project(
        self, organization_id: str, project_id: str
    ) -> dict[str, Any]:
        """Get one project's name, slug, description and settings within an organization

        GET /organizations/{organizationId}/projects/{projectId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_projects(
        self,
        organization_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        slug: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List projects in an organization; the IDs every project-level tool needs

        GET /organizations/{organizationId}/projects
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "slug": slug,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)


class WebsiteResource(BaseResource):
    """Website API methods."""

    async def submit_content_to_search_engines(
        self, organization_id: str, project_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Ask the search engines to recrawl a page, post, article or doc now

        POST /organizations/{organizationId}/projects/{projectId}/content/search-index
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/content/search-index"
        return await self._request(endpoint, method="POST", json=data)

    async def get_website_blog_page(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the one seeded blog archive page; no create call exists

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/blog-page
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/blog-page"
        params = {
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def update_website_blog_page_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        data: dict[str, Any],
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Update the blog archive page's name and SEO fields; cannot publish or edit content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/blog-page
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/blog-page"
        params = {
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="PATCH", json=data, params=params)

    async def get_website_consent_settings(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get the cookie banner copy, category toggles and policy links

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/consent
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/consent"
        return await self._request(endpoint, method="GET")

    async def get_website_dialog(
        self, organization_id: str, project_id: str, app_id: str, dialog_id: str
    ) -> dict[str, Any]:
        """Get one dialog with its full block tree, max width and close control

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/dialogs/{dialogId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/dialogs/{quote(str(dialog_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_website_dialog(
        self, organization_id: str, project_id: str, app_id: str, dialog_id: str
    ) -> dict[str, Any]:
        """Delete dialog

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/dialogs/{dialogId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/dialogs/{quote(str(dialog_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_website_dialogs(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        max_width: str | None = None,
        include_close: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List popup dialogs (modals, banners, slide-ins) in a site, newest first

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/dialogs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/dialogs"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "maxWidth": max_width,
            "includeClose": include_close,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_website_dialog(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a popup dialog; nothing shows it until a button links dialog:{id}

        POST /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/dialogs
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/dialogs"
        return await self._request(endpoint, method="POST", json=data)

    async def get_website_custom_domain(
        self, organization_id: str, project_id: str, app_id: str, domain_id: str
    ) -> dict[str, Any]:
        """Get one domain with its verification token, verified state and primary flag

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/domains/{domainId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/domains/{quote(str(domain_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_website_custom_domains(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        is_primary: str | None = None,
        is_verified: str | None = None,
        is_generated: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a site's custom domains, primary first, with verified state and verification token

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/domains
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/domains"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "isPrimary": is_primary,
            "isVerified": is_verified,
            "isGenerated": is_generated,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_footer(
        self, organization_id: str, project_id: str, app_id: str, footer_id: str
    ) -> dict[str, Any]:
        """Get one footer with its full block tree, which lite listings omit

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/footers/{footerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/footers/{quote(str(footer_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_website_footer(
        self, organization_id: str, project_id: str, app_id: str, footer_id: str
    ) -> dict[str, Any]:
        """Delete website footer

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/footers/{footerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/footers/{quote(str(footer_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_website_footers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a site's footers newest first, each with its block tree unless lite

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/footers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/footers"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_website_footer(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a reusable footer shell; pages attach it by id, content optional

        POST /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/footers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/footers"
        return await self._request(endpoint, method="POST", json=data)

    async def get_website_header(
        self, organization_id: str, project_id: str, app_id: str, header_id: str
    ) -> dict[str, Any]:
        """Get one header with its full block tree, which lite listings omit

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/headers/{headerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/headers/{quote(str(header_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_website_header(
        self, organization_id: str, project_id: str, app_id: str, header_id: str
    ) -> dict[str, Any]:
        """Delete website header

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/headers/{headerId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/headers/{quote(str(header_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_website_headers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a site's headers newest first, each with its block tree unless lite

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/headers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/headers"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_website_header(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a reusable header shell; pages attach it by id, content optional

        POST /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/headers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/headers"
        return await self._request(endpoint, method="POST", json=data)

    async def get_website_landing(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the one seeded page at the site root; no create call exists

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/landing
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/landing"
        params = {
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def update_website_landing_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        data: dict[str, Any],
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Update the landing page's name and SEO fields; cannot publish or edit content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/landing
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/landing"
        params = {
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="PATCH", json=data, params=params)

    async def get_website_layout(
        self, organization_id: str, project_id: str, app_id: str, layout_id: str
    ) -> dict[str, Any]:
        """Get one layout with its full block tree, which lite listings omit

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/layouts/{layoutId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/layouts/{quote(str(layout_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_website_layout(
        self, organization_id: str, project_id: str, app_id: str, layout_id: str
    ) -> dict[str, Any]:
        """Delete website layout

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/layouts/{layoutId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/layouts/{quote(str(layout_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_website_layouts(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List page layouts you can apply when creating a page, newest first

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/layouts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/layouts"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_website_layout(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a layout shell; pages set layoutId to share its block tree

        POST /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/layouts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/layouts"
        return await self._request(endpoint, method="POST", json=data)

    async def get_website_not_found_page(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the one seeded not found page; no create call exists

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/not-found-page
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/not-found-page"
        params = {
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def update_website_not_found_page_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        data: dict[str, Any],
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Update the not found page's name and SEO fields; cannot publish or edit content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/not-found-page
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/not-found-page"
        params = {
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="PATCH", json=data, params=params)

    async def get_website_page(
        self, organization_id: str, project_id: str, app_id: str, page_id: str
    ) -> dict[str, Any]:
        """Get one page with its full block tree, SEO, status and layout ids

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/pages/{pageId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/pages/{quote(str(page_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_website_page(
        self, organization_id: str, project_id: str, app_id: str, page_id: str
    ) -> dict[str, Any]:
        """Delete website page

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/pages/{pageId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/pages/{quote(str(page_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def update_website_page_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a page's name, title, slug, SEO fields, featured image and tags; cannot publish or edit content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/pages/{pageId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/pages/{quote(str(page_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def list_website_pages(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        slug: str | None = None,
        is_listed: str | None = None,
        layout_id: str | None = None,
        header_id: str | None = None,
        footer_id: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a site's pages with slug, live URL and publish status, newest first

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/pages
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/pages"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "slug": slug,
            "isListed": is_listed,
            "layoutId": layout_id,
            "headerId": header_id,
            "footerId": footer_id,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_website_page(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a page shell; content optional and status defaults to published, live immediately

        POST /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/pages
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/pages"
        return await self._request(endpoint, method="POST", json=data)

    async def get_website_post(
        self, organization_id: str, project_id: str, app_id: str, post_id: str
    ) -> dict[str, Any]:
        """Get one blog post with its full content blocks, tags and SEO fields

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/posts/{postId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/posts/{quote(str(post_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_website_post(
        self, organization_id: str, project_id: str, app_id: str, post_id: str
    ) -> dict[str, Any]:
        """Delete blog post

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/posts/{postId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/posts/{quote(str(post_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def update_website_post_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        post_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a post's name, title, slug, excerpt, author, publish date, tags and SEO, not its content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/posts/{postId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/posts/{quote(str(post_id), safe='')}"
        return await self._request(endpoint, method="PATCH", json=data)

    async def list_website_posts(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        status: str | None = None,
        slug: str | None = None,
        is_listed: str | None = None,
        author_id: str | None = None,
        author_name: str | None = None,
        publish_date: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List blog posts in a site, newest first, with author, tags and status

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/posts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/posts"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "status": status,
            "slug": slug,
            "isListed": is_listed,
            "authorId": author_id,
            "authorName": author_name,
            "publishDate": publish_date,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_website_post(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a blog post; status defaults to draft, unlike createWebsitePage

        POST /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/posts
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/posts"
        return await self._request(endpoint, method="POST", json=data)

    async def get_website_redirect(
        self, organization_id: str, project_id: str, app_id: str, redirect_id: str
    ) -> dict[str, Any]:
        """Get one URL redirect by id

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/redirects/{redirectId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/redirects/{quote(str(redirect_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def list_website_redirects(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        source: str | None = None,
        status: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a site's URL redirects, newest first, with from, to, status and source

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/redirects
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/redirects"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "source": source,
            "status": status,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_sidebar(
        self, organization_id: str, project_id: str, app_id: str, sidebar_id: str
    ) -> dict[str, Any]:
        """Get one sidebar with its full block tree, which lite listings omit

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/sidebars/{sidebarId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/sidebars/{quote(str(sidebar_id), safe='')}"
        return await self._request(endpoint, method="GET")

    async def delete_website_sidebar(
        self, organization_id: str, project_id: str, app_id: str, sidebar_id: str
    ) -> dict[str, Any]:
        """Delete website sidebar

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/sidebars/{sidebarId}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/sidebars/{quote(str(sidebar_id), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_website_sidebars(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        name: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> dict[str, Any]:
        """List a site's sidebars newest first, each with its block tree unless lite

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/sidebars
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/sidebars"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "name": name,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def create_website_sidebar(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> Any:
        """Create a reusable sidebar shell; a layoutSidebar block points at it by id

        POST /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/sidebars
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/sidebars"
        return await self._request(endpoint, method="POST", json=data)

    async def get_website_sign_in_page(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the one seeded not found page; no create call exists

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/sign-in-page
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/sign-in-page"
        params = {
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def update_website_sign_in_page_meta(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        data: dict[str, Any],
        draft_id: str | None = None,
    ) -> dict[str, Any]:
        """Update the not found page's name and SEO fields; cannot publish or edit content

        PATCH /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/sign-in-page
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/sign-in-page"
        params = {
            "draftId": draft_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="PATCH", json=data, params=params)

    async def list_website_tags(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
        sort: str | None = None,
        search: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """List the tag names in use across a site's pages and posts

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/tags
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/tags"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
            "sort": sort,
            "search": search,
            "tag": tag,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def get_website_tracking_settings(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get the site's Google Tag Manager container ID, the only tracking setting

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/tracking
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/tracking"
        return await self._request(endpoint, method="GET")

    async def get_website_urls(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Get existing page slugs and each page's layout, to avoid duplicate slugs

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/urls
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/urls"
        return await self._request(endpoint, method="GET")

    async def get_website_viewer_auth(
        self, organization_id: str, project_id: str, app_id: str
    ) -> dict[str, Any]:
        """Whether this site's private pages have members, and which tenant

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/viewer-auth
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/viewer-auth"
        return await self._request(endpoint, method="GET")

    async def remove_website_viewer(
        self, organization_id: str, project_id: str, app_id: str, uid: str
    ) -> dict[str, Any]:
        """Remove somebody's access to this website's gated content

        DELETE /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/viewers/{uid}
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/viewers/{quote(str(uid), safe='')}"
        return await self._request(endpoint, method="DELETE")

    async def list_website_viewers(
        self,
        organization_id: str,
        project_id: str,
        app_id: str,
        page: str | None = None,
        page_size: str | None = None,
        lite: str | None = None,
    ) -> dict[str, Any]:
        """List the people who can read this website's gated content

        GET /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/viewers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/viewers"
        params = {
            "page": page,
            "pageSize": page_size,
            "lite": lite,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request(endpoint, method="GET", params=params)

    async def invite_website_viewer(
        self, organization_id: str, project_id: str, app_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Invite somebody to read this website's gated content

        POST /organizations/{organizationId}/projects/{projectId}/apps/website/{appId}/viewers
        """
        endpoint = f"/organizations/{quote(str(organization_id), safe='')}/projects/{quote(str(project_id), safe='')}/apps/website/{quote(str(app_id), safe='')}/viewers"
        return await self._request(endpoint, method="POST", json=data)


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
    briefs: BriefsResource
    bug_reports: BugReportsResource
    builder: BuilderResource
    crm: CRMResource
    chat: ChatResource
    content_versions: ContentVersionsResource
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
        self.briefs = BriefsResource(self._client)
        self.bug_reports = BugReportsResource(self._client)
        self.builder = BuilderResource(self._client)
        self.crm = CRMResource(self._client)
        self.chat = ChatResource(self._client)
        self.content_versions = ContentVersionsResource(self._client)
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
