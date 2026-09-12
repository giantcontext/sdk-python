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
        │     ├── Website  (pages, posts, headers, footers, layouts, dialogs, sidebars)
        │     ├── Email    (emails, sends, recipients, headers, footers)
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
gc.website             # Website pages, posts, headers, footers, layouts
gc.email               # Emails, sends, recipients
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

    # List headers, footers, layouts, sidebars, dialogs
    headers = await gc.website.list_website_headers(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    footers = await gc.website.list_website_footers(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    layouts = await gc.website.list_website_layouts(
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

    # List emails. There are no campaigns or segments — each email carries
    # a natural-language trigger description, and Mind decides what to
    # send, when, per contact.
    emails = await gc.email.list_emails(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )
    for email in emails["data"]:
        print(f"{email['name']} ({email['subject']})")

    # Get a specific email
    email = await gc.email.get_email(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        email_id="c3d4e5f6-789a-bcde-f012-3456789abcde",
    )

    # List sends (past + planned deliveries across the app)
    sends = await gc.email.list_email_sends(
        organization_id=org_id, project_id=project_id, app_id=app_id,
    )

    # A contact's full email timeline (what Mind sent and has planned)
    timeline = await gc.email.get_contact_email_timeline(
        organization_id=org_id,
        project_id=project_id,
        app_id=app_id,
        contact_id="d4e5f6a7-8901-bcde-f012-4567890abcde",
    )
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
238 methods across 31 resources.

- [API Keys](#api-keys) (2)
- [App Members](#app-members) (2)
- [Briefs](#briefs) (4)
- [Bug Reports](#bug-reports) (2)
- [Builder](#builder) (16)
- [CRM](#crm) (15)
- [Chat](#chat) (6)
- [Content Versions](#content-versions) (3)
- [Developers](#developers) (14)
- [Drafts](#drafts) (8)
- [Email](#email) (22)
- [Feature Requests](#feature-requests) (3)
- [Forms](#forms) (6)
- [Health](#health) (1)
- [Ideas](#ideas) (5)
- [Invitations](#invitations) (2)
- [KB](#kb) (13)
- [Me](#me) (6)
- [Notifications](#notifications) (1)
- [Organization Members](#organization-members) (5)
- [Organizations](#organizations) (4)
- [Project Apps](#project-apps) (6)
- [Project Branding](#project-branding) (2)
- [Project Domains](#project-domains) (2)
- [Project Files](#project-files) (15)
- [Project Legal Documents](#project-legal-documents) (5)
- [Project Members](#project-members) (2)
- [Project Trash](#project-trash) (6)
- [Project Workflows](#project-workflows) (4)
- [Projects](#projects) (5)
- [Website](#website) (51)

### API Keys

`gc.api_keys`

#### `list_my_api_keys`

List your own API keys across organizations; never returns the secret value
Returns all active API keys belonging to the current user. Each key includes its ID, name, creation date, expiration date, and associated organization. The secret key value is not returned for security.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `organization_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.api_keys.list_my_api_keys(
    page=1,
)
```

---

#### `list_organization_api_keys`

List all API keys in an organization; metadata only, no secret values
Returns all active API keys for an organization. Each key object includes its ID, name, creation date, expiration date, and the user it is associated with. The secret key value is never returned in list responses. Requires admin or owner role within the organization.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `user_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.api_keys.list_organization_api_keys(
    organization_id="uuid-organization",
    page=1,
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
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `member_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.app_members.get_app_member(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    member_id="uuid-member",
)
```

---

#### `list_app_members`

List users with explicit app-level roles, excluding inherited org and project access
Returns a paginated list of all members who have been explicitly assigned roles at the app level. Each member entry includes the user's profile information (name, email, avatar) and their assigned role within the app. This is separate from organization-level or project-level membership; only users with direct app-level role assignments are returned.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `role` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.app_members.list_app_members(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```


---

### Briefs

`gc.briefs`

#### `approve_brief`

Approve a ready brief, which starts draft generation from its draft prompt
Approves a ready Mind brief and starts draft generation from the brief's canonical draft prompt. The brief must be in 'ready' status.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `brief_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.briefs.approve_brief(
    organization_id="uuid-organization",
    project_id="uuid-project",
    brief_id="uuid-brief",
)
```

---

#### `reject_brief`

Reject a ready brief so it never reaches draft generation
Rejects a ready Mind brief so it cannot be used to generate a draft.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `brief_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.briefs.reject_brief(
    organization_id="uuid-organization",
    project_id="uuid-project",
    brief_id="uuid-brief",
    data={...},
)
```

---

#### `get_brief`

Get one brief's full paper trail from idea to draft prompt
Returns full details of a Mind brief, including stream selection, discovery, plan, design, audit, retry history, and draft prompt/spec artifacts.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `brief_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.briefs.get_brief(
    organization_id="uuid-organization",
    project_id="uuid-project",
    brief_id="uuid-brief",
)
```

---

#### `list_briefs`

List Mind briefs for a project
Returns a paginated list of Mind briefs for the project. Briefs are the prepared bridge between ideas and generated drafts, including stream, planning, audit, and draft prompt artifacts.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `status` | `str` | No |
| `content_type` | `str` | No |
| `target_content_type` | `str` | No |
| `idea_id` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |
| `started_at` | `str` | No |
| `completed_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.briefs.list_briefs(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```


---

### Bug Reports

`gc.bug_reports`

#### `list_my_bug_reports`

List bug reports you filed, with severity, status and GitHub issue link
Returns a paginated list of bug reports submitted by the current user, filterable by status, severity and source and searchable by title or description. Each report includes its title, description, steps to reproduce, expected/actual behavior, severity, status (open/resolved/cancelled), browser info, page URL, report count, and linked GitHub issue details if any.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `severity` | `str` | No |
| `source` | `str` | No |
| `report_count` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.bug_reports.list_my_bug_reports(
    page=1,
)
```

---

#### `list_bug_report_comments`

List comments for a bug report
Returns all team comments and responses for a specific bug report owned by the current user. Each comment includes its ID, the comment text, the author name, and a creation timestamp. Comments are returned in chronological order.

| Parameter | Type | Required |
|-----------|------|----------|
| `bug_report_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `author` | `str` | No |
| `source` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.bug_reports.list_bug_report_comments(
    bug_report_id="uuid-bug_report",
    page=1,
)
```


---

### Builder

`gc.builder`

#### `get_content_types`

Get every content type and the blocks allowed in it
Lists every content type you can create or edit — website pages, posts, landings, headers, footers, sidebars, dialogs and layouts; kb articles and landings; developer docs and landings; forms; emails and their headers and footers — with the builder context each belongs to and the exact block types allowed inside it. Use it to answer 'what can I put in this?' before building. The reverse lookup, 'where can I use this block?', is the contexts field on listBuilderBlocks.

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.get_content_types()
```

---

#### `get_block_styles`

Get the styles schema shared by every block
Returns the one styles object every block, column and section accepts — margin, padding, width, background, border, box shadow, position, per-breakpoint visibility, entrance animation and cssId/cssClasses. It is identical for every block type, so call this once and reuse it. getBlock omits styles and refers here rather than repeating them on every block. The schema carries its own value-format guidance: which fields take per-breakpoint objects, when a bare number means a theme spacing multiple rather than pixels, and exactly which colour tokens resolve.

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.get_block_styles()
```

---

#### `get_block`

Get one block type's own fields and hints; shared styles come from getBlockStyles
Returns the JSON schema for a single block type plus its per-field authoring hints, scoped to (and validated against) the content type's palette. The styles object is identical for every block and is served by getBlockStyles instead of being repeated here. Follow this exactly when building block data for insertBlock/updateBlock.

| Parameter | Type | Required |
|-----------|------|----------|
| `block_type` | `str` | Yes |
| `content_type` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.get_block(
    block_type="value",
    content_type="value",
)
```

---

#### `delete_section`

Delete a section and every block inside it; recoverable from version history
Removes a section (and its blocks) from a content tree and records a version. Returns the removed section. The prior state is recoverable via restoreContentVersion.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.delete_section(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `insert_section`

Insert a section into a content tree
Inserts a new section (validated against the section schema, including any blocks it carries) and records a version. Every field on the supplied section is kept; only id and type are server-owned. Ids are generated for the section and for any columns/blocks that omit one. Omit an anchor to append at the end.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.insert_section(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `update_section`

Update a section's own properties; blocks stay untouched and columns cannot be patched
Patches a section's own properties and records a version. Any section field may be patched; id, type and columns are refused with an error rather than ignored. Does not touch its blocks — use the block tools for those.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.update_section(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `delete_block`

Delete a block, returning it; the prior tree stays in version history
Removes a block from a content tree and records a version. Returns the removed block, plus columnRemoved or sectionRemoved when deleting the block emptied its container: an empty column is pruned (it renders a gap) and, when that empties the whole section, the section is pruned too (it paints an orphan background band). Non-destructive at the history level — the prior state is recoverable via restoreContentVersion.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.delete_block(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `insert_block`

Insert a block into a content tree
Inserts a new block into a content entity's tree and records a version. The block's data is validated against its type's schema and the content's block palette. Returns the created block (with its generated id).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.insert_block(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `update_block`

Update a block's data and/or styles by merging only the fields you send; null clears a field
Merges the supplied fields into a block's data and/or its styles and records a version. Send data, styles, or both; fields you omit keep their current value; send null to clear one. Styles cover padding, margins, borders, background, alignment and hideOnMobile — previously settable only at insertBlock, now editable here. Locale maps merge per locale, so writing one language leaves the others intact. Validated against the block type's schema.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.update_block(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `move_section`

Move a section before or after a sibling, or append it at the end
Reorders a section to a new position (relative to a sibling, or appended) and records a version. Returns the moved section.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.move_section(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `move_block`

Move a block beside a sibling or into a section, leaving its data unchanged
Relocates a block to a new anchor (next to a sibling, or into a section) and records a version. Returns the moved block.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.move_block(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `set_content_visibility`

Set whether content is listed and whether it requires a signed-in reader
Changes who may read a content item and whether anything advertises it, and nothing else — not its content, status, slug or metadata. The two flags are independent. isListed governs whether the item appears in the sitemap, indexes, grids and search; an unlisted item stays live at its own URL, which is 'anyone with the link'. requiresViewerAuth governs whether an anonymous reader is served the body at all; a gated item renders the site's Sign In Page instead, never a 404. All four combinations are meaningful, including listed AND gated — a page whose existence is public and whose contents are not. Only the flags you send are changed.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.set_content_visibility(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `unpublish_content`

Return a published item to draft — status only, never the body
Sets a content item's status back to draft, taking it off the public site while leaving its content, slug and metadata intact so it can be published again unchanged. The first-published date is kept, not cleared. Unpublishing tells the search engines the URL is gone and purges the public cache, so a page removed this way stops being served rather than lingering in a cache or an index.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.unpublish_content(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `publish_content`

Publish a page, post, article, doc or email — status only, never the body
Sets a content item's status to published and leaves everything else untouched: not its content, slug, layout or metadata. Works for every content type that has a draft/published lifecycle — website pages and posts, KB articles, developer docs and emails. Structural pieces (headers, footers, layouts, landings, forms) are always live and are refused by name. Publishing re-indexes the item for AI search, signals the search engines, and purges the public cache. Re-publishing something already published is not an error; the response says alreadyInState. Pass publishAt with a future timestamp to schedule instead of publishing: the item stays a draft until a job takes it live, and the response returns scheduledPublishAt with status still draft.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.publish_content(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `search_content`

Find a string or a block type inside content
Search the content of pages, posts, KB articles and developer docs in a project — by exact case-insensitive string (query), by block type (blockTypes), or both. A text query also searches each section's heading and subheading, not just block copy. Filter by content type and by draft/published status. Every match reports its full location — contentId (canonical type), sectionId, columnId and blockId — plus matchIn (block, heading or subheading), so a hit feeds straight into a structural op (deleteSection, moveBlock, updateBlock, updateSection) with no tree read. The field path, locale and snippet are populated for a text query and null for a pure block-type match. Use searchSources instead when looking for material by meaning rather than by exact wording or structure.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `query` | `str` | No |
| `block_types` | `str` | No |
| `content_types` | `str` | No |
| `status` | `str` | No |
| `limit` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.search_content(
    organization_id="uuid-organization",
    project_id="uuid-project",
)
```

---

#### `get_content`

Get a content tree for editing
Returns the full Section[] content tree (with every section/column/block id) for a content entity — pages, posts, landings, etc. Fetch this before granular edits so you have the ids to target.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `content_type` | `str` | Yes |
| `content_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.builder.get_content(
    organization_id="uuid-organization",
    project_id="uuid-project",
    content_type="value",
    content_id="uuid-content",
)
```


---

### CRM

`gc.crm`

#### `get_crm_activity`

Get one activity's description, writing app and JSON data payload
Returns a single CRM activity by ID. Each activity is a natural-language description of something that happened, tagged with the app that wrote it, with optional JSON metadata and linked contact/company objects.

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

#### `list_crm_activities`

List the activity timeline for a whole CRM app, newest first, searchable
Returns a paginated timeline of CRM activities for the specified app, newest first. Each activity is a natural-language description of something that happened for a contact (or company), tagged with the app that wrote it and optionally enriched with a JSON `data` payload. Supports free-text search across the description.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `contact_id` | `str` | No |
| `company_id` | `str` | No |
| `written_by` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.list_crm_activities(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `log_crm_activity`

Log a past-tense sentence onto a contact or company timeline, append-only
Appends an activity to the CRM timeline. `description` is a natural-language sentence ('Viewed pricing page', 'Unsubscribed from newsletter'). `writtenBy` identifies which app wrote it. Optional `data` carries structured metadata for agents to read. Link to a contact and/or company via id.

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

#### `list_crm_company_activities`

List a company's activity timeline, newest first, whatever app logged it
Returns the natural-language activity timeline for a company, newest first. Each row is a description of something that happened, tagged with the app that wrote it, with optional JSON metadata.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `company_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `written_by` | `str` | No |
| `contact_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.list_crm_company_activities(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    company_id="uuid-company",
    page=1,
)
```

---

#### `list_crm_company_contacts`

List contacts linked to one company, paginated, alphabetical by last name
Returns a paginated list of CRM contacts linked to a specific company, ordered by last name then first name. Each contact includes name, email, phone, title, department, status, source, tags, and linked company object.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `company_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `source` | `str` | No |
| `title` | `str` | No |
| `department` | `str` | No |
| `email` | `str` | No |
| `email_subscribed` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.list_crm_company_contacts(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    company_id="uuid-company",
    page=1,
)
```

---

#### `get_crm_company`

Get one company with its profile fields and count of linked contacts
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

#### `list_crm_companies`

List companies in one CRM app, alphabetical by name, each with contact count
Returns a paginated list of all CRM companies for the specified app. Supports search by company name or industry. Each company includes a count of associated contacts.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `industry` | `str` | No |
| `size` | `str` | No |
| `email` | `str` | No |
| `website` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.list_crm_companies(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `list_crm_contact_activities`

List a contact's activity timeline, newest first, including rows written by other apps
Returns the natural-language activity timeline for a contact, newest first. Each row is a description of something that happened, tagged with the app that wrote it, with optional JSON metadata.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `contact_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `written_by` | `str` | No |
| `company_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.list_crm_contact_activities(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    contact_id="uuid-contact",
    page=1,
)
```

---

#### `set_crm_contact_field`

Set one key in a contact's custom properties, merging without clobbering siblings
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

Get one contact with all fields, tags and its linked company
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

Tag one contact with a single free-form string, idempotent, returns the contact
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

Untag one contact, one tag per call, idempotent, returns the updated contact
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

#### `list_crm_contacts`

List contacts in one CRM app, alphabetical by last name, search supported
Returns a paginated list of all CRM contacts for the specified app. Supports search by first name, last name, or email. Each contact includes associated company info if linked.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `company_id` | `str` | No |
| `status` | `str` | No |
| `source` | `str` | No |
| `title` | `str` | No |
| `department` | `str` | No |
| `email` | `str` | No |
| `email_subscribed` | `str` | No |
| `locale` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.crm.list_crm_contacts(
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

#### `reply_to_chat_conversation`

Reply into a chat conversation as a human operator
Send a human operator's reply into a conversation. Persists an 'operator' role message and claims the conversation for the operator if it was not already held. The visitor's widget receives it on its next poll.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `conversation_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.chat.reply_to_chat_conversation(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    conversation_id="uuid-conversation",
    data={...},
)
```

---

#### `take_over_chat_conversation`

Take over a chat conversation from the AI
A human operator takes control of a live conversation. While held, the AI answer path stands down and the operator's replies drive the conversation. Returns the resulting hold state.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `conversation_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.chat.take_over_chat_conversation(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    conversation_id="uuid-conversation",
)
```

---

#### `release_chat_conversation`

Release a chat conversation back to the AI
Release a conversation a human was holding. The AI answer path resumes for the conversation's next visitor message.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `conversation_id` | `str` | Yes |

```python
result = await gc.chat.release_chat_conversation(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    conversation_id="uuid-conversation",
)
```

---

#### `list_chat_conversations`

List every visitor conversation in a chat app, most recently updated first
List all chat conversations for a given chat app. Returns a paginated list of conversations with their IDs, titles, visitor IDs, and timestamps. Supports search filtering by conversation title or visitor ID. Results are ordered by most recently updated first. This is an admin-only endpoint used to review and manage all customer chat conversations.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `visitor_id` | `str` | No |
| `user_id` | `str` | No |

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

#### `list_chat_escalations`

List every escalation in a chat app, newest first
List all escalations for a chat app — the escalations inbox. Returns a paginated list with each escalation's status, visitor contact details, summary, originating URL, linked conversation, and timestamps. Filter by status to separate open handoffs from submitted or cancelled ones. Results are ordered by most recently created first. Admin-only.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `visitor_email` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.chat.list_chat_escalations(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```


---

### Content Versions

`gc.content_versions`

#### `restore_content_version`

Restore an entity to an older version; non-destructive, forward history is kept
Rolls a content entity back to a prior version. Non-destructive: writes the snapshot's content to the live entity and appends a new 'revert' version, preserving forward history.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `version_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.content_versions.restore_content_version(
    organization_id="uuid-organization",
    project_id="uuid-project",
    version_id="uuid-version",
)
```

---

#### `get_content_version`

Get one version's full content snapshot, which the list tool omits
Returns a single content version including its full Section[] content snapshot.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `version_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.content_versions.get_content_version(
    organization_id="uuid-organization",
    project_id="uuid-project",
    version_id="uuid-version",
)
```

---

#### `list_content_versions`

List one entity's edit history newest first; metadata only, no content snapshots
Returns the newest-first version history for a single content entity (page, post, landing, etc). Metadata only — use getContentVersion for a version's full content snapshot. This is the undo/rollback trail for both human and AI edits.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `source` | `str` | No |
| `created_by` | `str` | No |
| `version` | `str` | No |
| `created_at` | `str` | No |
| `content_type` | `str` | Yes |
| `content_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.content_versions.list_content_versions(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
    content_type="value",
    content_id="uuid-content",
)
```


---

### Developers

`gc.developers`

#### `get_developers_doc_category`

Get one category's own fields; its docs come from listDevelopersDocs with categoryId
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

#### `delete_developers_doc_category`

Delete developer doc category
Soft-deletes a developer docs category by moving it to the trash. Returns 404 if the category does not exist or is already deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `category_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.delete_developers_doc_category(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    category_id="uuid-category",
)
```

---

#### `update_developers_doc_category_meta`

Update a category's name and description; cannot re-slug or re-parent it
Updates a developer docs category's name and the description shown alongside it in navigation and listings. Only the fields you send are changed. A category has no separate title, so name IS the label a reader sees, and it is translatable. Cannot change the category's slug, parent, order or icon — a category slug sits in the public path of every doc beneath it and re-slugging leaves no redirect.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `category_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.update_developers_doc_category_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    category_id="uuid-category",
    data={...},
)
```

---

#### `list_developers_doc_categories`

List doc categories as a nested tree, sorted by display order
Lists all developer docs categories for the specified app, returned as a hierarchical tree structure. Categories are nested under their parent categories and sorted by their display order. Includes all active (non-deleted) categories.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `slug` | `str` | No |
| `icon` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.list_developers_doc_categories(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `create_developers_doc_category`

Create a doc category before the docs that reference it; slug must be unique
Creates a new developer docs category in the specified app. Validates slug uniqueness, automatically assigns display order among sibling categories, and supports hierarchical nesting via the parentId field. Categories are used to organize articles within the developer docs.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.developers.create_developers_doc_category(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_developers_doc`

Get one doc with its full content, SEO and category ids
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

#### `delete_developers_doc`

Delete developer doc
Soft-deletes a developer doc by moving it to the trash. Also removes the article from the AI developer docs. Returns 404 if the article does not exist or is already deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `doc_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.delete_developers_doc(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    doc_id="uuid-doc",
)
```

---

#### `update_developers_doc_meta`

Update a doc's name, title, slug, SEO, excerpt, featured image and tags; cannot publish or edit content
Updates the fields that describe a developer doc rather than govern it: SEO title, description, image, noindex, the excerpt, the featured image and tags. Only the fields you send are changed. Can rebind the page shell — the website app it borrows from, and its layout, header and footer. Cannot change the doc's content, status, visibility, order or category membership — use the block tools for content and publishContent to take it live.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `doc_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.update_developers_doc_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    doc_id="uuid-doc",
    data={...},
)
```

---

#### `list_developers_docs`

List docs in a developer portal, newest first; pass lite=true to skip huge content
Lists all developer docs for the specified app, with support for pagination, filtering by category, filtering by publish status, and full-text search across names and slugs. Returns docs sorted by creation date (newest first) by default.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `is_listed` | `str` | No |
| `category_id` | `str` | No |

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

#### `create_developers_doc`

Create a doc; slug must be unique, status defaults to draft, isListed to true
Creates a new developer doc in the specified app. Validates slug uniqueness, automatically assigns display order, and optionally associates the article with categories. If the article is created with 'published' status and has content, it is automatically ingested into the AI developer docs for search and retrieval.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.developers.create_developers_doc(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `update_developers_landing_meta`

Update the landing page's SEO title, description and image; not its content
Updates the fields that describe the developer portal landing page rather than govern it: SEO title, description and image. Only the fields you send are changed. Can rebind the page shell — the website app it borrows from, and its layout, header and footer. Cannot change the landing page's content or visibility — use the block tools for content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |
| `locale` | `str` | No |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.update_developers_landing_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_developers_redirect`

Get one URL redirect by id
Returns a single URL redirect by ID, including its fromPath, toPath, status and source.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `redirect_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.get_developers_redirect(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    redirect_id="uuid-redirect",
)
```

---

#### `list_developers_redirects`

List a developer portal's URL redirects, newest first, with from, to, status and source
Returns a paginated list of the URL redirects for this developers app. Each maps an old path (fromPath) to the current path (toPath) with a status (301 or 308) and a source: auto (recorded when a slug changed) or manual (added by hand).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `source` | `str` | No |
| `status` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.list_developers_redirects(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_developers_sync_logs`

Get the SDK and OpenAPI sync status and recent runs; diagnostic only, starts nothing
Returns recent SDK sync events and last-synced timestamps for both OpenAPI and SDK sync.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.developers.get_developers_sync_logs(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```


---

### Drafts

`gc.drafts`

#### `unarchive_draft`

Unarchive a draft back into the default list; already-unarchived is a no-op
Restores a previously archived draft to the default list.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `draft_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.unarchive_draft(
    organization_id="uuid-organization",
    project_id="uuid-project",
    draft_id="uuid-draft",
)
```

---

#### `archive_draft`

Archive an accepted draft to hide it from the default list without deleting
Hides an accepted draft from the default list without deleting it. Archived drafts are preserved as a paper trail and for AI training data. Only accepted or partially_accepted drafts can be archived.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `draft_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.archive_draft(
    organization_id="uuid-organization",
    project_id="uuid-project",
    draft_id="uuid-draft",
)
```

---

#### `generate_edit_draft`

Generate AI edits to existing content; async, returns a pending draftId to poll
Generates a reviewable edit draft for an EXISTING resource. The AI analyzes the current content, determines what to keep/modify/add/remove, and stages the edited version as a copy — the live content only changes when the draft is accepted. For brand-new content, use generateNewDraft.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.generate_edit_draft(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `get_draft`

Get one draft with its prompt, generated content and status; poll while pending
Retrieves the full details of a single AI-generated content draft including the prompt, generated content, tool calls, and sources. Pass lite=true while polling to get status, qualityScore and errorMessage without the content tree, tool calls or sources.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `draft_id` | `str` | Yes |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.get_draft(
    organization_id="uuid-organization",
    project_id="uuid-project",
    draft_id="uuid-draft",
)
```

---

#### `delete_draft`

Delete a rejected, failed or cancelled draft permanently; other statuses return 409
Permanently deletes a draft. Only rejected, failed, or cancelled drafts can be deleted. Returns 409 if the draft is in any other status (pending, ready, accepted).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `draft_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.delete_draft(
    organization_id="uuid-organization",
    project_id="uuid-project",
    draft_id="uuid-draft",
)
```

---

#### `generate_new_draft`

Generate new content from a prompt; async, takes 5-15 minutes, nothing publishes yet
Generates NEW content as a reviewable draft from a natural language prompt. The draft is a proposal — nothing publishes until it is accepted. For changes to existing content, use generateEditDraft.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.generate_new_draft(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `create_edit_draft`

Create a copy-on-write draft of existing content for manual editing, no AI
Creates a draft copy of existing content for non-destructive editing. The original stays untouched until the draft is accepted. On accept, the copy's content replaces the original. On reject, the copy is deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.create_edit_draft(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `list_drafts`

List a project's drafts newest first; archived hidden unless includeArchived
Returns a paginated list of AI-generated content drafts for the specified project. By default archived drafts are hidden — pass includeArchived=true to include them.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `name` | `str` | No |
| `prompt` | `str` | No |
| `content_type` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |
| `include_archived` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.drafts.list_drafts(
    organization_id="uuid-organization",
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

Get one contact's sent and planned emails with per-send opens and clicks
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

Get one email with its full content blocks and header/footer links
Returns a single email by ID, including name, subject line, trigger description, full content blocks, header/footer references, and timestamps.

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

#### `delete_email`

Delete email
Soft-deletes an email by moving it to the project trash. Can be restored from trash later.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `email_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.delete_email(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    email_id="uuid-email",
)
```

---

#### `update_email_meta`

Update an email's name, slug, subject and send-trigger sentence, not content or status
Updates the fields that describe an email rather than govern it: its internal name and slug, the subject line, and the trigger description saying when the Mind should send it. Only the fields you send are changed. An email is sent rather than served, so its slug is an internal reference and changing it breaks no link. Subject is the reader-facing string; emails have no title. Can rebind the header and footer. Cannot change the email's content or status — use the block tools for content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `email_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.update_email_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    email_id="uuid-email",
    data={...},
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

Unsubscribe a contact from one email; the row is kept for resubscribe
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

#### `list_email_recipients`

List one email's subscribers, including past unsubscribes, newest subscription first
Returns the subscribers for a specific email template. Includes currently subscribed and previously unsubscribed contacts.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `email_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `contact_id` | `str` | No |
| `subscribed_at` | `str` | No |
| `unsubscribed_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.list_email_recipients(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    email_id="uuid-email",
    page=1,
)
```

---

#### `subscribe_email_recipient`

Subscribe a CRM contact to one email; resubscribes if previously unsubscribed
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

#### `list_emails`

List emails in an email app, newest first; pass lite=true to skip content
Returns a list of all emails for the specified app. Each email includes its name, subject line, trigger description, content blocks, and associated header/footer references.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `slug` | `str` | No |
| `name` | `str` | No |
| `header_id` | `str` | No |
| `footer_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.list_emails(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_email_footer`

Get one footer's block content in full; listEmailFooters lite=true returns metadata only
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

#### `delete_email_footer`

Delete email footer
Permanently deletes an email footer.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `footer_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.delete_email_footer(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    footer_id="uuid-footer",
)
```

---

#### `list_email_footers`

List footers in an email app, newest first; pass lite=true to skip content
Returns a list of all email footers for the specified app. Footers contain branding, unsubscribe links, and legal text appended to emails.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |

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

#### `create_email_footer`

Create a footer shell; only name is required, add blocks afterwards
Creates a new email footer with content blocks for branding, unsubscribe links, and legal text.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.email.create_email_footer(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_email_header`

Get one header's full block tree; no lite mode, so expect heavy output
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

#### `delete_email_header`

Delete email header
Permanently deletes an email header.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `header_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.delete_email_header(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    header_id="uuid-header",
)
```

---

#### `list_email_headers`

List headers in an email app, newest first; pass lite=true to skip content
Returns a list of all email headers for the specified app. Headers contain branding and navigation elements prepended to emails.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

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

#### `create_email_header`

Create a header shell; only name is required, add blocks afterwards
Creates a new email header with content blocks for branding and navigation.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.email.create_email_header(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_email_send`

Get one send with its full delivery and engagement event log
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

Update a send to reschedule or cancel; only planned and queued rows accept edits
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

#### `list_email_sends`

List past, queued and planned sends across the app, filterable by email or contact
Returns the log of sends (past + planned + queued) for this email app. Filter by email, contact, or status. Sorted by effective time (sent_at, then scheduled_for, then created_at) descending.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `email_id` | `str` | No |
| `contact_id` | `str` | No |
| `status` | `str` | No |
| `locale` | `str` | No |
| `recipient_email` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.email.list_email_sends(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `create_email_send`

Create a send for one contact; defaults to planned, which sends nothing until queued
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

#### `list_popular_feature_requests`

List everyone's feature requests ranked by votes, showing whether you voted
Returns all non-merged, non-cancelled feature requests sorted by vote count. Includes whether the current user has voted for each request and the comment count. Does not expose user identity information for privacy.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `priority` | `str` | No |
| `vote_count` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.feature_requests.list_popular_feature_requests(
    page=1,
)
```

---

#### `list_my_feature_requests`

List feature requests you filed, with status, vote count and GitHub issue link
Returns all feature requests submitted by the current user (up to 100). Each request includes its title, description, priority, status (open/planned/shipped/cancelled), vote count, and linked GitHub issue details if any.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `priority` | `str` | No |
| `source` | `str` | No |
| `vote_count` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.feature_requests.list_my_feature_requests(
    page=1,
)
```

---

#### `list_feature_request_comments`

List comments for a feature request
Returns all team comments and responses for a specific feature request owned by the current user. Each comment includes its ID, the comment text, the author name, and a creation timestamp. Comments are returned in chronological order.

| Parameter | Type | Required |
|-----------|------|----------|
| `feature_request_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `author` | `str` | No |
| `source` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.feature_requests.list_feature_request_comments(
    feature_request_id="uuid-feature_request",
    page=1,
)
```


---

### Forms

`gc.forms`

#### `get_form`

Get one form's fields, settings and content blocks in Builder format
Retrieve the full details of a single form by its identifier. Returns the form's unique identifier, associated app identifier, name, URL slug, description, field definitions (each with name, type, and required status), rich content layout (Builder block structure used for rendering), settings (redirect URL, tags, source, success message, submission limit), active/inactive status, and creation and update timestamps. The NOTIFICATION ADDRESS IS NOT HERE — it is one setting for the whole Forms app, not per form: read settings.notifyEmail from getProjectApp for this appId. This description used to promise it on the form, which is how it came to be reported as missing.

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

#### `delete_form`

Delete form
Soft-delete a form by moving it to the trash. The form and its data are not permanently destroyed and can potentially be restored. Requires app settings write permission. Returns a success indicator.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `form_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.forms.delete_form(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    form_id="uuid-form",
)
```

---

#### `update_form_meta`

Update a form's name and description; cannot re-slug it or change fields
Updates the fields that describe a form rather than govern it: its internal name, its description, and its settings — the message a visitor sees after submitting, the button label, the submission limit and the CRM tags. Only the fields you send are changed, and settings merge per key, so sending one leaves the rest alone. Cannot change the form's slug, fields, content or active status — use updateBlock and the section tools for content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `form_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.forms.update_form_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    form_id="uuid-form",
    data={...},
)
```

---

#### `get_form_submission`

Get one submission's full answers plus its user agent, IP and referer
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

#### `list_form_submissions`

List one form's submissions, newest first, with submitted data and metadata
Retrieve a paginated list of all submissions received for a specific form. Each submission includes its unique identifier, the parent form identifier, the user-submitted data (key-value pairs corresponding to form fields), metadata (user agent, IP address, referer, submission timestamp, tags, source), and the creation timestamp. Supports full-text search across submission data.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `form_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.forms.list_form_submissions(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    form_id="uuid-form",
    page=1,
)
```

---

#### `list_forms`

List forms in a Forms app with their fields and submission counts, newest first
Retrieve a paginated list of all forms belonging to the specified Forms app. Each form in the response includes its unique identifier, name, URL slug, description, field definitions (name, type, required status), rich content layout, settings (notification email, redirect URL), active/inactive status, creation and update timestamps, and a count of how many submissions have been received. Supports searching forms by name or slug.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `slug` | `str` | No |
| `is_active` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.forms.list_forms(
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

Get a unique LLM-generated message, proving the AI pipeline is live
Sends a prompt to the AI service which calls Gemini to generate a unique message. A successful response with a message confirms the full chain is working: API → AI service → Gemini API. Each call returns a different message, proving the LLM is live.

**Returns:** `dict[str, Any]`

```python
result = await gc.health.get_health_echo()
```


---

### Ideas

`gc.ideas`

#### `approve_idea`

Approve a pending idea to start content generation; a draft may follow automatically
Approve an idea, which sets its status to 'approved'. Email sends and focused email edits enqueue durable materialization contracts; other content types trigger draft generation automatically. The idea must be in 'pending' status.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `idea_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.approve_idea(
    organization_id="uuid-organization",
    project_id="uuid-project",
    idea_id="uuid-idea",
    data={...},
)
```

---

#### `dismiss_idea`

Dismiss a pending idea with an optional reason so Mind stops suggesting it
Dismiss an idea that the user doesn't want to pursue. The idea must be in 'pending' status. Optionally include a reason for dismissal. Dismissed ideas are tracked so Mind doesn't re-suggest them.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `idea_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.dismiss_idea(
    organization_id="uuid-organization",
    project_id="uuid-project",
    idea_id="uuid-idea",
    data={...},
)
```

---

#### `get_idea`

Get one idea's rationale, outline and similarity score before approving or dismissing
Returns full details of a Mind idea including title, rationale, outline, priority, similarity score, and status. If the idea has status 'pending', it can be approved (triggering draft generation) or dismissed.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `idea_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.get_idea(
    organization_id="uuid-organization",
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
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `priority` | `str` | No |
| `app_id` | `str` | No |
| `content_type` | `str` | No |
| `target_content_type` | `str` | No |
| `operation_key` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.ideas.list_ideas(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```

---

#### `trigger_ideation`

Trigger Mind ideation for a project
Enqueues a durable Mind ideation contract for this project. Optional 'target' narrows execution to one (contentType, operationKey) operation — useful for targeted testing. Returns the run and contract IDs immediately.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.ideas.trigger_ideation(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```


---

### Invitations

`gc.invitations`

#### `get_organization_invitation`

Get an invitation by ID
Retrieves a single invitation by its ID within an organization. Returns the invitation object including invitee email, assigned role, status (pending, accepted, expired), creator, and timestamps. The 'invitationId' param is the invitation UUID. Returns 404 if the invitation does not exist.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `invitation_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.invitations.get_organization_invitation(
    organization_id="uuid-organization",
    invitation_id="uuid-invitation",
)
```

---

#### `list_organization_invitations`

List invitations sent by an organization: pending, accepted and expired, with role
Returns a paginated list of pending, accepted, and expired invitations for an organization. Each invitation includes the invitee email, assigned role, status, creation date, and expiration. Supports search by email, filtering by status, and sorting. Requires owner or admin role within the organization.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `role` | `str` | No |
| `email` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.invitations.list_organization_invitations(
    organization_id="uuid-organization",
    page=1,
)
```


---

### KB

`gc.kb`

#### `get_kb_article`

Get one article including its full content tree, status, SEO and category ids
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

#### `delete_kb_article`

Delete KB article
Soft-deletes a knowledge base article by moving it to the trash. Also removes the article from the AI knowledge base. Returns 404 if the article does not exist or is already deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `article_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.delete_kb_article(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    article_id="uuid-article",
)
```

---

#### `update_kb_article_meta`

Update an article's name, title, slug, SEO fields, excerpt, tags and featured image; cannot publish or edit content
Updates the fields that describe a knowledge base article rather than govern it: SEO title, description, image and noindex, plus the excerpt, tags and featured image. Only the fields you send are changed. Can rebind the layout, header and footer. Cannot change the article's content, status, visibility, order or category assignments — use publishContent to take it live.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `article_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.update_kb_article_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    article_id="uuid-article",
    data={...},
)
```

---

#### `list_kb_articles`

List articles in one KB app, newest first; pass lite=true to omit huge content
Lists all knowledge base articles for the specified app, with support for pagination, filtering by category, filtering by publish status, and full-text search across names and slugs. Returns articles sorted by creation date (newest first) by default.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `slug` | `str` | No |
| `status` | `str` | No |
| `is_listed` | `str` | No |
| `category_id` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |
| `published_at` | `str` | No |

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

#### `create_kb_article`

Create an article shell; publishing with content also ingests it for AI chat
Creates a new knowledge base article in the specified app. Validates slug uniqueness, automatically assigns display order, and optionally associates the article with categories. If the article is created with 'published' status and has content, it is automatically ingested into the AI knowledge base for search and retrieval.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.kb.create_kb_article(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_kb_category`

Get one category's name, slug, description, parent and order; not its articles
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

#### `delete_kb_category`

Delete KB category
Soft-deletes a knowledge base category by moving it to the trash. Returns 404 if the category does not exist or is already deleted.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `category_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.delete_kb_category(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    category_id="uuid-category",
)
```

---

#### `update_kb_category_meta`

Update a category's name and description; cannot re-slug, reorder or re-parent it
Updates a knowledge base category's name and its description, the blurb shown beneath it in listings and on its own page. Only the fields you send are changed. A category has no separate title, so name IS the label a reader sees, and it is translatable. Cannot change the category's slug or icon, reorder it, or move it in the hierarchy — a category slug sits in the public path of every article beneath it and re-slugging leaves no redirect.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `category_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.update_kb_category_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    category_id="uuid-category",
    data={...},
)
```

---

#### `list_kb_categories`

List a KB app's categories as a nested parent-child tree, roots paginated
Lists all knowledge base categories for the specified app, returned as a hierarchical tree structure. Categories are nested under their parent categories and sorted by their display order. Includes all active (non-deleted) categories.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `slug` | `str` | No |
| `icon` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.list_kb_categories(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `create_kb_category`

Create a category, optionally nested under a parent; order assigned automatically
Creates a new knowledge base category in the specified app. Validates slug uniqueness, automatically assigns display order among sibling categories, and supports hierarchical nesting via the parentId field. Categories are used to organize articles within the knowledge base.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.kb.create_kb_category(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `update_kb_landing_meta`

Update knowledge base landing page metadata
Updates the SEO title, description and image of the knowledge base landing page. Only the fields you send are changed. Can rebind its website, layout, header and footer. Cannot replace the landing's builder content or change its visibility.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.update_kb_landing_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_kb_redirect`

Get one URL redirect by id
Returns a single URL redirect by ID, including its fromPath, toPath, status and source.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `redirect_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.get_kb_redirect(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    redirect_id="uuid-redirect",
)
```

---

#### `list_kb_redirects`

List a knowledge base's URL redirects, newest first, with from, to, status and source
Returns a paginated list of the URL redirects for this knowledge base app. Each maps an old path (fromPath) to the current path (toPath) with a status (301 or 308) and a source: auto (recorded when a slug changed) or manual (added by hand).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `source` | `str` | No |
| `status` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.kb.list_kb_redirects(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```


---

### Me

`gc.me`

#### `list_my_suspension_messages`

List your suspension appeal thread, both your messages and admin replies
Returns the full suspension appeal message thread for the current user. Each message includes the sender (user or admin), the message content, and a timestamp. Only available to users with an active or past suspension.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `author_type` | `str` | No |
| `author_id` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.me.list_my_suspension_messages(
    page=1,
)
```

---

#### `list_my_notifications`

List the caller's notifications, filterable by read status and type
Returns a paginated list of notifications for the authenticated user. Supports filtering by read/unread status and notification type via query parameters. Each notification includes its type, title, message, read status, and associated resource reference.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `type` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.me.list_my_notifications(
    page=1,
)
```

---

#### `list_my_organizations`

List organizations you belong to and your role in each
Returns all organizations that the authenticated user is a member of. Each organization includes its ID, name, slug, logo URL, and the user's role within that organization (owner, admin, editor or viewer).

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `slug` | `str` | No |
| `plan` | `str` | No |
| `subscription_status` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.me.list_my_organizations(
    page=1,
)
```

---

#### `list_my_invitations`

List pending org invitations addressed to the caller's email, with offered role
Returns a paginated list of pending organization invitations addressed to the current user's email. Each invitation includes the organization name, the role offered, who sent it, and when it was created. Supports standard pagination query parameters.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `role` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.me.list_my_invitations(
    page=1,
)
```

---

#### `list_my_activities`

List activity by or affecting you, with the resource each touched, paginated
Returns a paginated list of activities performed by or affecting the current user. Each activity includes the action taken, the resource type and ID involved, the actor, and a timestamp. Filter by action or resourceType, sort with sort=field:direction, and page with page and pageSize.

| Parameter | Type | Required |
|-----------|------|----------|
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `action` | `str` | No |
| `resource_type` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.me.list_my_activities(
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

#### `list_member_project_memberships`

List all organization projects with one member's access level, null where none
Returns a list of all projects in the organization along with the specified member's access level for each project. Each entry includes the project ID, name, and the member's role/permission level within that project (or null if they have no direct project membership). Useful for auditing a member's project access across the organization.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `member_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `role` | `str` | No |
| `joined_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.organization_members.list_member_project_memberships(
    organization_id="uuid-organization",
    member_id="uuid-member",
    page=1,
)
```

---

#### `list_member_app_memberships`

List every app with one member's role; project roles do not grant app access
Returns every app across the organization's projects along with the specified member's role on each, or null where they have no binding. Since a project role no longer grants access inside an app, this is what shows which apps a member can actually work in. Each entry carries its project so the apps can be grouped under the project they belong to.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `member_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `app_type` | `str` | No |
| `role` | `str` | No |
| `project_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.organization_members.list_member_app_memberships(
    organization_id="uuid-organization",
    member_id="uuid-member",
    page=1,
)
```

---

#### `list_organization_member_activities`

Get member activities
Returns a paginated activity feed for a specific member within an organization. Activities include actions the member has performed such as project updates, document edits, member management changes, and settings modifications. Each activity entry includes the action type, resource details, and timestamp. Supports pagination via page and pageSize query parameters.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `member_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `action` | `str` | No |
| `resource_type` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.organization_members.list_organization_member_activities(
    organization_id="uuid-organization",
    member_id="uuid-member",
    page=1,
)
```

---

#### `get_organization_member`

Get one member's profile, role, title and join date by member UUID
Retrieves a single organization member by their member ID. Returns the member object including user profile (name, email, avatar), role, title, and join date. The 'memberId' param is the member UUID. Returns 404 if the member does not exist in this organization.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `member_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.organization_members.get_organization_member(
    organization_id="uuid-organization",
    member_id="uuid-member",
)
```

---

#### `list_organization_members`

List members of an organization with their roles, paginated and searchable
Returns a paginated list of all members in an organization. Each member object includes the member ID, user profile (name, email, avatar), role (owner, admin, editor, viewer), title, and join date. Supports search by name or email, filtering by role, and sorting. Pagination is controlled via page and pageSize query parameters.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `role` | `str` | No |
| `title` | `str` | No |
| `user_id` | `str` | No |
| `invited_by` | `str` | No |
| `joined_at` | `str` | No |
| `invited_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.organization_members.list_organization_members(
    organization_id="uuid-organization",
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
| `organization_id` | `str` | Yes |
| `account_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.organizations.get_service_account(
    organization_id="uuid-organization",
    account_id="uuid-account",
)
```

---

#### `list_service_accounts`

List an organization's service accounts, newest first
Returns all service accounts configured for the organization. Service accounts are non-human identities used for programmatic API access via API keys. Only organization owners and admins can view service accounts.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `email` | `str` | No |
| `created_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.organizations.list_service_accounts(
    organization_id="uuid-organization",
    page=1,
)
```

---

#### `get_organization`

Get one organization's name, slug, plan, status and member count by ID
Retrieves a single organization by its unique ID. Returns the full organization object including name, slug, logo URL, plan, status, member count, and timestamps. Returns 404 if the organization does not exist.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.organizations.get_organization(
    organization_id="uuid-organization",
)
```

---

#### `get_organization_by_slug`

Get an organization from a URL slug when you have no ID
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

### Project Apps

`gc.project_apps`

#### `get_project_app_by_slug`

Get a project app by slug
Retrieves the full details of a single app by its URL-friendly slug within the specified project. This is an alternative to looking up an app by ID when you have the human-readable slug instead. Returns the same complete app object as the get-by-ID endpoint including name, slug, app type, configuration, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_slug` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.get_project_app_by_slug(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_slug="my-app",
)
```

---

#### `get_app_settings`

Read one app's settings, whatever kind of app it is
Returns the app's settings object together with the schema describing what that app accepts, so a caller can discover the shape without knowing the app type in advance. The shape comes from the app's own declaration, not from a list maintained here. Answers 404 with NO_APP_SETTINGS for an app type that has no settings, and names the ones that do.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.get_app_settings(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `update_app_settings`

Change one app's settings, merging into what is already there
Merges the given keys into the app's settings, validating them against the app's own declared schema — an unknown key or a wrong type is a 400 naming the offending key, not a silent write. Only the keys sent are changed; omitted keys keep their value. Send a key as null to clear it.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.update_app_settings(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_project_app`

Get a project app by ID
Retrieves the full details of a single app by its unique ID within the specified project. Returns the app's name, slug, app type, configuration settings, and timestamps. The app must belong to the specified project or a 404 error is returned.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.get_project_app(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `list_deleted_project_apps`

List soft-deleted apps in a project's trash, restorable or permanently deletable
Returns a list of all soft-deleted (trashed) apps within the specified project. These are apps that have been deleted but not yet permanently removed. Each app includes its full details including name, slug, app type, and deletion timestamp. Trashed apps can be restored using the restore endpoint or permanently deleted using the permanent delete endpoint.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `slug` | `str` | No |
| `app_type` | `str` | No |
| `is_active` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.list_deleted_project_apps(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```

---

#### `list_project_apps`

List a project's active apps and their types to obtain the appId
Returns a paginated list of all active (non-deleted) apps configured within the specified project. Apps represent individual applications such as websites, email, forms, knowledge bases, chat widgets, CRM instances, developer docs, or socials. Each app includes its unique ID, name, slug, app type, configuration, and timestamps. Supports pagination and search filtering.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `slug` | `str` | No |
| `app_type` | `str` | No |
| `is_active` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_apps.list_project_apps(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```


---

### Project Branding

`gc.project_branding`

#### `get_project_branding`

Get one branding profile's colors, fonts, logos and favicon
Retrieves the full details of a specific branding configuration by its unique ID within the specified project. Returns the branding's name and complete set of visual identity settings including primary and secondary colors, font selections, logo URLs, favicon, and any other configured styling properties. The branding must belong to the specified project.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `branding_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_branding.get_project_branding(
    organization_id="uuid-organization",
    project_id="uuid-project",
    branding_id="uuid-branding",
)
```

---

#### `list_project_brandings`

List a project's named branding profiles: colors, fonts, logos, favicon
Returns a paginated list of all branding configurations for the specified project. Projects can have multiple named branding profiles (e.g., 'Website Brand', 'LMS Brand'), each containing visual identity settings such as primary and secondary colors, font selections, logo URLs, and favicon. Each branding entry includes its unique ID, name, and the full set of configured styling properties.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `created_by` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_branding.list_project_brandings(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```


---

### Project Domains

`gc.project_domains`

#### `get_domain_verification_instructions`

Get the exact DNS record the owner must add to verify a domain
Retrieves the DNS verification instructions for the specified custom domain. Returns the exact DNS record (type, name, and value) that must be added to the domain's DNS configuration at the domain registrar to prove ownership. This is required before the domain can be verified and used for serving content. The instructions include the CNAME or TXT record details needed for the verification process.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `domain_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_domains.get_domain_verification_instructions(
    organization_id="uuid-organization",
    project_id="uuid-project",
    domain_id="uuid-domain",
)
```

---

#### `list_project_domains`

List a project's manageable domains with verification status and owning app
Returns a comprehensive list of all domains (both auto-generated and custom) across all apps within the specified project. Each domain entry includes its hostname, verification status, whether it is generated or custom, whether it is the primary domain for its app, and the associated app name and slug. Domains are grouped by app and sorted with generated domains first and primary domains prioritized.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `app_id` | `str` | No |
| `app_type` | `str` | No |
| `hostname` | `str` | No |
| `is_generated` | `str` | No |
| `is_primary` | `str` | No |
| `is_verified` | `str` | No |
| `verification_status` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_domains.list_project_domains(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```


---

### Project Files

`gc.project_files`

#### `restore_file_trash_item`

Restore an item from trash
Restores a previously soft-deleted file or folder from the file trash back to the file manager. For folders, optionally restores all contained files and subfolders. Requires specifying the item type (file or folder) in the request body. Returns counts of restored files and folders for folder-type items.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `item_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.restore_file_trash_item(
    organization_id="uuid-organization",
    project_id="uuid-project",
    item_id="uuid-item",
    data={...},
)
```

---

#### `list_file_references`

List places where a file is referenced
Returns a comprehensive list of all entities that reference this file across the project. This includes pages, headers, footers, blog posts, templates, sidebars, dialogs, forms, and branding settings. Useful for understanding the impact of deleting or replacing a file.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `type` | `str` | No |
| `id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.list_file_references(
    organization_id="uuid-organization",
    project_id="uuid-project",
    file_id="uuid-file",
    page=1,
)
```

---

#### `get_file_folder`

Get one folder's name and parent; use listFiles with folderId to see its files
Retrieves the details of a single folder in the project file manager, including its name, parent folder ID, and creation metadata.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `folder_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.get_file_folder(
    organization_id="uuid-organization",
    project_id="uuid-project",
    folder_id="uuid-folder",
)
```

---

#### `delete_file_folder`

Delete a file folder (files are moved to root)
Soft-deletes a folder and all its contents (files and subfolders) by moving them to the file trash. The folder and its contents can be restored from trash before permanent deletion. Returns a count of deleted folders and files.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `folder_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.delete_file_folder(
    organization_id="uuid-organization",
    project_id="uuid-project",
    folder_id="uuid-folder",
)
```

---

#### `replace_file_content`

Replace a text file's content in place; id, URL and references stay unchanged
Replaces the content of an existing text file. The file must be a text-based type (Markdown, plain text, CSV, JSON, YAML, HTML, CSS, JS, XML, SVG). The file's storage object is overwritten, its size is updated, and AI embeddings are re-generated from the new content. The file ID, URL, metadata, and all references remain unchanged.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.replace_file_content(
    organization_id="uuid-organization",
    project_id="uuid-project",
    file_id="uuid-file",
    data={...},
)
```

---

#### `permanent_delete_file_trash_item`

Permanently delete an item from trash
Permanently and irreversibly deletes a file or folder from the file trash. For files, also removes the file from cloud storage. For folders, recursively deletes all contained files and subfolders. Requires specifying the item type (file or folder) in the request body.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `item_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.permanent_delete_file_trash_item(
    organization_id="uuid-organization",
    project_id="uuid-project",
    item_id="uuid-item",
    data={...},
)
```

---

#### `open_file`

Open a file's content inline: text as string, images as base64, 10 MB cap
Returns the actual content of a file inline — text as a string, images as base64. Use this when you need to read or analyze a file's content rather than just its metadata. Text files (Markdown, CSV, JSON, YAML, plain text, HTML, CSS, JS, XML, SVG) are returned in the 'content' field. Image files (PNG, JPG, GIF, WebP) are returned as base64 in the 'base64Content' field. Files over 10 MB or unsupported types return 404.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.open_file(
    organization_id="uuid-organization",
    project_id="uuid-project",
    file_id="uuid-file",
)
```

---

#### `empty_file_trash`

Empty trash (permanently delete old items)
Permanently deletes all items from the file trash, optionally filtering to only delete items older than a specified number of days. Removes files from cloud storage and recursively deletes folder contents. Returns counts of deleted files and folders.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.empty_file_trash(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `get_file`

Get one file's metadata only (URL, type, size, folder); openFile returns the content
Retrieves the full details of a single file in the project file manager, including its filename, MIME type, size, dimensions, storage URL, alt text, caption, and folder assignment.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.get_file(
    organization_id="uuid-organization",
    project_id="uuid-project",
    file_id="uuid-file",
)
```

---

#### `delete_file`

Delete a file
Soft-deletes a file from the project file manager by moving it to the file trash. The file can be restored from trash before it is permanently deleted. Also removes the file from cloud storage if permanently deleted later.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `file_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.delete_file(
    organization_id="uuid-organization",
    project_id="uuid-project",
    file_id="uuid-file",
)
```

---

#### `list_file_folders`

List file folders in a project
Returns all folders in the project file manager. Filter by parentId to list only the children of one folder, or parentId_isnull=true for the project root. Omit both to list every folder in the project. Folders are used to organize uploaded files (images, documents, media).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `parent_id` | `str` | No |
| `name` | `str` | No |
| `created_by` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.list_file_folders(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```

---

#### `search_files`

Search file contents by meaning; returns matching snippet and relevance score per file
Searches project files by their content using semantic/AI search. Returns files whose content matches the meaning of the query, along with the matching content snippet and a relevance score.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `mime_type` | `str` | No |
| `similarity` | `str` | No |
| `filename` | `str` | No |
| `query` | `str` | Yes |
| `limit` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.search_files(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
    query="search term",
)
```

---

#### `list_file_trash`

List a project's trashed files and folders, restorable until permanently deleted
Returns all soft-deleted files and folders currently in the project's file trash. Items remain in trash until they are restored or permanently deleted. Each item includes its original metadata and the date it was trashed.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `type` | `str` | No |
| `mime_type` | `str` | No |
| `parent_id` | `str` | No |
| `deleted_by` | `str` | No |
| `deleted_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.list_file_trash(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```

---

#### `save_file`

Save a file from text or image content
Saves a file to the project from raw text content (Markdown, Mermaid, CSV, JSON, YAML, plain text, etc.) or base64-encoded binary data — images (PNG, JPG, GIF, WebP, SVG) and documents alike (PDF, Word, Excel), with document text extracted and embedded exactly as a console upload would. The file is stored in the project and processed for AI embeddings (text) or image classification (images). Use this to save documents, notes, diagrams, structured data, or screenshots into the project knowledge base.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.save_file(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `list_files`

List a project's files, with search, filtering and sorting
Returns a paginated list of files (images, documents, media) uploaded to the project file manager. Search matches filename, original filename, title and description. Filter with folderId (folderId_isnull=true for the project root), mimeType (mimeType_like=image/ for every image), isPublic and grounding.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `is_public` | `str` | No |
| `grounding` | `str` | No |
| `mime_type` | `str` | No |
| `folder_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_files.list_files(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```


---

### Project Legal Documents

`gc.project_legal_documents`

#### `publish_project_legal_document`

Publish a draft project legal document
Publishes a draft legal document, making it immutable. Every locale listed in the project's enabled_locales must have non-empty content, otherwise the publish is rejected.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `document_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_legal_documents.publish_project_legal_document(
    organization_id="uuid-organization",
    project_id="uuid-project",
    document_id="uuid-document",
)
```

---

#### `get_project_legal_document`

Get a project legal document by ID
Returns a single legal document version for the project, including its localized content map and publish status.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `document_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_legal_documents.get_project_legal_document(
    organization_id="uuid-organization",
    project_id="uuid-project",
    document_id="uuid-document",
)
```

---

#### `update_project_legal_document`

Update a draft project legal document
Updates the localized content of a draft legal document. Published documents are immutable and must be re-drafted as a new version.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `document_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_legal_documents.update_project_legal_document(
    organization_id="uuid-organization",
    project_id="uuid-project",
    document_id="uuid-document",
    data={...},
)
```

---

#### `list_project_legal_documents`

List a project's legal document versions across all types, draft and published
Returns a paginated list of legal document versions for the project, including drafts and published versions across all document types (terms of service, privacy policy, acceptable use policy, cookie policy, custom).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `type` | `str` | No |
| `status` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_legal_documents.list_project_legal_documents(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```

---

#### `create_project_legal_document`

Create a new draft project legal document
Creates a new draft legal document for the project with auto-incremented version per (project, type). Content is a record keyed by locale code; at least one locale is required before publishing.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.project_legal_documents.create_project_legal_document(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
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
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `member_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_members.get_project_member(
    organization_id="uuid-organization",
    project_id="uuid-project",
    member_id="uuid-member",
)
```

---

#### `list_project_members`

List users added to a project with their roles
Returns a paginated list of users who are members of the specified project, including their roles and profile information. Supports search by name, filtering, and sorting. Project members have access to project resources based on their assigned role.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `role` | `str` | No |
| `title` | `str` | No |
| `user_id` | `str` | No |
| `joined_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_members.list_project_members(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```


---

### Project Trash

`gc.project_trash`

#### `restore_project_trash_batch`

Restore a trash batch
Restores every trash entry that shares a batch id back to its original location. Batches are created when a single user action trashed multiple rows — for example, deleting a folder places the folder, its files, and its subfolders into the same batch. Folders are restored before files so parent-child foreign keys hold.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `batch_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_trash.restore_project_trash_batch(
    organization_id="uuid-organization",
    project_id="uuid-project",
    batch_id="uuid-batch",
)
```

---

#### `restore_project_trash_item`

Restore an item from trash
Restores a soft-deleted entity from the project trash back to its original location. Dynamically rebuilds the database INSERT from the stored JSONB entity snapshot. Returns the restored entity type, entity ID, and associated app ID.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `trash_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_trash.restore_project_trash_item(
    organization_id="uuid-organization",
    project_id="uuid-project",
    trash_id="uuid-trash",
)
```

---

#### `get_project_trash_item`

Get one trashed item's entity type, deletion metadata and stored data snapshot
Retrieves the full details of a single item in the project trash by its trash record ID. Includes the original entity type, entity ID, name, deletion timestamp, and the stored entity data snapshot.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `trash_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_trash.get_project_trash_item(
    organization_id="uuid-organization",
    project_id="uuid-project",
    trash_id="uuid-trash",
)
```

---

#### `permanent_delete_project_trash_item`

Permanently delete an item from trash
Permanently and irreversibly removes an item from the project trash. For media/file items, also deletes the associated file from cloud storage. This operation cannot be undone. The item will no longer be recoverable after this action.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `trash_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_trash.permanent_delete_project_trash_item(
    organization_id="uuid-organization",
    project_id="uuid-project",
    trash_id="uuid-trash",
)
```

---

#### `list_project_trash`

List soft-deleted items across a whole project, filterable by entity type
Returns a paginated list of all soft-deleted resources across the entire project, including pages, posts, files, forms, and other entities. Supports filtering by entity type to narrow results. Each trash item includes the original entity metadata, deletion timestamp, and the user who deleted it.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `entity_type` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_trash.list_project_trash(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```

---

#### `empty_project_trash`

Empty all items from trash
Permanently and irreversibly deletes all items currently in the project trash. For media/file items, also removes the associated files from cloud storage. This operation cannot be undone. Returns the count of permanently deleted items.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_trash.empty_project_trash(
    organization_id="uuid-organization",
    project_id="uuid-project",
)
```


---

### Project Workflows

`gc.project_workflows`

#### `get_workflow_run`

Get a workflow run and its tasks
| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `run_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_workflows.get_workflow_run(
    organization_id="uuid-organization",
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
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `run_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_workflows.dismiss_workflow_run(
    organization_id="uuid-organization",
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
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `type` | `str` | No |
| `created_at` | `str` | No |
| `started_at` | `str` | No |
| `completed_at` | `str` | No |
| `include_dismissed` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.project_workflows.list_workflow_runs(
    organization_id="uuid-organization",
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
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.project_workflows.create_workflow_run(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```


---

### Projects

`gc.projects`

#### `get_project_by_slug`

Get one project from its URL slug, same object as the by-ID lookup
Retrieves the full details of a single project by its URL-friendly slug within the specified organization. This is an alternative to looking up a project by its UUID when you have the human-readable slug from a URL or user input. Returns the same complete project object as the get-by-ID endpoint including name, slug, description, settings, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_slug` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.get_project_by_slug(
    organization_id="uuid-organization",
    project_slug="my-project",
)
```

---

#### `search_sources`

Search project material by meaning, not literal text; returns ranked cited excerpts
Semantic search across all project knowledge — files, pages, posts, KB articles, developer docs, SDK methods, emails, and private CRM data. Returns the most relevant text chunks ranked by similarity, with sourceType and sourceId citations. Use the sourceId with the appropriate get endpoint (getFile, getWebsitePage, etc.) to retrieve the full source document.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `source_type` | `str` | No |
| `source_id` | `str` | No |
| `similarity` | `str` | No |
| `query` | `str` | Yes |
| `limit` | `str` | No |
| `source_types` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.search_sources(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
    query="search term",
)
```

---

#### `list_project_urls`

List resolved paths for all published content, for building links and menus
Returns resolved relative URLs for all published content across all apps in the project. Includes pages, posts, articles, etc. with name, path, type, and SEO metadata. Filter by app or type, search by name or path, and sort by any of them. Used for link resolution in AI builders, menus, emails, and navigation.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `app` | `str` | No |
| `type` | `str` | No |
| `id` | `str` | No |
| `path` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.list_project_urls(
    organization_id="uuid-organization",
    project_id="uuid-project",
    page=1,
)
```

---

#### `get_project`

Get one project's name, slug, description and settings within an organization
Retrieves the full details of a single project by its unique ID within the specified organization. Returns the project's name, slug, description, settings, and timestamps. The project must belong to the specified organization or a 404 error is returned.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.get_project(
    organization_id="uuid-organization",
    project_id="uuid-project",
)
```

---

#### `list_projects`

List projects in an organization; the IDs every project-level tool needs
Returns a paginated list of all projects belonging to the specified organization. Projects are the top-level containers that hold apps, brandings, and domains. Supports search filtering by project name and pagination via page and pageSize query parameters. Each project in the response includes its unique ID, name, slug, description, and timestamps.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `slug` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.projects.list_projects(
    organization_id="uuid-organization",
    page=1,
)
```


---

### Website

`gc.website`

#### `submit_content_to_search_engines`

Ask the search engines to recrawl a page, post, article or doc now
Submits a content item's public URL to IndexNow (Bing, Yandex, Naver, Yep, Seznam) and nudges Google to re-fetch the sitemap. Publishing or editing content already does this automatically — reach for this when something is stale anyway: the page was edited outside the platform's knowledge, a domain was verified after the content went live, or an earlier submission failed. Only web-facing content has a URL to submit: pages, posts, KB articles, developer docs and the landings. Headers, footers, layouts and forms are not submittable because they have no URL of their own, even though editing one changes what a page renders. Drafts are not submitted either.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.submit_content_to_search_engines(
    organization_id="uuid-organization",
    project_id="uuid-project",
    data={...},
)
```

---

#### `get_website_blog_page`

Get the one seeded blog archive page; no create call exists
Returns the app-level website blog archive page rendered at the site's blog root.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_blog_page(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `update_website_blog_page_meta`

Update the blog archive page's name and SEO fields; cannot publish or edit content
Updates the fields that describe the website blog archive page rather than govern it: its internal name, and SEO title, description, image and noindex. Only the fields you send are changed. The archive is the app's blog-root singleton, so it has no slug. Can rebind the layout, header and footer. Cannot change the archive's content or visibility — use the block tools for content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.update_website_blog_page_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_consent_settings`

Get the cookie banner copy, category toggles and policy links
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

Get one dialog with its full block tree, max width and close control
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

#### `delete_website_dialog`

Delete dialog
Permanently deletes a website dialog.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `dialog_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.delete_website_dialog(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    dialog_id="uuid-dialog",
)
```

---

#### `list_website_dialogs`

List popup dialogs (modals, banners, slide-ins) in a site, newest first
Returns a list of all popup dialogs configured for this website app. Dialogs are used for modals, popups, banners, and slide-ins.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `max_width` | `str` | No |
| `include_close` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

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

#### `create_website_dialog`

Create a popup dialog; nothing shows it until a button links dialog:{id}
Creates a new popup dialog for this website app.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.website.create_website_dialog(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_custom_domain`

Get one domain with its verification token, verified state and primary flag
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

List a site's custom domains, primary first, with verified state and verification token
Returns a list of all custom domains configured for this website app, including verification status, SSL status, and whether each is the primary domain. The primary domain comes first unless a sort is requested, over domain, isPrimary, isVerified, isGenerated, createdAt or updatedAt.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `is_primary` | `str` | No |
| `is_verified` | `str` | No |
| `is_generated` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_custom_domains(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_footer`

Get one footer with its full block tree, which lite listings omit
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

#### `delete_website_footer`

Delete website footer
Permanently deletes a website footer component.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `footer_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.delete_website_footer(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    footer_id="uuid-footer",
)
```

---

#### `list_website_footers`

List a site's footers newest first, each with its block tree unless lite
Returns a list of all footer components for this website app. Footers are reusable layout sections displayed at the bottom of pages.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

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

#### `create_website_footer`

Create a reusable footer shell; pages attach it by id, content optional
Creates a new footer component for this website app.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.website.create_website_footer(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_header`

Get one header with its full block tree, which lite listings omit
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

#### `delete_website_header`

Delete website header
Permanently deletes a website header component.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `header_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.delete_website_header(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    header_id="uuid-header",
)
```

---

#### `list_website_headers`

List a site's headers newest first, each with its block tree unless lite
Returns a list of all header components for this website app. Headers are reusable navigation/branding sections displayed at the top of pages.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

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

#### `create_website_header`

Create a reusable header shell; pages attach it by id, content optional
Creates a new header component for this website app.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.website.create_website_header(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_landing`

Get the one seeded page at the site root; no create call exists
Returns the app-level website landing page rendered at the website root.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_landing(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `update_website_landing_meta`

Update the landing page's name and SEO fields; cannot publish or edit content
Updates the fields that describe the website landing page rather than govern it: its internal name, and SEO title, description, image and noindex. Only the fields you send are changed. A landing is the app's root singleton, so it has no slug and no title. Can rebind the layout, header and footer. Cannot change the landing's content or visibility — use the block tools for content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.update_website_landing_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_layout`

Get one layout with its full block tree, which lite listings omit
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

#### `delete_website_layout`

Delete website layout
Permanently deletes a website page layout.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `layout_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.delete_website_layout(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    layout_id="uuid-layout",
)
```

---

#### `list_website_layouts`

List page layouts you can apply when creating a page, newest first
Returns a list of all page layouts for this website app. Layouts provide reusable page layouts and content block structures.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

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

#### `create_website_layout`

Create a layout shell; pages set layoutId to share its block tree
Creates a new page layout for this website app.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.website.create_website_layout(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_not_found_page`

Get the one seeded not found page; no create call exists
Returns the app-level website not found page, rendered on any unresolved path.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_not_found_page(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `update_website_not_found_page_meta`

Update the not found page's name and SEO fields; cannot publish or edit content
Updates the fields that describe the website not found page rather than govern it: its internal name, and SEO title, description, image and noindex. Only the fields you send are changed. The 404 is the app's not-found singleton, so it has no slug. Can rebind the layout, header and footer. Cannot change the page's content or visibility — use the block tools for content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.update_website_not_found_page_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_page`

Get one page with its full block tree, SEO, status and layout ids
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

#### `delete_website_page`

Delete website page
Soft-deletes a website page by moving it to the project trash. Can be restored from trash later.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.delete_website_page(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page_id="uuid-page",
)
```

---

#### `update_website_page_meta`

Update a page's name, title, slug, SEO fields, featured image and tags; cannot publish or edit content
Updates the fields that describe a page rather than govern it: SEO title, description, image, noindex, featured image, and tags. Only the fields you send are changed. Can rebind the layout, header and footer. Cannot change the page's content, status or visibility — use the block tools for content and publishContent to take it live.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.update_website_page_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page_id="uuid-page",
    data={...},
)
```

---

#### `list_website_pages`

List a site's pages with slug, live URL and publish status, newest first
Returns a list of all pages for this website app. Each page includes its title, slug, publish status, SEO metadata, and associated header/footer/sidebar references.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `slug` | `str` | No |
| `is_listed` | `str` | No |
| `layout_id` | `str` | No |
| `header_id` | `str` | No |
| `footer_id` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_pages(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `create_website_page`

Create a page shell; content optional and status defaults to published, live immediately
Creates a new website page. Requires a title. Optionally set slug, content blocks, SEO metadata, header, footer, and sidebar references.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.website.create_website_page(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_post`

Get one blog post with its full content blocks, tags and SEO fields
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

#### `delete_website_post`

Delete blog post
Soft-deletes a blog post by moving it to the project trash. Can be restored from trash later.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `post_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.delete_website_post(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    post_id="uuid-post",
)
```

---

#### `update_website_post_meta`

Update a post's name, title, slug, excerpt, author, publish date, tags and SEO, not its content
Updates the fields that describe a post rather than govern it: SEO title and description, excerpt, author name, publish date, tags and featured image. Only the fields you send are changed. Can rebind the layout, header and footer. Cannot change the post's content or status — use the block tools for content and publishContent to take it live.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `post_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.update_website_post_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    post_id="uuid-post",
    data={...},
)
```

---

#### `list_website_posts`

List blog posts in a site, newest first, with author, tags and status
Returns a paginated list of all blog posts for this website app. Each post includes title, slug, excerpt, publish status, author, tags, and featured image.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `status` | `str` | No |
| `slug` | `str` | No |
| `is_listed` | `str` | No |
| `author_id` | `str` | No |
| `author_name` | `str` | No |
| `publish_date` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_posts(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `create_website_post`

Create a blog post; status defaults to draft, unlike createWebsitePage
Creates a new blog post. Requires a name and slug. Optionally set content blocks, excerpt, tags, featured image, SEO metadata, and publish status.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.website.create_website_post(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_redirect`

Get one URL redirect by id
Returns a single URL redirect by ID, including its fromPath, toPath, status and source.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `redirect_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_redirect(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    redirect_id="uuid-redirect",
)
```

---

#### `list_website_redirects`

List a site's URL redirects, newest first, with from, to, status and source
Returns a paginated list of the URL redirects for this website app. Each maps an old path (fromPath) to the current path (toPath) with a status (301 or 308) and a source: auto (recorded when a slug changed) or manual (added by hand).

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `source` | `str` | No |
| `status` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_redirects(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_sidebar`

Get one sidebar with its full block tree, which lite listings omit
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

#### `delete_website_sidebar`

Delete website sidebar
Permanently deletes a website sidebar component.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `sidebar_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.delete_website_sidebar(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    sidebar_id="uuid-sidebar",
)
```

---

#### `list_website_sidebars`

List a site's sidebars newest first, each with its block tree unless lite
Returns a list of all sidebar components for this website app. Sidebars are reusable layout sections displayed alongside page content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `name` | `str` | No |
| `created_at` | `str` | No |
| `updated_at` | `str` | No |

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

#### `create_website_sidebar`

Create a reusable sidebar shell; a layoutSidebar block points at it by id
Creates a new sidebar component for this website app.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

```python
result = await gc.website.create_website_sidebar(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `get_website_sign_in_page`

Get the one seeded not found page; no create call exists
Returns the app-level website not found page, rendered on any unresolved path.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_sign_in_page(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `update_website_sign_in_page_meta`

Update the not found page's name and SEO fields; cannot publish or edit content
Updates the fields that describe the website not found page rather than govern it: its internal name, and SEO title, description, image and noindex. Only the fields you send are changed. The 404 is the app's not-found singleton, so it has no slug. Can rebind the layout, header and footer. Cannot change the page's content or visibility — use the block tools for content.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |
| `draft_id` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.update_website_sign_in_page_meta(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

---

#### `list_website_tags`

List the tag names in use across a site's pages and posts
Returns a list of all tags used across pages and posts in this website app. Tags are used for categorization and filtering.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |
| `sort` | `str` | No |
| `search` | `str` | No |
| `tag` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_tags(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `get_website_tracking_settings`

Get the site's Google Tag Manager container ID, the only tracking setting
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

Get existing page slugs and each page's layout, to avoid duplicate slugs
Returns existing page slugs (to avoid duplicate URLs) and per-page entries with the layout each page uses (the builder's peer-usage signal for layout selection).

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

---

#### `get_website_viewer_auth`

Whether this site's private pages have members, and which tenant
Returns whether viewer sign-in is enabled for this website app and the identity tenant holding its viewers. The tenant id is not a secret — it is compared against a session's claim, never used to mint one.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.get_website_viewer_auth(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
)
```

---

#### `remove_website_viewer`

Remove somebody's access to this website's gated content
Deletes the member's account in the site's identity tenant. DOES NOT END A LIVE SESSION: a session cookie is a signed token the edge verifies on its own and never checks against the provider, so somebody already signed in keeps reading until their token expires, within the hour. Re-inviting the same address afterwards creates a new account rather than restoring this one.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `uid` | `str` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.remove_website_viewer(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    uid="value",
)
```

---

#### `list_website_viewers`

List the people who can read this website's gated content
Returns the site's members — the viewers who can read pages and posts marked as requiring sign-in. Read from the site's identity tenant rather than from a table, so it reflects what can actually sign in rather than a copy that could disagree. hasSignedIn is false for somebody who has been invited but has not followed the link yet.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `page` | `str` | No |
| `page_size` | `str` | No |
| `lite` | `str` | No |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.list_website_viewers(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    page=1,
)
```

---

#### `invite_website_viewer`

Invite somebody to read this website's gated content
Creates an account in the site's identity tenant and emails a sign-in link. NO PASSWORD IS SET: the link signs them in, once, and the identity provider owns its expiry. Inviting somebody who already has an account sends a fresh link rather than failing, which is how an expired invitation is repaired. Invited people can read every gated page on this site and nothing else — they are not Giant Context users and hold no permissions.

| Parameter | Type | Required |
|-----------|------|----------|
| `organization_id` | `str` | Yes |
| `project_id` | `str` | Yes |
| `app_id` | `str` | Yes |
| `data` | `dict` | Yes |

**Returns:** `dict[str, Any]`

```python
result = await gc.website.invite_website_viewer(
    organization_id="uuid-organization",
    project_id="uuid-project",
    app_id="uuid-app",
    data={...},
)
```

<!-- API_REFERENCE_END -->

## Requirements

- Python 3.11+
- [httpx](https://www.python-httpx.org/)

## License

MIT
