"""Real integration handlers — execute tools against actual services.

Each handler receives (integration_config, tool_inputs) and returns a ToolResult.
This is the pluggable layer that replaces mock implementations when a tool has
integration credentials configured.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
from typing import Any
from urllib.parse import urljoin

import httpx

from app.schemas.tool import ToolResult

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _mask(value: str | None) -> str | None:
    """Mask a credential value for safe logging / display."""
    if not value or len(value) <= 4:
        return "***"
    return "***" + value[-2:]


def _mask_credentials(config: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of integration_config with credential values masked."""
    mask_keys = {
        "api_key", "bearer_token", "password", "smtp_password",
        "secret_key", "bot_token", "secret", "access_key",
        "connection_string",
    }
    masked = dict(config)
    for key in list(masked.keys()):
        if key in mask_keys:
            masked[key] = _mask(str(masked.get(key, "")))
    # Mask credentials sub-dict
    if "credentials" in masked and isinstance(masked["credentials"], dict):
        masked["credentials"] = {
            k: _mask(str(v)) for k, v in masked["credentials"].items()
        }
    return masked


async def _run_sync(func, *args, **kwargs):
    """Run a synchronous function in a thread to avoid blocking the event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


# ──────────────────────────────────────────────
# Integration Handler
# ──────────────────────────────────────────────

class IntegrationHandler:
    """Dispatches tool execution to real service handlers based on integration config."""

    def __init__(self):
        self._http_client: httpx.AsyncClient | None = None

    async def execute(
        self, integration_config: dict[str, Any], tool_inputs: dict[str, Any]
    ) -> ToolResult:
        """Execute a tool against a real service.

        Args:
            integration_config: The integration config dict (connection details).
            tool_inputs: The tool call inputs from the workflow node.

        Returns:
            ToolResult with success/output/error.
        """
        itype = integration_config.get("integration_type", "custom")

        handlers = {
            "http": self._handle_http,
            "email_smtp": self._handle_email_smtp,
            "email_api": self._handle_email_api,
            "database": self._handle_database,
            "messaging_slack": self._handle_messaging_slack,
            "storage_s3": self._handle_storage_s3,
        }
        handler = handlers.get(itype)
        if not handler:
            return ToolResult(
                success=False,
                error=f"Unknown integration type: {itype}",
                retryable=False,
            )

        try:
            return await handler(integration_config, tool_inputs)
        except Exception as exc:
            logger.error(
                "Integration error [%s]: %s",
                itype,
                exc,
                extra={"config": _mask_credentials(integration_config)},
            )
            return ToolResult(success=False, error=str(exc), retryable=True)

    # ── HTTP ──────────────────────────────────

    async def _handle_http(
        self, config: dict[str, Any], inputs: dict[str, Any]
    ) -> ToolResult:
        """Make an HTTP request to a configured API endpoint."""
        base_url = config.get("base_url", "").rstrip("/")
        if not base_url:
            return ToolResult(success=False, error="Missing 'base_url' in integration config", retryable=False)

        url = inputs.get("url", "")
        if not url:
            return ToolResult(success=False, error="Missing 'url' in tool inputs", retryable=False)

        # Support relative paths
        if not url.startswith("http"):
            url = urljoin(base_url + "/", url.lstrip("/"))

        method = inputs.get("method", "GET").upper()
        headers = dict(config.get("default_headers", {}) or {})
        headers.update(inputs.get("headers", {}) or {})

        # Auth
        auth_type = config.get("auth_type", "none")
        creds = config.get("credentials", {}) or {}
        if auth_type == "bearer" and creds.get("bearer_token"):
            headers["Authorization"] = f"Bearer {creds['bearer_token']}"
        elif auth_type == "api_key" and creds.get("api_key"):
            api_key_header = config.get("api_key_header", "X-API-Key")
            headers[api_key_header] = creds["api_key"]
        elif auth_type == "basic":
            user = creds.get("username", "")
            pwd = creds.get("password", "")
            import base64
            headers["Authorization"] = "Basic " + base64.b64encode(f"{user}:{pwd}".encode()).decode()

        body = inputs.get("body")
        timeout = config.get("timeout_seconds", 30)

        try:
            client = self._get_http_client()
            response = await client.request(
                method, url, headers=headers,
                json=body if isinstance(body, (dict, list)) else None,
                content=body if isinstance(body, str) else None,
                timeout=timeout,
            )
        except httpx.TimeoutException:
            return ToolResult(success=False, error=f"Request timed out after {timeout}s", retryable=True)
        except httpx.ConnectError as exc:
            return ToolResult(success=False, error=f"Connection failed: {exc}", retryable=True)
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), retryable=True)

        # Parse response
        response_body = None
        try:
            response_body = response.json()
        except (json.JSONDecodeError, ValueError):
            response_body = response.text

        success = response.is_success
        logger.debug(
            "HTTP %s %s -> %d", method, url, response.status_code,
            extra={"integration_type": "http", "url": url, "status": response.status_code},
        )

        return ToolResult(
            success=success,
            output={
                "status_code": response.status_code,
                "body": response_body,
                "headers": dict(response.headers),
                "url": str(response.url),
            },
            error=None if success else f"HTTP {response.status_code}: {response.text[:500]}",
            retryable=response.status_code >= 500,
        )

    # ── Email (SMTP) ──────────────────────────

    async def _handle_email_smtp(
        self, config: dict[str, Any], inputs: dict[str, Any]
    ) -> ToolResult:
        """Send an email via SMTP."""
        try:
            import aiosmtplib
        except ImportError:
            return ToolResult(
                success=False,
                error="aiosmtplib not installed. Run: pip install aiosmtplib",
                retryable=False,
            )

        smtp_host = config.get("smtp_host", "")
        smtp_port = config.get("smtp_port", 587)
        smtp_user = config.get("smtp_user", "")
        smtp_password = config.get("smtp_password", "")
        from_address = config.get("from_address", smtp_user)
        use_tls = config.get("use_tls", True)

        to = inputs.get("to") or inputs.get("to_address", "")
        subject = inputs.get("subject", "")
        body = inputs.get("body") or inputs.get("content", "")

        if not to:
            return ToolResult(success=False, error="Missing 'to' address", retryable=False)
        if not smtp_host:
            return ToolResult(success=False, error="Missing 'smtp_host' in integration config", retryable=False)

        from email.message import EmailMessage
        message = EmailMessage()
        message["From"] = from_address
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_user,
                password=smtp_password,
                use_tls=use_tls,
            )
        except aiosmtplib.SMTPAuthenticationError:
            return ToolResult(success=False, error="SMTP authentication failed — check credentials", retryable=False)
        except aiosmtplib.SMTPConnectError as exc:
            return ToolResult(success=False, error=f"SMTP connection failed: {exc}", retryable=True)
        except Exception as exc:
            return ToolResult(success=False, error=f"SMTP send failed: {exc}", retryable=True)

        logger.debug("SMTP email sent to %s via %s:%d", to, smtp_host, smtp_port)
        return ToolResult(success=True, output={"sent": True, "to": to, "subject": subject})

    # ── Email (API) ───────────────────────────

    async def _handle_email_api(
        self, config: dict[str, Any], inputs: dict[str, Any]
    ) -> ToolResult:
        """Send email via an API provider (SendGrid, Mailgun, Postmark)."""
        base_url = config.get("api_endpoint", "")
        api_key = config.get("api_key", "")
        provider = config.get("provider", "sendgrid")

        if not base_url or not api_key:
            return ToolResult(
                success=False,
                error="Missing 'api_endpoint' or 'api_key' in integration config",
                retryable=False,
            )

        to = inputs.get("to", "")
        subject = inputs.get("subject", "")
        body = inputs.get("body", "")

        # Build provider-specific payload
        if provider == "sendgrid":
            payload = {
                "personalizations": [{"to": [{"email": to}], "subject": subject}],
                "from": {"email": config.get("from_address", "")},
                "content": [{"type": "text/plain", "value": body}],
            }
        elif provider == "mailgun":
            payload = {"from": config.get("from_address", ""), "to": to, "subject": subject, "text": body}
        else:
            payload = {"to": to, "subject": subject, "body": body}

        try:
            client = self._get_http_client()
            response = await client.post(
                base_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), retryable=True)

        body_out = None
        try:
            body_out = response.json()
        except (json.JSONDecodeError, ValueError):
            body_out = response.text

        return ToolResult(
            success=response.is_success,
            output={"status_code": response.status_code, "body": body_out},
            error=None if response.is_success else f"HTTP {response.status_code}: {response.text[:500]}",
            retryable=response.status_code >= 500,
        )

    # ── Database ──────────────────────────────

    async def _handle_database(
        self, config: dict[str, Any], inputs: dict[str, Any]
    ) -> ToolResult:
        """Query a real database using async drivers."""
        driver = config.get("driver", "")
        connection_string = config.get("connection_string", "")

        if not connection_string:
            return ToolResult(success=False, error="Missing 'connection_string' in integration config", retryable=False)

        query = inputs.get("query", inputs.get("sql", ""))
        if not query:
            return ToolResult(success=False, error="Missing 'query' or 'sql' in tool inputs", retryable=False)

        # Detect driver from connection string if not explicit
        if not driver:
            if connection_string.startswith("postgresql"):
                driver = "postgresql"
            elif connection_string.startswith("mysql"):
                driver = "mysql"
            elif connection_string.startswith("sqlite"):
                driver = "sqlite"

        if driver == "postgresql":
            return await self._db_postgresql(connection_string, query, inputs)
        elif driver == "mysql":
            return await self._db_mysql(connection_string, query, inputs)
        elif driver == "sqlite":
            return await self._db_sqlite(connection_string, query, inputs)
        else:
            return ToolResult(success=False, error=f"Unsupported database driver: {driver}", retryable=False)

    async def _db_postgresql(self, conn_str: str, query: str, inputs: dict) -> ToolResult:
        try:
            import asyncpg
        except ImportError:
            return ToolResult(success=False, error="asyncpg not installed. Run: pip install asyncpg", retryable=False)

        # Sanitize: only allow SELECT and WITH (read-only)
        q_lower = query.strip().lower()
        if not (q_lower.startswith("select") or q_lower.startswith("with")):
            return ToolResult(success=False, error="Only SELECT queries are allowed in workflow tools", retryable=False)

        try:
            conn = await asyncpg.connect(conn_str)
            try:
                rows = await conn.fetch(query)
                records = [dict(r) for r in rows]
                count = len(records)
            finally:
                await conn.close()
        except ImportError:
            return ToolResult(success=False, error="asyncpg not installed", retryable=False)
        except Exception as exc:
            return ToolResult(success=False, error=f"Database query failed: {exc}", retryable=True)

        return ToolResult(success=True, output={"records": records, "count": count})

    async def _db_mysql(self, conn_str: str, query: str, inputs: dict) -> ToolResult:
        try:
            import aiomysql
        except ImportError:
            return ToolResult(success=False, error="aiomysql not installed. Run: pip install aiomysql", retryable=False)

        q_lower = query.strip().lower()
        if not (q_lower.startswith("select") or q_lower.startswith("with")):
            return ToolResult(success=False, error="Only SELECT queries are allowed", retryable=False)

        try:
            conn = await aiomysql.connect(conn_str)
            try:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(query)
                    rows = await cur.fetchall()
                    count = len(rows) if rows else 0
            finally:
                conn.close()
        except ImportError:
            return ToolResult(success=False, error="aiomysql not installed", retryable=False)
        except Exception as exc:
            return ToolResult(success=False, error=f"Database query failed: {exc}", retryable=True)

        return ToolResult(success=True, output={"records": rows or [], "count": count})

    async def _db_sqlite(self, conn_str: str, query: str, inputs: dict) -> ToolResult:
        import sqlite3
        import asyncio

        # Extract path from connection string like sqlite:///path or sqlite:///relative
        db_path = conn_str.replace("sqlite:///", "").replace("sqlite://", "")

        def _query():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            try:
                cur = conn.execute(query)
                rows = [dict(r) for r in cur.fetchall()]
                count = len(rows)
                return rows, count, None
            except Exception as exc:
                return None, 0, str(exc)
            finally:
                conn.close()

        rows, count, error = await _run_sync(_query)
        if error:
            return ToolResult(success=False, error=f"SQLite query failed: {error}", retryable=False)

        return ToolResult(success=True, output={"records": rows, "count": count})

    # ── Messaging (Slack) ─────────────────────

    async def _handle_messaging_slack(
        self, config: dict[str, Any], inputs: dict[str, Any]
    ) -> ToolResult:
        """Send a message to Slack via the Web API."""
        bot_token = config.get("bot_token", "")
        if not bot_token:
            return ToolResult(success=False, error="Missing 'bot_token' in integration config", retryable=False)

        channel = inputs.get("channel") or inputs.get("channel_id", "")
        text = inputs.get("message") or inputs.get("text", "")
        if not channel:
            return ToolResult(success=False, error="Missing 'channel' in tool inputs", retryable=False)

        payload = {"channel": channel, "text": text}
        if inputs.get("blocks"):
            payload["blocks"] = inputs["blocks"]

        try:
            client = self._get_http_client()
            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                json=payload,
                headers={"Authorization": f"Bearer {bot_token}", "Content-Type": "application/json"},
                timeout=30,
            )
            body = response.json()
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), retryable=True)

        if not body.get("ok"):
            return ToolResult(success=False, error=body.get("error", "Slack API error"), retryable=False)

        return ToolResult(success=True, output={"ts": body.get("ts"), "channel": channel, "message_id": body.get("message", {}).get("ts")})

    # ── Storage (S3) ──────────────────────────

    async def _handle_storage_s3(
        self, config: dict[str, Any], inputs: dict[str, Any]
    ) -> ToolResult:
        """Interact with S3-compatible storage."""
        try:
            import boto3
            from botocore.exceptions import ClientError, BotoCoreError
        except ImportError:
            return ToolResult(success=False, error="boto3 not installed. Run: pip install boto3", retryable=False)

        access_key = config.get("access_key", "")
        secret_key = config.get("secret_key", "")
        bucket = config.get("bucket", "")
        region = config.get("region", "us-east-1")
        endpoint_url = config.get("endpoint_url")  # For non-AWS S3 (MinIO, etc.)

        if not access_key or not secret_key or not bucket:
            return ToolResult(success=False, error="Missing 'access_key', 'secret_key', or 'bucket' in config", retryable=False)

        action = inputs.get("action", "get_object")  # get_object, put_object, list_objects, delete_object
        key = inputs.get("key", inputs.get("filename", ""))
        content = inputs.get("content", inputs.get("body", ""))

        def _s3_call():
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
            s3 = session.client("s3", endpoint_url=endpoint_url)

            if action == "list_objects":
                resp = s3.list_objects_v2(Bucket=bucket, Prefix=inputs.get("prefix", ""))
                objects = [
                    {"key": o["Key"], "size": o["Size"], "modified": str(o["LastModified"])}
                    for o in resp.get("Contents", [])
                ]
                return {"objects": objects, "count": len(objects)}

            elif action == "get_object":
                if not key:
                    raise ValueError("Missing 'key' for get_object")
                resp = s3.get_object(Bucket=bucket, Key=key)
                body = resp["Body"].read()
                try:
                    parsed = json.loads(body)
                    return {"key": key, "content": parsed, "size": len(body)}
                except (json.JSONDecodeError, ValueError):
                    return {"key": key, "content": body.decode("utf-8", errors="replace"), "size": len(body)}

            elif action == "put_object":
                if not key:
                    raise ValueError("Missing 'key' for put_object")
                body = content.encode("utf-8") if isinstance(content, str) else content
                s3.put_object(Bucket=bucket, Key=key, Body=body)
                return {"key": key, "size": len(body), "bucket": bucket}

            elif action == "delete_object":
                if not key:
                    raise ValueError("Missing 'key' for delete_object")
                s3.delete_object(Bucket=bucket, Key=key)
                return {"key": key, "deleted": True, "bucket": bucket}

            else:
                raise ValueError(f"Unsupported S3 action: {action}")

        try:
            result = await _run_sync(_s3_call)
        except ImportError:
            return ToolResult(success=False, error="boto3 not installed", retryable=False)
        except Exception as exc:
            return ToolResult(success=False, error=f"S3 operation failed: {exc}", retryable=True)

        return ToolResult(success=True, output=result)

    # ── Internal ──────────────────────────────

    def _get_http_client(self) -> httpx.AsyncClient:
        """Lazy-init and reuse the HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(follow_redirects=True)
        return self._http_client

    async def close(self):
        """Clean up resources."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

# Singleton — reused across tool executions
integration_handler = IntegrationHandler()
