# GiantContext Python SDK

Official Python SDK for the [Giant Context](https://giantcontext.com) API -- an autonomous marketing platform.

[![PyPI version](https://img.shields.io/pypi/v/giantcontext.svg)](https://pypi.org/project/giantcontext/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

| Resource | Link |
|---|---|
| PyPI | [pypi.org/project/giantcontext](https://pypi.org/project/giantcontext/) |
| GitHub | [github.com/giantcontext/sdk-python](https://github.com/giantcontext/sdk-python) |
| TypeScript SDK | [npmjs.com/package/@giantcontext/sdk-typescript](https://www.npmjs.com/package/@giantcontext/sdk-typescript) |
| TypeScript GitHub | [github.com/giantcontext/sdk-typescript](https://github.com/giantcontext/sdk-typescript) |
| Developer Portal | [giantcontext.com/en/developers](https://giantcontext.com/en/developers) |
| Platform | [giantcontext.com](https://giantcontext.com) |

## Installation

```bash
pip install giantcontext
```

```bash
poetry add giantcontext
```

```bash
uv add giantcontext
```

## Usage

```python
import asyncio
import os
from giantcontext import create_giant_context

async def main():
    async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
        # Get current user
        me = await gc.me.get_me()
        print(f"Logged in as {me['displayName']}")

        # List organizations you belong to
        orgs = await gc.me.get_my_organizations()
        org = orgs[0]

        # List projects in the organization
        projects = await gc.projects.get_projects(id=org["id"])
        for project in projects["data"]:
            print(f"  {project['name']} ({project['slug']})")

        # Discover apps in a project
        apps = await gc.project_apps.get_project_apps(
            id=org["id"],
            project_id=projects["data"][0]["id"],
        )
        for app in apps["data"]:
            print(f"  {app['type']}: {app['name']}")

asyncio.run(main())
```

## Authentication

### API Keys

API keys use the `gct_` prefix. Create one from the Giant Context console under **Settings > API Keys**.

```python
gc = create_giant_context(api_key="gct_a1b2c3d4e5f6...")
```

The recommended pattern is to store your key in an environment variable:

```bash
export GIANTCONTEXT_API_KEY="gct_a1b2c3d4e5f6..."
```

```python
import os
from giantcontext import create_giant_context

gc = create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"])
```

### Token Exchange

The SDK never sends your API key directly to resource endpoints. On the first request, it exchanges the key for a short-lived JWT via `POST /api/auth/token`. The JWT is cached in memory and automatically refreshed 60 seconds before expiry. This is handled transparently -- you never need to manage tokens yourself.

## Core Concepts

Giant Context organizes content in a hierarchy:

```
Organization
  └── Project
        ├── Apps
        │     ├── Website  (pages, posts, headers, footers, templates, dialogs, sidebars)
        │     ├── Email    (emails, campaigns, segments, headers, footers)
        │     ├── CRM      (contacts, companies, activities)
        │     ├── Forms    (forms, submissions)
        │     └── KB       (articles, categories)
        ├── Files          (images, documents, folders)
        ├── Branding       (colors, fonts, logos, design briefs)
        ├── Drafts         (AI-generated content awaiting review)
        └── Ideas          (AI suggestions from Mind)
```

**Organizations** contain one or more **Projects**. Each project has **Apps** (website, email, CRM, forms, knowledge base), plus shared resources like files and branding. **Drafts** are AI-generated content items, and **Ideas** are suggestions surfaced by Mind, the AI engine.

The SDK mirrors this hierarchy with resource namespaces:

```python
gc.organizations       # Organization-level operations
gc.projects            # Project CRUD and lookup
gc.project_apps        # App discovery within a project
gc.website             # Website pages, posts, headers, footers, templates
gc.email               # Email templates, campaigns, segments
gc.crm                 # Contacts, companies, activities
gc.forms               # Forms and submissions
gc.other               # Knowledge base articles and categories
gc.project_files       # File management and search
gc.project_branding    # Branding assets
gc.drafts              # AI-generated drafts
gc.ideas               # Mind suggestions
gc.me                  # Current user profile, notifications, activity
```

## Async Context Manager

The SDK is fully async, built on [httpx](https://www.python-httpx.org/). The recommended pattern is `async with`, which ensures the underlying HTTP connection pool is properly closed:

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    orgs = await gc.me.get_my_organizations()
    # Connection pool is closed automatically on exit
```

If you need manual lifecycle control:

```python
gc = create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"])
try:
    orgs = await gc.me.get_my_organizations()
finally:
    await gc.close()
```

## Working with Organizations and Projects

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    # List organizations the current user belongs to
    orgs = await gc.me.get_my_organizations()
    org_id = orgs[0]["id"]  # e.g. "d4e5f6a7-1234-5678-9abc-def012345678"

    # Get a specific organization by ID
    org = await gc.organizations.get_organization(id=org_id)
    print(org["name"])  # "Acme Corp"

    # Or look it up by slug
    org = await gc.organizations.get_organization_by_slug(slug="acme-corp")

    # List projects in the organization
    projects = await gc.projects.get_projects(id=org_id)
    # projects == {"data": [...], "pagination": {"page": 1, "pageSize": 25, "total": 3}}

    # Get a specific project by ID
    project = await gc.projects.get_project(
        id=org_id,
        project_id="a1b2c3d4-5678-9abc-def0-123456789abc",
    )
    print(project["name"])  # "Marketing Site"

    # Or look it up by slug
    project = await gc.projects.get_project_by_slug(
        id=org_id,
        project_slug="marketing-site",
    )
```

## Working with Website Content

Most app-level resources require three IDs: `organization_id`, `project_id`, and `app_id`. Discover the app ID using `get_project_apps` or `get_project_app_by_slug`:

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"

    # Discover the website app
    website_app = await gc.project_apps.get_project_app_by_slug(
        id=org_id,
        project_id=project_id,
        app_slug="website",
    )
    app_id = website_app["id"]

    # List all pages
    pages = await gc.website.get_website_pages(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
    )
    for page in pages["data"]:
        print(f"{page['title']} - /{page['slug']}")

    # Get a single page with full block content
    page = await gc.website.get_website_page(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        page_id="b2c3d4e5-6789-abcd-ef01-234567890abc",
    )
    print(page["title"])    # "About Us"
    print(page["sections"]) # [{...}, {...}] -- full section/block tree

    # List blog posts
    posts = await gc.website.get_website_posts(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        page="1",
        page_size="10",
    )

    # Search pages by title
    results = await gc.website.get_website_pages(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        search="pricing",
    )

    # List headers, footers, templates, sidebars, dialogs
    headers = await gc.website.list_website_headers(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    footers = await gc.website.list_website_footers(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    templates = await gc.website.list_website_templates(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )

    # Get page URLs for sitemap generation
    urls = await gc.website.get_website_urls(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
```

## Working with Email

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"

    # Discover the email app
    email_app = await gc.project_apps.get_project_app_by_slug(
        id=org_id, project_id=project_id, app_slug="email",
    )
    app_id = email_app["id"]

    # List email templates
    emails = await gc.email.get_emails(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    for email in emails["data"]:
        print(f"{email['name']} ({email['subject']})")

    # Get a specific email template
    email = await gc.email.get_email(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        email_id="c3d4e5f6-789a-bcde-f012-3456789abcde",
    )

    # List campaigns and their send history
    campaigns = await gc.email.get_email_campaigns(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    campaign = campaigns["data"][0]
    sends = await gc.email.get_email_campaign_sends(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        campaign_id=campaign["id"],
    )

    # List segments and get contact count
    segments = await gc.email.list_email_segments(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    for segment in segments["data"]:
        count = await gc.email.get_email_segment_count(
            organization_id=org_id,
            project_id=project_id,
            app_id=app_id,
            segment_id=segment["id"],
        )
        print(f"{segment['name']}: {count['count']} contacts")
```

## Working with CRM

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"

    # Discover the CRM app
    crm_app = await gc.project_apps.get_project_app_by_slug(
        id=org_id, project_id=project_id, app_slug="crm",
    )
    app_id = crm_app["id"]

    # List contacts with search
    contacts = await gc.crm.get_crm_contacts_list(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        search="jane",
    )
    for contact in contacts["data"]:
        print(f"{contact['name']} <{contact['email']}>")

    # Get a specific contact and their activity history
    contact = await gc.crm.get_crm_contact(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        contact_id="e5f6a7b8-9012-cdef-3456-789abcdef012",
    )
    activities = await gc.crm.get_crm_contact_activities(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        contact_id=contact["id"],
    )

    # List companies
    companies = await gc.crm.get_crm_companies_list(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )

    # Get contacts for a specific company
    company_contacts = await gc.crm.get_crm_company_contacts(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        company_id=companies["data"][0]["id"],
    )
```

## Working with Forms

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"

    # Discover the forms app
    forms_app = await gc.project_apps.get_project_app_by_slug(
        id=org_id, project_id=project_id, app_slug="forms",
    )
    app_id = forms_app["id"]

    # List all forms
    forms = await gc.forms.get_forms_list(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    for form in forms["data"]:
        print(f"{form['name']} (id: {form['id']})")

    # Get a specific form's definition (fields, validation rules)
    form = await gc.forms.get_form(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        form_id="f6a7b8c9-0123-def4-5678-9abcdef01234",
    )

    # List submissions for a form
    submissions = await gc.forms.get_form_submissions(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        form_id=form["id"],
        page="1",
        page_size="50",
    )
    for sub in submissions["data"]:
        print(f"  Submitted at {sub['createdAt']}: {sub['data']}")
```

## Working with Knowledge Base

Knowledge base resources are under `gc.other`:

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"

    # Discover the KB app
    kb_app = await gc.project_apps.get_project_app_by_slug(
        id=org_id, project_id=project_id, app_slug="kb",
    )
    app_id = kb_app["id"]

    # List categories
    categories = await gc.other.list_kb_categories(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    for cat in categories:
        print(f"{cat['name']} (id: {cat['id']})")

    # List articles, optionally filtered by category or status
    articles = await gc.other.list_kb_articles(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        status="published",
        search="getting started",
    )
    for article in articles["data"]:
        print(f"{article['title']}")

    # Get a single article with full content
    article = await gc.other.get_kb_article(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        article_id=articles["data"][0]["id"],
    )

    # Get KB settings
    settings = await gc.other.get_kb_settings(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
```

## Working with Files

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"

    # List files in a project
    files = await gc.project_files.get_files(
        id=org_id, project_id=project_id,
    )
    for f in files["data"]:
        print(f"{f['name']} ({f['mimeType']}, {f['size']} bytes)")

    # Search files by content (semantic search)
    results = await gc.project_files.search_project_files(
        id=org_id,
        project_id=project_id,
        query="quarterly revenue report",
        limit="5",
    )
    for result in results:
        print(f"{result['name']} (score: {result['score']})")

    # Get a specific file
    file = await gc.project_files.get_file(
        id=org_id,
        project_id=project_id,
        file_id="a7b8c9d0-1234-ef56-7890-abcdef012345",
    )

    # Save a file from text content (useful for programmatic content creation)
    new_file = await gc.project_files.save_file(
        id=org_id,
        project_id=project_id,
        data={
            "name": "meeting-notes-2026-04.md",
            "content": "# Q2 Planning\n\nKey decisions from today's meeting...",
            "mimeType": "text/markdown",
        },
    )
    print(f"Created file: {new_file['id']}")

    # List file folders
    folders = await gc.project_files.get_file_folders(
        id=org_id, project_id=project_id,
    )

    # List files in a specific folder
    folder_files = await gc.project_files.get_files(
        id=org_id,
        project_id=project_id,
        folder_id=folders[0]["id"],
    )

    # Find everywhere a file is referenced (pages, emails, etc.)
    refs = await gc.project_files.get_file_references(
        id=org_id,
        project_id=project_id,
        file_id="a7b8c9d0-1234-ef56-7890-abcdef012345",
    )
    for ref in refs:
        print(f"Used in {ref['type']}: {ref['title']}")
```

## Working with Drafts

Drafts are AI-generated content items. The typical workflow is: trigger generation (via the console or API), then poll for completion.

```python
import asyncio

async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"

    # List all drafts for a project
    drafts = await gc.drafts.list_drafts(
        id=org_id, project_id=project_id,
    )
    for draft in drafts["data"]:
        print(f"{draft['title']} [{draft['status']}]")
        # status: "pending", "generating", "ready", "failed"

    # Get a specific draft (includes full generated content when ready)
    draft = await gc.drafts.get_draft(
        id=org_id,
        project_id=project_id,
        draft_id="b8c9d0e1-2345-f678-90ab-cdef01234567",
    )

    # Request an AI edit of existing content
    edit = await gc.drafts.edit_draft(data={
        "organizationId": org_id,
        "projectId": project_id,
        "contentType": "page",
        "contentId": "c9d0e1f2-3456-7890-abcd-ef0123456789",
        "instructions": "Make the hero section more compelling and add a CTA button",
    })
    draft_id = edit["id"]

    # Poll until the draft is ready
    while True:
        draft = await gc.drafts.get_draft(
            id=org_id, project_id=project_id, draft_id=draft_id,
        )
        if draft["status"] in ("ready", "failed"):
            break
        await asyncio.sleep(2)

    if draft["status"] == "ready":
        print(f"Draft ready: {draft['title']}")
```

## Working with Ideas

Ideas are suggestions generated by Mind, the AI engine. They can be approved (which creates a draft) or dismissed.

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"

    # List all ideas for a project
    ideas = await gc.ideas.list_ideas(id=org_id, project_id=project_id)
    for idea in ideas["data"]:
        print(f"[{idea['status']}] {idea['title']}: {idea['description']}")

    # Get a specific idea
    idea = await gc.ideas.get_idea(
        id=org_id,
        project_id=project_id,
        idea_id="d0e1f2a3-4567-890a-bcde-f01234567890",
    )

    # Approve an idea (triggers draft generation)
    result = await gc.ideas.approve_idea(
        id=org_id,
        project_id=project_id,
        idea_id=idea["id"],
        data={"feedback": "Sounds good, please generate this"},
    )

    # Dismiss an idea
    await gc.ideas.dismiss_idea(
        id=org_id,
        project_id=project_id,
        idea_id="e1f2a3b4-5678-90ab-cdef-012345678901",
        data={"reason": "Not relevant to our current strategy"},
    )
```

## Pagination

List endpoints return paginated results. Use `page` and `page_size` to control pagination:

```python
async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    org_id = "d4e5f6a7-1234-5678-9abc-def012345678"
    project_id = "a1b2c3d4-5678-9abc-def0-123456789abc"
    app_id = "e5f6a7b8-9012-cdef-3456-789abcdef012"

    # First page, 10 items
    result = await gc.website.get_website_pages(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        page="1",
        page_size="10",
    )

    pages = result["data"]            # list of page objects
    pagination = result["pagination"]  # {"page": 1, "pageSize": 10, "total": 47}

    # Iterate through all pages
    all_pages = []
    current_page = 1
    while True:
        result = await gc.website.get_website_pages(
            organization_id=org_id,
            project_id=project_id,
            app_id=app_id,
            page=str(current_page),
            page_size="25",
        )
        all_pages.extend(result["data"])
        total = result["pagination"]["total"]
        if len(all_pages) >= total:
            break
        current_page += 1

    print(f"Fetched {len(all_pages)} pages total")
```

## Error Handling

The SDK raises `httpx.HTTPStatusError` for non-2xx responses. The error response body contains a structured JSON message:

```python
import httpx

async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    try:
        project = await gc.projects.get_project(
            id="d4e5f6a7-1234-5678-9abc-def012345678",
            project_id="nonexistent-id",
        )
    except httpx.HTTPStatusError as e:
        print(e.response.status_code)  # 404
        print(e.response.json())       # {"message": "Project not found", "code": "NOT_FOUND"}
```

Common error codes:

| Status | Code             | Meaning                                    |
| ------ | ---------------- | ------------------------------------------ |
| 400    | `BAD_REQUEST`    | Invalid request body or parameters         |
| 401    | `UNAUTHORIZED`   | Invalid or expired API key                 |
| 403    | `FORBIDDEN`      | Insufficient permissions for this resource |
| 404    | `NOT_FOUND`      | Resource does not exist                    |
| 409    | `CONFLICT`       | Resource already exists or state conflict  |
| 429    | `RATE_LIMITED`   | Too many requests, retry after backoff     |
| 500    | `INTERNAL_ERROR` | Server error, contact support              |

## Request IDs and Tracing

Every API response includes an `x-request-id` header. Include this when reporting issues to support:

```python
import httpx

async with create_giant_context(api_key=os.environ["GIANTCONTEXT_API_KEY"]) as gc:
    try:
        await gc.projects.get_project(
            id="d4e5f6a7-1234-5678-9abc-def012345678",
            project_id="nonexistent-id",
        )
    except httpx.HTTPStatusError as e:
        request_id = e.response.headers.get("x-request-id")
        print(f"Request failed. Request ID: {request_id}")
        # Include this ID when contacting support
```

## Configuration

```python
import os
from giantcontext import create_giant_context

gc = create_giant_context(
    # Required. Your API key (format: gct_*).
    # Get one from the Giant Context console: Settings > API Keys.
    api_key=os.environ["GIANTCONTEXT_API_KEY"],

    # Optional. API base URL. Default: "https://api.giantcontext.com"
    base_url="https://api.giantcontext.com",

    # Optional. Request timeout in seconds. Default: 30.0
    timeout=30.0,
)
```

| Parameter  | Type    | Default                        | Description                  |
| ---------- | ------- | ------------------------------ | ---------------------------- |
| `api_key`  | `str`   | _required_                     | API key starting with `gct_` |
| `base_url` | `str`   | `https://api.giantcontext.com` | API base URL                 |
| `timeout`  | `float` | `30.0`                         | Request timeout in seconds   |

## API Reference

<!-- API_REFERENCE_START -->
140 methods across 28 resources.

- [API Keys](#api-keys) (2)
- [App Members](#app-members) (2)
- [Bug Reports](#bug-reports) (2)
- [CRM](#crm) (15)
- [Chat](#chat) (2)
- [Developers](#developers) (5)
- [Drafts](#drafts) (7)
- [Email](#email) (16)
- [Feature Requests](#feature-requests) (3)
- [Forms](#forms) (4)
- [Health](#health) (1)
- [Ideas](#ideas) (5)
- [Invitations](#invitations) (2)
- [KB](#kb) (5)
- [Me](#me) (6)
- [Notifications](#notifications) (1)
- [Organization Members](#organization-members) (4)
- [Organizations](#organizations) (4)
- [Project Apps](#project-apps) (4)
- [Project Branding](#project-branding) (2)
- [Project Domains](#project-domains) (2)
- [Project Files](#project-files) (10)
- [Project Legal Documents](#project-legal-documents) (2)
- [Project Members](#project-members) (2)
- [Project Trash](#project-trash) (2)
- [Project Workflows](#project-workflows) (4)
- [Projects](#projects) (5)
- [Website](#website) (21)

### API Keys

`gc.api_keys`

#### `list_my_api_keys`

Get my API keys
Returns all active API keys belonging to the current user. Each key includes its ID, name, creation date, expiration date, and associated organization. The secret key value is not returned for security.

**Returns:** `dict[str, Any]`

```python
result = await gc.api_keys.list_my_api_keys()
```

---

#### `list_organization_api_keys`

Get organization API keys
Returns all active API keys for an organization. Each key object includes its ID, name, creation date, expiration date, and the user it is associated with. The secret key value is never returned in list responses. Requires admin or owner role within the organization.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.api_keys.list_organization_api_keys(
    id="uuid-id",
)
```


---

### App Members

`gc.app_members`

#### `get_app_member`

Get an app member by ID
Retrieves the full details of a specific app member by their membership ID. Returns the member's user profile information (name, email, avatar) along with their assigned role within the app and membership timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `member_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.app_members.get_app_member(
    id="uuid-id",
    project_id="uuid-project",
    app_id="uuid-app",
    member_id="uuid-member",
)
```

---

#### `get_app_members`

Get members of an app
Returns a paginated list of all members who have been explicitly assigned roles at the app level. Each member entry includes the user's profile information (name, email, avatar) and their assigned role within the app. This is separate from organization-level or project-level membership; only users with direct app-level role assignments are returned.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.app_members.get_app_members(
    id="uuid-id",
    project_id="uuid-project",
    app_id="uuid-app",
)
```


---

### Bug Reports

`gc.bug_reports`

#### `list_my_bug_reports`

Get my bug reports
Returns all bug reports submitted by the current user (up to 100). Each report includes its title, description, steps to reproduce, expected/actual behavior, severity, status (open/resolved/cancelled), browser info, page URL, report count, and linked GitHub issue details if any.

**Returns:** `dict[str, Any]`

```python
result = await gc.bug_reports.list_my_bug_reports()
```

---

#### `get_bug_report_comments`

Get comments for a bug report
Returns all team comments and responses for a specific bug report owned by the current user. Each comment includes its ID, the comment text, the author name, and a creation timestamp. Comments are returned in chronological order.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.bug_reports.get_bug_report_comments(
    id="uuid-id",
)
```


---

### CRM

`gc.crm`

#### `get_crm_activity`

Get activity
Returns a single CRM activity by ID. Each activity is a natural-language description of something that happened, tagged by source app with optional JSON metadata and linked contact/company objects.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `activity_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.get_crm_activity(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    activity_id="uuid-activity",
)
```

---

#### `get_crm_activities_list`

Get activities
Returns a paginated timeline of CRM activities for the specified app, newest first. Each activity is a natural-language description of something that happened for a contact (or company), tagged by source app and optionally enriched with a JSON `data` payload. Supports free-text search across the description.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.get_crm_activities_list(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `log_crm_activity`

Log activity
Appends an activity to the CRM timeline. `description` is a natural-language sentence ('Viewed pricing page', 'Unsubscribed from newsletter'). `source` identifies which app wrote it. Optional `data` carries structured metadata for agents to read. Link to a contact and/or company via id.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.crm.log_crm_activity(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_crm_company_activities`

Get activities for a company
Returns the natural-language activity timeline for a company, newest first. Each row is a description of something that happened, tagged by source app with optional JSON metadata.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `company_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.crm.get_crm_company_activities(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    company_id="uuid-company",
)
```

---

#### `get_crm_company_contacts`

Get contacts for a company
Returns all CRM contacts linked to a specific company, ordered by last name then first name. Each contact includes name, email, phone, title, department, status, source, tags, and linked company object.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `company_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.crm.get_crm_company_contacts(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    company_id="uuid-company",
)
```

---

#### `get_crm_company`

Get company
Returns a single CRM company by ID, including name, website, industry, size, annual revenue, contact info, address, tags, custom properties, and a count of associated contacts.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `company_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.get_crm_company(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    company_id="uuid-company",
)
```

---

#### `get_crm_companies_list`

Get companies
Returns a paginated list of all CRM companies for the specified app. Supports search by company name or industry. Each company includes a count of associated contacts.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.get_crm_companies_list(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_crm_contact_activities`

Get activities for a contact
Returns the natural-language activity timeline for a contact, newest first. Each row is a description of something that happened, tagged by source app with optional JSON metadata.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `contact_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.crm.get_crm_contact_activities(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    contact_id="uuid-contact",
)
```

---

#### `set_crm_contact_field`

Set contact field
Sets a single key on a contact's custom `properties`. Merges at the key level — siblings are preserved. Use this instead of PUT /contacts when only one field needs to change, especially from other apps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `contact_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.set_crm_contact_field(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    contact_id="uuid-contact",
    data={...},
)
```

---

#### `get_crm_contact`

Get contact
Returns a single CRM contact by ID, including linked company details. Fields include name, email, phone, title, department, status, source, tags, email subscription status, and last activity timestamp.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `contact_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.get_crm_contact(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    contact_id="uuid-contact",
)
```

---

#### `update_crm_contact`

Update contact
Updates a CRM contact. All fields are optional — only provided fields are updated. Returns 409 if email or phone conflicts with an existing contact.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `contact_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.update_crm_contact(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    contact_id="uuid-contact",
    data={...},
)
```

---

#### `tag_crm_contact`

Tag contact
Adds a tag to a contact. Tags are free-form strings used for segmenting, gating marketing messages, and ad-hoc grouping. Idempotent — adding an existing tag is a no-op.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `contact_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.tag_crm_contact(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    contact_id="uuid-contact",
    data={...},
)
```

---

#### `untag_crm_contact`

Untag contact
Removes a tag from a contact. Idempotent — removing a tag the contact doesn't have is a no-op.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `contact_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.untag_crm_contact(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    contact_id="uuid-contact",
    data={...},
)
```

---

#### `get_crm_contacts_list`

Get contacts
Returns a paginated list of all CRM contacts for the specified app. Supports search by first name, last name, or email. Each contact includes associated company info if linked.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.get_crm_contacts_list(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `create_crm_contact`

Create contact
Creates a new CRM contact. Requires firstName and lastName. Optionally link to a company via companyId. Supports email, phone, title, department, status, source, custom properties, and tags.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.crm.create_crm_contact(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```


---

### Chat

`gc.chat`

#### `get_chat_conversation`

Get chat conversation with paginated messages
Retrieve a chat conversation with cursor-based paginated messages. Without a cursor, returns the most recent messages (up to limit). Use direction=older with cursor/cursorId to load history.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `conversation_id` | `str` | Yes |
| `cursor` | `str` | No |
| `cursor_id` | `str` | No |
| `direction` | `str` | No |
| `limit` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.chat.get_chat_conversation(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    conversation_id="uuid-conversation",
)
```

---

#### `list_chat_conversations`

Get all chat conversations
List all chat conversations for a given chat app. Returns a paginated list of conversations with their IDs, titles, visitor IDs, and timestamps. Supports search filtering by conversation title or visitor ID. Results are ordered by most recently updated first. This is an admin-only endpoint used to review and manage all customer chat conversations.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.chat.list_chat_conversations(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```


---

### Developers

`gc.developers`

#### `get_developers_doc_category`

Get developer doc category
Retrieves a single developer docs category by its ID, including its name, slug, description, parent relationship, icon, and display order. Returns 404 if the category does not exist or has been soft-deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `category_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.get_developers_doc_category(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    category_id="uuid-category",
)
```

---

#### `list_developers_doc_categories`

Get developer doc categories
Lists all developer docs categories for the specified app, returned as a hierarchical tree structure. Categories are nested under their parent categories and sorted by their display order. Includes all active (non-deleted) categories.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.developers.list_developers_doc_categories(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `get_developers_doc`

Get developer doc
Retrieves a single developer doc by its ID, including its full rich text content, publish status, SEO metadata, and associated category IDs. Returns 404 if the article does not exist or has been soft-deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `doc_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.get_developers_doc(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    doc_id="uuid-doc",
)
```

---

#### `list_developers_docs`

Get developer docs
Lists all developer docs for the specified app, with support for pagination, filtering by category, filtering by publish status, and full-text search across names and slugs. Returns docs sorted by creation date (newest first) by default.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `category_id` | `str` | No |
| `status` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.list_developers_docs(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `list_developers_sync_logs`

List developer sync logs
Returns recent SDK sync events and last-synced timestamps for both OpenAPI and SDK sync.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.list_developers_sync_logs(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```


---

### Drafts

`gc.drafts`

#### `generate_draft`

Generate AI content draft
Generates an AI content draft from a natural language prompt. Creates a system service account if needed, mints an ephemeral JWT, and calls the AI service. The resulting draft can be reviewed and accepted or rejected via the drafts API.

| Parameter | Type | Required |
|-----------|------|----------|
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.generate_draft(
    data={...},
)
```

---

#### `edit_draft`

Create an edit draft
Creates a draft copy of existing content for non-destructive editing. The original stays untouched until the draft is accepted. On accept, the copy's content replaces the original. On reject, the copy is deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.edit_draft(
    data={...},
)
```

---

#### `unarchive_draft`

Unarchive a draft
Restores a previously archived draft to the default list.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `draft_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.unarchive_draft(
    id="uuid-id",
    project_id="uuid-project",
    draft_id="uuid-draft",
)
```

---

#### `archive_draft`

Archive a draft
Hides an accepted draft from the default list without deleting it. Archived drafts are preserved as a paper trail and for AI training data. Only accepted or partially_accepted drafts can be archived.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `draft_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.archive_draft(
    id="uuid-id",
    project_id="uuid-project",
    draft_id="uuid-draft",
)
```

---

#### `get_draft`

Get a draft by ID
Retrieves the full details of a single AI-generated content draft including the prompt, generated content, tool calls, and sources.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `draft_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.get_draft(
    id="uuid-id",
    project_id="uuid-project",
    draft_id="uuid-draft",
)
```

---

#### `delete_draft`

Delete a draft
Permanently deletes a draft. Only rejected, failed, or cancelled drafts can be deleted. Returns 409 if the draft is in any other status (pending, ready, accepted).

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `draft_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.delete_draft(
    id="uuid-id",
    project_id="uuid-project",
    draft_id="uuid-draft",
)
```

---

#### `list_drafts`

List drafts for a project
Returns a paginated list of AI-generated content drafts for the specified project. By default archived drafts are hidden — pass includeArchived=true to include them.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `include_archived` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.list_drafts(
    id="uuid-id",
    project_id="uuid-project",
    page=1,
)
```


---

### Email

`gc.email`

#### `send_transactional_email`

Send transactional email
Sends a single transactional email to a specific recipient using an email template. Used for one-off emails like order confirmations, password resets, etc.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.send_transactional_email(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_contact_email_timeline`

Contact email timeline
Returns the unified email timeline for a contact: past sends + planned sends (including staged sends from a Mind sends draft when present), each with per-send engagement stats (opens, clicks, bounced, complained). Each send carries its `draftId` (non-null only while staged in a ready draft). The response-level `draftId` points at the contact's active sends draft when one exists — use it to render accept/reject UI. Order is COALESCE(sent_at, scheduled_for, created_at) DESC so upcoming planned sends appear at the top, then recent sent, then older.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `contact_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_contact_email_timeline(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    contact_id="uuid-contact",
)
```

---

#### `get_email`

Get email template
Returns a single email template by ID, including name, subject line, full content blocks, header/footer references, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `email_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_email(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    email_id="uuid-email",
)
```

---

#### `get_email_recipient`

Get email recipient
Returns a single recipient row with subscription state.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `email_id` | `str` | Yes |
| `recipient_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_email_recipient(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    email_id="uuid-email",
    recipient_id="uuid-recipient",
)
```

---

#### `unsubscribe_email_recipient`

Unsubscribe a recipient
Soft-unsubscribes a recipient by setting unsubscribed_at and an optional reason. The row is preserved for audit + resubscribe.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `email_id` | `str` | Yes |
| `recipient_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.unsubscribe_email_recipient(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    email_id="uuid-email",
    recipient_id="uuid-recipient",
    data={...},
)
```

---

#### `get_email_recipients`

List email recipients
Returns the subscribers for a specific email template. Includes currently subscribed and previously unsubscribed contacts.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `email_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_email_recipients(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    email_id="uuid-email",
    page=1,
)
```

---

#### `subscribe_email_recipient`

Subscribe a contact
Adds a contact as a recipient of this email. If the contact was previously unsubscribed, the row is resurrected (unsubscribed_at cleared).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `email_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.email.subscribe_email_recipient(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    email_id="uuid-email",
    data={...},
)
```

---

#### `get_emails`

Get email templates
Returns a list of all email templates for the specified app. Each template includes its name, subject line, content blocks, and associated header/footer references.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_emails(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_email_footer`

Get email footer
Returns a single email footer by ID, including its name, content blocks, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `footer_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_email_footer(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    footer_id="uuid-footer",
)
```

---

#### `list_email_footers`

Get email footers
Returns a list of all email footers for the specified app. Footers contain branding, unsubscribe links, and legal text appended to emails.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.list_email_footers(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_email_header`

Get email header
Returns a single email header by ID, including its name, content blocks, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `header_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_email_header(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    header_id="uuid-header",
)
```

---

#### `list_email_headers`

Get email headers
Returns a list of all email headers for the specified app. Headers contain branding and navigation elements prepended to emails.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.list_email_headers(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_email_send`

Get email send with events
Returns a single send row and its full event log (delivered/open/click/bounce/complaint/unsubscribe).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `send_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_email_send(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    send_id="uuid-send",
)
```

---

#### `update_email_send`

Update send
Reschedule, cancel, or adjust metadata on a send row. Cannot modify rows with status='sent' or status='failed'.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `send_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.update_email_send(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    send_id="uuid-send",
    data={...},
)
```

---

#### `get_email_sends`

List email sends
Returns the log of sends (past + planned + queued) for this email app. Filter by email, contact, or status. Sorted by effective time (sent_at, then scheduled_for, then created_at) descending.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `email_id` | `str` | No |
| `contact_id` | `str` | No |
| `status` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.get_email_sends(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `create_email_send`

Create a planned send
Creates a send row. Mind writes status='planned' rows that it reorders as new CRM activity lands. When Mind commits to firing, it transitions to status='queued' with scheduled_for set; a worker picks it up.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.email.create_email_send(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```


---

### Feature Requests

`gc.feature_requests`

#### `get_popular_feature_requests`

Get popular feature requests
Returns all non-merged, non-cancelled feature requests sorted by vote count. Includes whether the current user has voted for each request and the comment count. Does not expose user identity information for privacy.

| Parameter | Type | Required |
|-----------|------|----------|
| `limit` | `str` | No |
| `offset` | `str` | No |
| `status` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.feature_requests.get_popular_feature_requests()
```

---

#### `list_my_feature_requests`

Get my feature requests
Returns all feature requests submitted by the current user (up to 100). Each request includes its title, description, priority, status (open/planned/shipped/cancelled), vote count, and linked GitHub issue details if any.

**Returns:** `dict[str, Any]`

```python
result = await gc.feature_requests.list_my_feature_requests()
```

---

#### `get_feature_request_comments`

Get comments for a feature request
Returns all team comments and responses for a specific feature request owned by the current user. Each comment includes its ID, the comment text, the author name, and a creation timestamp. Comments are returned in chronological order.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.feature_requests.get_feature_request_comments(
    id="uuid-id",
)
```


---

### Forms

`gc.forms`

#### `get_form`

Get form
Retrieve the full details of a single form by its identifier. Returns the form's unique identifier, associated app identifier, name, URL slug, description, field definitions (each with name, type, and required status), rich content layout (Builder block structure used for rendering), settings (notification email, redirect URL, tags, source), active/inactive status, and creation and update timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `form_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.forms.get_form(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    form_id="uuid-form",
)
```

---

#### `get_form_submission`

Get form submission
Retrieve the full details of a single form submission by its identifier. Returns the submission's unique identifier, the parent form identifier, the complete user-submitted data (key-value pairs corresponding to form fields), metadata (user agent, IP address, referer, submission timestamp, tags, source), and the creation timestamp.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `form_id` | `str` | Yes |
| `submission_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.forms.get_form_submission(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    form_id="uuid-form",
    submission_id="uuid-submission",
)
```

---

#### `get_form_submissions`

Get form submissions
Retrieve a paginated list of all submissions received for a specific form. Each submission includes its unique identifier, the parent form identifier, the user-submitted data (key-value pairs corresponding to form fields), metadata (user agent, IP address, referer, submission timestamp, tags, source), and the creation timestamp. Supports full-text search across submission data.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `form_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.forms.get_form_submissions(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    form_id="uuid-form",
    page=1,
)
```

---

#### `get_forms_list`

Get forms
Retrieve a paginated list of all forms belonging to the specified Forms app. Each form in the response includes its unique identifier, name, URL slug, description, field definitions (name, type, required status), rich content layout, settings (notification email, redirect URL), active/inactive status, creation and update timestamps, and a count of how many submissions have been received. Supports searching forms by name or slug.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.forms.get_forms_list(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```


---

### Health

`gc.health`

#### `get_health_echo`

Verify LLM connectivity
Sends a prompt to the AI service which calls Gemini to generate a unique message. A successful response with a message confirms the full chain is working: API → AI service → Gemini API. Each call returns a different message, proving the LLM is live.

**Returns:** `dict[str, Any]`

```python
result = await gc.health.get_health_echo()
```


---

### Ideas

`gc.ideas`

#### `approve_idea`

Approve a Mind idea
Approve an idea, which sets its status to 'approved'. If the idea's content type has draft enabled in the project's aiEntityConfig, this also triggers draft generation automatically. The idea must be in 'pending' status.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `idea_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.approve_idea(
    id="uuid-id",
    project_id="uuid-project",
    idea_id="uuid-idea",
    data={...},
)
```

---

#### `dismiss_idea`

Dismiss a Mind idea
Dismiss an idea that the user doesn't want to pursue. The idea must be in 'pending' status. Optionally include a reason for dismissal. Dismissed ideas are tracked so Mind doesn't re-suggest them.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `idea_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.dismiss_idea(
    id="uuid-id",
    project_id="uuid-project",
    idea_id="uuid-idea",
    data={...},
)
```

---

#### `get_idea`

Get a Mind idea
Returns full details of a Mind idea including title, rationale, outline, priority, similarity score, and status. If the idea has status 'pending', it can be approved (triggering draft generation) or dismissed.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `idea_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.get_idea(
    id="uuid-id",
    project_id="uuid-project",
    idea_id="uuid-idea",
)
```

---

#### `list_ideas`

List Mind ideas for a project
Returns a paginated list of Mind ideas for the project. Ideas represent content gaps or suggestions identified by the AI ideation engine. Filter by status to see pending, approved, dismissed, or drafted ideas.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.list_ideas(
    id="uuid-id",
    project_id="uuid-project",
    page=1,
)
```

---

#### `trigger_ideation`

Trigger Mind ideation for a project
Runs the Mind ideation pipeline for this project, producing new pending ideas. Optional 'target' narrows execution to one (contentType, operationKey) operation — useful for targeted testing. Returns the created ideas synchronously.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.trigger_ideation(
    id="uuid-id",
    project_id="uuid-project",
    data={...},
)
```


---

### Invitations

`gc.invitations`

#### `get_organization_invitation`

Get an invitation by ID
Retrieves a single invitation by its ID within an organization. Returns the invitation object including invitee email, assigned role, status (pending, accepted, expired), creator, and timestamps. The 'id' param is the organization UUID and 'invitationId' is the invitation UUID. Returns 404 if the invitation does not exist.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `invitation_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.invitations.get_organization_invitation(
    id="uuid-id",
    invitation_id="uuid-invitation",
)
```

---

#### `get_organization_invitations`

Get organization invitations
Returns a paginated list of pending, accepted, and expired invitations for an organization. Each invitation includes the invitee email, assigned role, status, creation date, and expiration. Supports search by email, filtering by status, and sorting. Requires owner or admin role within the organization.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.invitations.get_organization_invitations(
    id="uuid-id",
)
```


---

### KB

`gc.kb`

#### `get_kb_article`

Get KB article
Retrieves a single knowledge base article by its ID, including its full rich text content, publish status, SEO metadata, and associated category IDs. Returns 404 if the article does not exist or has been soft-deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `article_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.get_kb_article(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    article_id="uuid-article",
)
```

---

#### `list_kb_articles`

Get KB articles
Lists all knowledge base articles for the specified app, with support for pagination, filtering by category, filtering by publish status, and full-text search across names and slugs. Returns articles sorted by creation date (newest first) by default.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `category_id` | `str` | No |
| `status` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.list_kb_articles(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_kb_category`

Get KB category
Retrieves a single knowledge base category by its ID, including its name, slug, description, parent relationship, icon, and display order. Returns 404 if the category does not exist or has been soft-deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `category_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.get_kb_category(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    category_id="uuid-category",
)
```

---

#### `list_kb_categories`

Get KB categories
Lists all knowledge base categories for the specified app, returned as a hierarchical tree structure. Categories are nested under their parent categories and sorted by their display order. Includes all active (non-deleted) categories.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.kb.list_kb_categories(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `get_kb_settings`

Get KB settings
Retrieves the current configuration settings for the knowledge base app, including display preferences, branding, and behavioral options stored as a JSON settings object on the app record.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.get_kb_settings(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```


---

### Me

`gc.me`

#### `get_my_suspension_messages`

Get my suspension appeal messages
Returns the full suspension appeal message thread for the current user. Each message includes the sender (user or admin), the message content, and a timestamp. Only available to users with an active or past suspension.

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.me.get_my_suspension_messages()
```

---

#### `get_my_notifications`

Get my notifications
Returns a paginated list of notifications for the authenticated user. Supports filtering by read/unread status and notification type via query parameters. Each notification includes its type, title, message, read status, and associated resource reference.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.me.get_my_notifications(
    page=1,
)
```

---

#### `get_my_organizations`

Get organizations I belong to
Returns all organizations that the authenticated user is a member of. Each organization includes its ID, name, slug, logo URL, and the user's role within that organization (e.g. owner, admin, member).

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.me.get_my_organizations()
```

---

#### `get_my_invitations`

Get my pending invitations
Returns a paginated list of pending organization invitations addressed to the current user's email. Each invitation includes the organization name, the role offered, who sent it, and when it was created. Supports standard pagination query parameters.

**Returns:** `dict[str, Any]`

```python
result = await gc.me.get_my_invitations()
```

---

#### `get_my_activities`

Get my activity history
Returns a paginated list of activities performed by or affecting the current user. Each activity includes the action taken, the resource type and ID involved, the actor, and a timestamp. Supports standard pagination query parameters (page, pageSize, sortBy, sortOrder).

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.me.get_my_activities(
    page=1,
)
```

---

#### `get_me`

Get current user profile and permissions
Returns the authenticated user's full profile including name, email, avatar, role (admin/editor/viewer), active status, notification preferences, suspension status, a list of all granted RBAC permissions, and organization memberships with roles. Auto-provisions new users on first login with a default viewer role.

**Returns:** `dict[str, Any]`

```python
result = await gc.me.get_me()
```


---

### Notifications

`gc.notifications`

#### `send_notification`

Send a notification
Dispatches a notification to a single user, an email recipient, all members of an organization, or all members of a project. Exactly one recipient field (userId | email | organizationId | projectId) must be supplied. Channels fan out in parallel; failures land in the result counts. Restricted to platform admins.

| Parameter | Type | Required |
|-----------|------|----------|
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.notifications.send_notification(
    data={...},
)
```


---

### Organization Members

`gc.organization_members`

#### `get_member_project_memberships`

Get member project memberships
Returns a list of all projects in the organization along with the specified member's access level for each project. Each entry includes the project ID, name, and the member's role/permission level within that project (or null if they have no direct project membership). Useful for auditing a member's project access across the organization.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `member_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.organization_members.get_member_project_memberships(
    id="uuid-id",
    member_id="uuid-member",
)
```

---

#### `get_organization_member_activities`

Get member activities
Returns a paginated activity feed for a specific member within an organization. Activities include actions the member has performed such as project updates, document edits, member management changes, and settings modifications. Each activity entry includes the action type, resource details, and timestamp. Supports pagination via page and pageSize query parameters.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `member_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.organization_members.get_organization_member_activities(
    id="uuid-id",
    member_id="uuid-member",
    page=1,
)
```

---

#### `get_organization_member`

Get a member by ID
Retrieves a single organization member by their member ID. Returns the member object including user profile (name, email, avatar), role, title, and join date. The 'id' param is the organization UUID and 'memberId' is the member UUID. Returns 404 if the member does not exist in this organization.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `member_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.organization_members.get_organization_member(
    id="uuid-id",
    member_id="uuid-member",
)
```

---

#### `get_organization_members`

Get organization members
Returns a paginated list of all members in an organization. Each member object includes the member ID, user profile (name, email, avatar), role (owner, admin, member), title, and join date. Supports search by name or email, filtering by role, and sorting. Pagination is controlled via page and pageSize query parameters.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.organization_members.get_organization_members(
    id="uuid-id",
    page=1,
)
```


---

### Organizations

`gc.organizations`

#### `get_service_account`

Get a service account
Returns the full details of a specific service account, including its name, description, role, and creation metadata. Only organization owners and admins can view service account details.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `account_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.organizations.get_service_account(
    id="uuid-id",
    account_id="uuid-account",
)
```

---

#### `list_service_accounts`

Get organization service accounts
Returns all service accounts configured for the organization. Service accounts are non-human identities used for programmatic API access via API keys. Only organization owners and admins can view service accounts.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.organizations.list_service_accounts(
    id="uuid-id",
)
```

---

#### `get_organization_by_slug`

Get organization by slug
Retrieves a single organization by its URL-friendly slug (e.g. 'my-company'). Returns the full organization object including ID, name, slug, logo URL, plan, status, member count, and timestamps. Useful for resolving organizations from URLs or user input where the slug is known but the ID is not. Returns 404 if no organization matches the given slug.

| Parameter | Type | Required |
|-----------|------|----------|
| `slug` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.organizations.get_organization_by_slug(
    slug="my-slug",
)
```

---

#### `get_organization`

Get an organization by ID
Retrieves a single organization by its unique ID. Returns the full organization object including name, slug, logo URL, plan, status, member count, and timestamps. Returns 404 if the organization does not exist.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.organizations.get_organization(
    id="uuid-id",
)
```


---

### Project Apps

`gc.project_apps`

#### `get_project_app_by_slug`

Get a project app by slug
Retrieves the full details of a single app by its URL-friendly slug within the specified project. This is an alternative to looking up an app by ID when you have the human-readable slug instead. Returns the same complete app object as the get-by-ID endpoint including name, slug, app type, configuration, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_slug` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.get_project_app_by_slug(
    id="uuid-id",
    project_id="uuid-project",
    app_slug="my-app",
)
```

---

#### `get_project_app`

Get a project app by ID
Retrieves the full details of a single app by its unique ID within the specified project. Returns the app's name, slug, app type, configuration settings, and timestamps. The app must belong to the specified project or a 404 error is returned.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.get_project_app(
    id="uuid-id",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `get_deleted_project_apps`

Get deleted apps in trash
Returns a list of all soft-deleted (trashed) apps within the specified project. These are apps that have been deleted but not yet permanently removed. Each app includes its full details including name, slug, app type, and deletion timestamp. Trashed apps can be restored using the restore endpoint or permanently deleted using the permanent delete endpoint.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.project_apps.get_deleted_project_apps(
    id="uuid-id",
    project_id="uuid-project",
)
```

---

#### `get_project_apps`

Get apps in a project
Returns a paginated list of all active (non-deleted) apps configured within the specified project. Apps represent individual applications such as websites, CRM instances, email campaigns, forms, knowledge bases, or chat widgets. Each app includes its unique ID, name, slug, app type, configuration, and timestamps. Supports pagination and search filtering.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.get_project_apps(
    id="uuid-id",
    project_id="uuid-project",
)
```


---

### Project Branding

`gc.project_branding`

#### `get_project_branding`

Get project branding
Retrieves the full details of a specific branding configuration by its unique ID within the specified project. Returns the branding's name and complete set of visual identity settings including primary and secondary colors, font selections, logo URLs, favicon, and any other configured styling properties. The branding must belong to the specified project.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `branding_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_branding.get_project_branding(
    id="uuid-id",
    project_id="uuid-project",
    branding_id="uuid-branding",
)
```

---

#### `list_project_brandings`

Get project brandings
Returns a paginated list of all branding configurations for the specified project. Projects can have multiple named branding profiles (e.g., 'Website Brand', 'LMS Brand'), each containing visual identity settings such as primary and secondary colors, font selections, logo URLs, and favicon. Each branding entry includes its unique ID, name, and the full set of configured styling properties.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_branding.list_project_brandings(
    id="uuid-id",
    project_id="uuid-project",
)
```


---

### Project Domains

`gc.project_domains`

#### `get_domain_verification_instructions`

Get domain verification instructions
Retrieves the DNS verification instructions for the specified custom domain. Returns the exact DNS record (type, name, and value) that must be added to the domain's DNS configuration at the domain registrar to prove ownership. This is required before the domain can be verified and used for serving content. The instructions include the CNAME or TXT record details needed for the verification process.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `domain_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_domains.get_domain_verification_instructions(
    id="uuid-id",
    project_id="uuid-project",
    domain_id="uuid-domain",
)
```

---

#### `list_project_domains`

Get all domains for a project
Returns a comprehensive list of all domains (both auto-generated and custom) across all apps within the specified project. Each domain entry includes its hostname, verification status, whether it is generated or custom, whether it is the primary domain for its app, and the associated app name and slug. Domains are grouped by app and sorted with generated domains first and primary domains prioritized.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.project_domains.list_project_domains(
    id="uuid-id",
    project_id="uuid-project",
)
```


---

### Project Files

`gc.project_files`

#### `get_file_references`

Get all places where a file is referenced
Returns a comprehensive list of all entities that reference this file across the project. This includes pages, headers, footers, blog posts, templates, sidebars, dialogs, forms, and branding settings. Useful for understanding the impact of deleting or replacing a file.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.project_files.get_file_references(
    id="uuid-id",
    project_id="uuid-project",
    file_id="uuid-file",
)
```

---

#### `get_file_folder`

Get a file folder
Retrieves the details of a single folder in the project file manager, including its name, parent folder ID, and creation metadata.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `folder_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.get_file_folder(
    id="uuid-id",
    project_id="uuid-project",
    folder_id="uuid-folder",
)
```

---

#### `replace_file_content`

Replace file content
Replaces the content of an existing text file. The file must be a text-based type (Markdown, plain text, CSV, JSON, YAML, HTML, CSS, JS, XML, SVG). The file's storage object is overwritten, its size is updated, and AI embeddings are re-generated from the new content. The file ID, URL, metadata, and all references remain unchanged.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.replace_file_content(
    id="uuid-id",
    project_id="uuid-project",
    file_id="uuid-file",
    data={...},
)
```

---

#### `open_file`

Read file content
Returns the actual content of a file inline — text as a string, images as base64. Use this when you need to read or analyze a file's content rather than just its metadata. Text files (Markdown, CSV, JSON, YAML, plain text, HTML, CSS, JS, XML, SVG) are returned in the 'content' field. Image files (PNG, JPG, GIF, WebP) are returned as base64 in the 'base64Content' field. Files over 10 MB or unsupported types return 404.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.open_file(
    id="uuid-id",
    project_id="uuid-project",
    file_id="uuid-file",
)
```

---

#### `get_file`

Get a file
Retrieves the full details of a single file in the project file manager, including its filename, MIME type, size, dimensions, storage URL, alt text, caption, and folder assignment.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.get_file(
    id="uuid-id",
    project_id="uuid-project",
    file_id="uuid-file",
)
```

---

#### `get_file_folders`

Get file folders in a project
Returns all folders in the project file manager. Optionally filter by parentId to list only child folders of a specific parent folder. Pass parentId='null' or omit it to list root-level folders. Folders are used to organize uploaded files (images, documents, media).

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.project_files.get_file_folders(
    id="uuid-id",
    project_id="uuid-project",
)
```

---

#### `search_files`

Search files by content
Searches project files by their content using semantic/AI search. Returns files whose content matches the meaning of the query, along with the matching content snippet and a relevance score.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `query` | `str` | Yes |
| `limit` | `str` | No |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.project_files.search_files(
    id="uuid-id",
    project_id="uuid-project",
    query="search term",
)
```

---

#### `list_file_trash`

Get items in trash
Returns all soft-deleted files and folders currently in the project's file trash. Items remain in trash until they are restored or permanently deleted. Each item includes its original metadata and the date it was trashed.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.project_files.list_file_trash(
    id="uuid-id",
    project_id="uuid-project",
)
```

---

#### `save_file`

Save a file from text or image content
Saves a file to the project from raw text content (Markdown, Mermaid, CSV, JSON, YAML, plain text, etc.) or base64-encoded image data (PNG, JPG, GIF, WebP, SVG). The file is stored in the project and processed for AI embeddings (text) or image classification (images). Use this to save documents, notes, diagrams, structured data, or screenshots into the project knowledge base.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.save_file(
    id="uuid-id",
    project_id="uuid-project",
    data={...},
)
```

---

#### `get_files`

Get files in a project
Returns a paginated list of files (images, documents, media) uploaded to the project file manager. Supports full-text search by filename, filtering by folder ID and MIME type, and standard pagination and sorting options. Files at the root level can be retrieved by passing folderId as 'null'.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `folder_id` | `str` | No |
| `mime_type` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.get_files(
    id="uuid-id",
    project_id="uuid-project",
    page=1,
)
```


---

### Project Legal Documents

`gc.project_legal_documents`

#### `get_project_legal_document`

Get a project legal document by ID
Returns a single legal document version for the project, including its localized content map and publish status.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `document_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_legal_documents.get_project_legal_document(
    id="uuid-id",
    project_id="uuid-project",
    document_id="uuid-document",
)
```

---

#### `list_project_legal_documents`

List project legal documents
Returns a paginated list of legal document versions for the project, including drafts and published versions across all document types (terms of service, privacy policy, acceptable use policy, cookie policy, custom).

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_legal_documents.list_project_legal_documents(
    id="uuid-id",
    project_id="uuid-project",
)
```


---

### Project Members

`gc.project_members`

#### `get_project_member`

Get a project member by ID
Retrieves the full details of a single project member by their membership ID, including their user profile information, assigned role, and membership metadata.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `member_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_members.get_project_member(
    id="uuid-id",
    project_id="uuid-project",
    member_id="uuid-member",
)
```

---

#### `get_project_members`

Get project members
Returns a paginated list of users who are members of the specified project, including their roles and profile information. Supports search by name, filtering, and sorting. Project members have access to project resources based on their assigned role.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_members.get_project_members(
    id="uuid-id",
    project_id="uuid-project",
    page=1,
)
```


---

### Project Trash

`gc.project_trash`

#### `get_project_trash_item`

Get a single trash item
Retrieves the full details of a single item in the project trash by its trash record ID. Includes the original entity type, entity ID, name, deletion timestamp, and the stored entity data snapshot.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `trash_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_trash.get_project_trash_item(
    id="uuid-id",
    project_id="uuid-project",
    trash_id="uuid-trash",
)
```

---

#### `list_project_trash`

Get all items in project trash
Returns a paginated list of all soft-deleted resources across the entire project, including pages, posts, files, forms, and other entities. Supports filtering by entity type to narrow results. Each trash item includes the original entity metadata, deletion timestamp, and the user who deleted it.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `type` | `str` | No |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_trash.list_project_trash(
    id="uuid-id",
    project_id="uuid-project",
    page=1,
)
```


---

### Project Workflows

`gc.project_workflows`

#### `get_workflow_run`

Get a workflow run and its tasks
| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `run_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_workflows.get_workflow_run(
    id="uuid-id",
    project_id="uuid-project",
    run_id="uuid-run",
)
```

---

#### `dismiss_workflow_run`

Dismiss a workflow run
Soft-hide a run from the default list view. The run itself is preserved for audit and can still be fetched by ID or listed with includeDismissed=true.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `run_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_workflows.dismiss_workflow_run(
    id="uuid-id",
    project_id="uuid-project",
    run_id="uuid-run",
)
```

---

#### `list_workflow_runs`

List workflow runs
Returns a paginated list of workflow runs for the project. Filter by status (pending/running/succeeded/failed/cancelled) or workflow type. Dismissed runs are hidden by default.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `status` | `str` | No |
| `type` | `str` | No |
| `include_dismissed` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_workflows.list_workflow_runs(
    id="uuid-id",
    project_id="uuid-project",
    page=1,
)
```

---

#### `create_workflow_run`

Start a workflow run
Persists a new run of the given workflow type and enqueues its root tasks (tasks with no dependencies). The orchestrator will pick them up on its next tick.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.project_workflows.create_workflow_run(
    id="uuid-id",
    project_id="uuid-project",
    data={...},
)
```


---

### Projects

`gc.projects`

#### `get_project_by_slug`

Get project by slug
Retrieves the full details of a single project by its URL-friendly slug within the specified organization. This is an alternative to looking up a project by its UUID when you have the human-readable slug from a URL or user input. Returns the same complete project object as the get-by-ID endpoint including name, slug, description, settings, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_slug` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.get_project_by_slug(
    id="uuid-id",
    project_slug="my-project",
)
```

---

#### `search_project`

Search project knowledge
Semantic search across all project knowledge — files, pages, posts, KB articles, developer docs, SDK methods, emails, and private CRM data. Returns the most relevant text chunks ranked by similarity, with sourceType and sourceId citations. Use the sourceId with the appropriate get endpoint (getFile, getWebsitePage, etc.) to retrieve the full source document.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `query` | `str` | Yes |
| `limit` | `str` | No |
| `source_types` | `str` | No |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.projects.search_project(
    id="uuid-id",
    project_id="uuid-project",
    query="search term",
)
```

---

#### `get_project_urls`

Get all project URLs
Returns resolved relative URLs for all published content across all apps in the project. Includes pages, posts, articles, etc. with name, path, type, and SEO metadata. Used for link resolution in AI builders, menus, emails, and navigation.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.get_project_urls(
    id="uuid-id",
    project_id="uuid-project",
)
```

---

#### `get_project`

Get a project by ID
Retrieves the full details of a single project by its unique ID within the specified organization. Returns the project's name, slug, description, settings, and timestamps. The project must belong to the specified organization or a 404 error is returned.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.get_project(
    id="uuid-id",
    project_id="uuid-project",
)
```

---

#### `get_projects`

Get projects in an organization
Returns a paginated list of all projects belonging to the specified organization. Projects are the top-level containers that hold apps, brandings, and domains. Supports search filtering by project name and pagination via page and pageSize query parameters. Each project in the response includes its unique ID, name, slug, description, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.get_projects(
    id="uuid-id",
    page=1,
)
```


---

### Website

`gc.website`

#### `get_website_consent_settings`

Get consent settings
Returns the cookie consent and privacy settings configured for this website app, including banner text, consent categories, and GDPR/CCPA compliance options.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_consent_settings(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `get_website_dialog`

Get dialog
Returns a single website dialog by ID, including its name, type, trigger rules, content blocks, and display settings.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `dialog_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_dialog(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    dialog_id="uuid-dialog",
)
```

---

#### `list_website_dialogs`

Get dialogs
Returns a list of all popup dialogs configured for this website app. Dialogs are used for modals, popups, banners, and slide-ins.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_dialogs(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_custom_domain`

Get custom domain
Returns a single custom domain by ID, including hostname, verification status, SSL status, DNS records needed, and primary flag.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `domain_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_custom_domain(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    domain_id="uuid-domain",
)
```

---

#### `list_website_custom_domains`

Get custom domains
Returns a list of all custom domains configured for this website app, including verification status, SSL status, and whether each is the primary domain.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `list[dict[str, Any]]`

```python
result = await gc.website.list_website_custom_domains(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `get_website_footer`

Get website footer
Returns a single website footer by ID, including its name, content blocks, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `footer_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_footer(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    footer_id="uuid-footer",
)
```

---

#### `list_website_footers`

Get website footers
Returns a list of all footer components for this website app. Footers are reusable layout sections displayed at the bottom of pages.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_footers(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_header`

Get website header
Returns a single website header by ID, including its name, content blocks, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `header_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_header(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    header_id="uuid-header",
)
```

---

#### `list_website_headers`

Get website headers
Returns a list of all header components for this website app. Headers are reusable navigation/branding sections displayed at the top of pages.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_headers(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_layout`

Get website layout
Returns a single website layout by ID, including its name, content blocks, layout structure, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `layout_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_layout(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    layout_id="uuid-layout",
)
```

---

#### `list_website_layouts`

Get website layouts
Returns a list of all page layouts for this website app. Layouts provide reusable page layouts and content block structures.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_layouts(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_page`

Get website page
Returns a single website page by ID, including title, slug, full content blocks, SEO metadata, publish status, and layout references (header, footer, sidebar).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_page(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page_id="uuid-page",
)
```

---

#### `get_website_pages`

Get website pages
Returns a list of all pages for this website app. Each page includes its title, slug, publish status, SEO metadata, and associated header/footer/sidebar references.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_pages(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_post`

Get blog post
Returns a single blog post by ID, including title, slug, full content blocks, excerpt, tags, author, featured image, SEO metadata, and publish status.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `post_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_post(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    post_id="uuid-post",
)
```

---

#### `get_website_posts`

Get blog posts
Returns a paginated list of all blog posts for this website app. Each post includes title, slug, excerpt, publish status, author, tags, and featured image.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_posts(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_app_settings`

Get website settings
Returns the website app settings including global SEO defaults, favicon, social image, language, and theme configuration.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_app_settings(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `get_website_sidebar`

Get website sidebar
Returns a single website sidebar by ID, including its name, content blocks, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `sidebar_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_sidebar(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    sidebar_id="uuid-sidebar",
)
```

---

#### `list_website_sidebars`

Get website sidebars
Returns a list of all sidebar components for this website app. Sidebars are reusable layout sections displayed alongside page content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `search` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_sidebars(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_tags`

Get website tags
Returns a list of all tags used across pages and posts in this website app. Tags are used for categorization and filtering.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `list[str]`

```python
result = await gc.website.get_website_tags(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `get_website_tracking_settings`

Get tracking settings
Returns the tracking configuration for this website app, including Google Tag Manager container ID.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_tracking_settings(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `get_website_urls`

Get existing website page URLs
Returns a list of all existing page slugs for this website app. Use this to avoid generating duplicate URLs when creating new pages.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_urls(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

<!-- API_REFERENCE_END -->

## Requirements

- Python 3.11+
- [httpx](https://www.python-httpx.org/)

## License

MIT
