---
type: community
cohesion: 0.10
members: 26
---

# Integration Tests

**Cohesion:** 0.10 - loosely connected
**Members:** 26 nodes

## Members
- [[dot-test_database_without_connection_string_returns_failure()]] - code - backend/tests/test_integrations.py
- [[dot-test_dispatches_to_aws_s3()]] - code - backend/tests/test_integrations.py
- [[dot-test_dispatches_to_database()]] - code - backend/tests/test_integrations.py
- [[dot-test_dispatches_to_email_smtp()]] - code - backend/tests/test_integrations.py
- [[dot-test_dispatches_to_http_webhook()]] - code - backend/tests/test_integrations.py
- [[dot-test_dispatches_to_slack()]] - code - backend/tests/test_integrations.py
- [[dot-test_http_connection_error_is_retryable()]] - code - backend/tests/test_integrations.py
- [[dot-test_http_without_base_url_returns_failure()]] - code - backend/tests/test_integrations.py
- [[dot-test_integration_handler_returns_tool_result()]] - code - backend/tests/test_integrations.py
- [[dot-test_tool_model_has_integration_config_field()]] - code - backend/tests/test_integrations.py
- [[dot-test_unknown_type_returns_failure()]] - code - backend/tests/test_integrations.py
- [[AWS S3 handler lists objects.]] - rationale - backend/tests/test_integrations.py
- [[Connection errors are marked as retryable.]] - rationale - backend/tests/test_integrations.py
- [[CustomTool model has integration_config column for real execution.]] - rationale - backend/tests/test_integrations.py
- [[Database handler queries via connection string.]] - rationale - backend/tests/test_integrations.py
- [[HTTP handler sends request to configured base_url + url.]] - rationale - backend/tests/test_integrations.py
- [[Missing base_url returns a clear error.]] - rationale - backend/tests/test_integrations.py
- [[Missing connection_string returns a clear error.]] - rationale - backend/tests/test_integrations.py
- [[SMTP handler sends email via aiosmtplib.]] - rationale - backend/tests/test_integrations.py
- [[Slack messaging handler posts messages via Web API.]] - rationale - backend/tests/test_integrations.py
- [[TestIntegrationHandler]] - code - backend/tests/test_integrations.py
- [[TestRealExecution]] - code - backend/tests/test_integrations.py
- [[Tests that the workflow runner uses real integrations when configured.]] - rationale - backend/tests/test_integrations.py
- [[Unknown integration type returns failure.]] - rationale - backend/tests/test_integrations.py
- [[asyncio]] - code
- [[integration_handler.execute returns a ToolResult.]] - rationale - backend/tests/test_integrations.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Integration_Tests
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Integration Tool Tests]]
- 1 edge to [[_COMMUNITY_Custom Tools API]]
- 1 edge to [[_COMMUNITY_Community 22]]

## Top bridge nodes
- [[TestRealExecution]] - degree 8, connects to 3 communities
- [[TestIntegrationHandler]] - degree 8, connects to 1 community