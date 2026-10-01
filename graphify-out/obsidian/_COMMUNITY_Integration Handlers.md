---
type: community
cohesion: 0.10
members: 29
---

# Integration Handlers

**Cohesion:** 0.10 - loosely connected
**Members:** 29 nodes

## Members
- [[dot-__init__()_16]] - code - backend/app/tools/integrations.py
- [[dot-_db_mysql()]] - code - backend/app/tools/integrations.py
- [[dot-_db_postgresql()]] - code - backend/app/tools/integrations.py
- [[dot-_db_sqlite()]] - code - backend/app/tools/integrations.py
- [[dot-_get_http_client()]] - code - backend/app/tools/integrations.py
- [[dot-_handle_database()]] - code - backend/app/tools/integrations.py
- [[dot-_handle_email_api()]] - code - backend/app/tools/integrations.py
- [[dot-_handle_email_smtp()]] - code - backend/app/tools/integrations.py
- [[dot-_handle_http()]] - code - backend/app/tools/integrations.py
- [[dot-_handle_messaging_slack()]] - code - backend/app/tools/integrations.py
- [[dot-_handle_storage_s3()]] - code - backend/app/tools/integrations.py
- [[dot-close()]] - code - backend/app/tools/integrations.py
- [[dot-execute()_1]] - code - backend/app/tools/integrations.py
- [[Any_10]] - code
- [[AsyncClient]] - code
- [[Dispatches tool execution to real service handlers based on integration config.]] - rationale - backend/app/tools/integrations.py
- [[Execute a tool against a real service. Args integration_config The…]] - rationale - backend/app/tools/integrations.py
- [[IntegrationHandler]] - code - backend/app/tools/integrations.py
- [[Interact with S3-compatible storage.]] - rationale - backend/app/tools/integrations.py
- [[Lazy-init and reuse the HTTP client.]] - rationale - backend/app/tools/integrations.py
- [[Make an HTTP request to a configured API endpoint.]] - rationale - backend/app/tools/integrations.py
- [[Query a real database using async drivers.]] - rationale - backend/app/tools/integrations.py
- [[Run a synchronous function in a thread to avoid blocking the event loop.]] - rationale - backend/app/tools/integrations.py
- [[Send a message to Slack via the Web API.]] - rationale - backend/app/tools/integrations.py
- [[Send an email via SMTP.]] - rationale - backend/app/tools/integrations.py
- [[Send email via an API provider (SendGrid, Mailgun, Postmark).]] - rationale - backend/app/tools/integrations.py
- [[_query()]] - code - backend/app/tools/integrations.py
- [[_run_sync()]] - code - backend/app/tools/integrations.py
- [[_s3_call()]] - code - backend/app/tools/integrations.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Integration_Handlers
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Community 22]]
- 4 edges to [[_COMMUNITY_Integration Tool Tests]]

## Top bridge nodes
- [[IntegrationHandler]] - degree 16, connects to 2 communities
- [[dot-execute()_1]] - degree 5, connects to 2 communities
- [[Any_10]] - degree 8, connects to 1 community
- [[dot-_handle_database()]] - degree 7, connects to 1 community
- [[dot-_handle_storage_s3()]] - degree 6, connects to 1 community