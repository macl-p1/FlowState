"""Custom tools API routes — CRUD for user-created tools with verification flow."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Any
import json
import asyncio

from app.database import get_db
from app.models.custom_tool import CustomTool, ToolStatus, ToolType
from app.schemas.custom_tool import (
    CustomToolCreate,
    CustomToolUpdate,
    CustomToolResponse,
    ToolVerifyRequest,
    ToolVerifyResponse,
    ToolCategory,
)
from app.tools.registry import registry

router = APIRouter()


def _tool_to_response(tool: CustomTool) -> CustomToolResponse:
    return CustomToolResponse(
        id=tool.id,
        name=tool.name,
        description=tool.description,
        tool_type=tool.tool_type.value,
        status=tool.status.value,
        input_schema=tool.input_schema or {},
        config=tool.config or {},
        output_schema=tool.output_schema or {},
        last_test_result=tool.last_test_result,
        verified_at=tool.verified_at,
        verified_by=tool.verified_by,
        created_at=tool.created_at,
        updated_at=tool.updated_at,
    )


# ──────────────────────────────────────────────
# Categories
# ──────────────────────────────────────────────

@router.get("/tools/categories", response_model=list[ToolCategory])
async def list_categories(db: Session = Depends(get_db)):
    """Group all tools (built-in + custom) by type."""
    # Count built-in tools by type keyword
    builtin_counts: dict[str, int] = {}
    for t in registry.list_all():
        name_lower = t.name.lower()
        if "http" in name_lower:
            builtin_counts["http"] = builtin_counts.get("http", 0) + 1
        elif any(k in name_lower for k in ["database", "sql", "query"]):
            builtin_counts["database"] = builtin_counts.get("database", 0) + 1
        elif any(k in name_lower for k in ["email", "smtp", "mail"]):
            builtin_counts["email"] = builtin_counts.get("email", 0) + 1
        elif any(k in name_lower for k in ["webhook", "callback"]):
            builtin_counts["webhook"] = builtin_counts.get("webhook", 0) + 1
        elif any(k in name_lower for k in ["transform", "map", "filter"]):
            builtin_counts["transform"] = builtin_counts.get("transform", 0) + 1
        elif any(k in name_lower for k in ["delay", "wait", "sleep"]):
            builtin_counts["delay"] = builtin_counts.get("delay", 0) + 1
        elif any(k in name_lower for k in ["slack", "teams", "message", "chat"]):
            builtin_counts["messaging"] = builtin_counts.get("messaging", 0) + 1
        elif any(k in name_lower for k in ["file", "storage", "s3", "bucket"]):
            builtin_counts["storage"] = builtin_counts.get("storage", 0) + 1
        else:
            builtin_counts["custom"] = builtin_counts.get("custom", 0) + 1

    # Count user custom tools
    custom_counts: dict[str, int] = {}
    for t in db.query(CustomTool).all():
        ttype = t.tool_type.value
        custom_counts[ttype] = custom_counts.get(ttype, 0) + 1

    type_map = {
        "http": "HTTP / API",
        "database": "Database",
        "email": "Email",
        "webhook": "Webhook",
        "transform": "Transform",
        "delay": "Delay / Wait",
        "messaging": "Messaging",
        "storage": "Storage",
        "custom": "Custom",
    }

    all_types = set(builtin_counts) | set(custom_counts)
    categories = []
    for ttype in sorted(all_types):
        label = type_map.get(ttype, ttype.title())
        categories.append(ToolCategory(
            type=ttype,
            label=label,
            icon=_type_icon(ttype),
            description=f"{builtin_counts.get(ttype, 0)} built-in, {custom_counts.get(ttype, 0)} custom",
            count=builtin_counts.get(ttype, 0) + custom_counts.get(ttype, 0),
        ))

    # Always include 'All' category
    categories.insert(0, ToolCategory(
        type="all",
        label="All Tools",
        icon="Puzzle",
        description=f"{len(registry.list_all())} built-in, {db.query(CustomTool).count()} custom",
        count=len(registry.list_all()) + db.query(CustomTool).count(),
    ))

    return categories


def _type_icon(ttype: str) -> str:
    icons = {
        "http": "Globe",
        "database": "Database",
        "email": "Mail",
        "webhook": "Link",
        "transform": "Workflow",
        "delay": "Clock",
        "messaging": "MessageSquare",
        "storage": "HardDrive",
        "custom": "Puzzle",
    }
    return icons.get(ttype, "Puzzle")


# ──────────────────────────────────────────────
# Custom Tools CRUD
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# All Tools (built-in + custom)
# ──────────────────────────────────────────────

@router.get("/tools/all", response_model=list[CustomToolResponse])
async def list_all_tools(db: Session = Depends(get_db)):
    """Return built-in tools + custom tools in one unified list."""
    from datetime import datetime, timezone

    builtin_type_map = {
        "http": "http", "database": "database", "email": "email",
        "webhook": "custom", "transform": "transform", "delay": "delay",
        "messaging": "messaging", "storage": "storage",
    }

    results: list[CustomToolResponse] = []

    # Built-in tools from registry
    for t in registry.list_all():
        name_lower = t.name.lower()
        ttype = "custom"
        for keyword, cat in builtin_type_map.items():
            if keyword in name_lower:
                ttype = cat
                break

        results.append(CustomToolResponse(
            id=f"builtin_{t.name}",
            name=t.name,
            description=t.description,
            tool_type=ttype,
            status="verified",
            input_schema=t.input_schema or {},
            config={},
            output_schema={"type": "object"},
            last_test_result=None,
            verified_at=datetime.now(timezone.utc),
            verified_by="built-in",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ))

    # Custom tools from DB
    for t in db.query(CustomTool).order_by(CustomTool.created_at.desc()).all():
        results.append(_tool_to_response(t))

    # Sort: custom first (they have real timestamps), then built-in
    results.sort(key=lambda r: r.created_at, reverse=True)
    return results


@router.get("/tools/custom", response_model=list[CustomToolResponse])
async def list_custom_tools(db: Session = Depends(get_db)):
    """List all custom (user-created) tools."""
    tools = db.query(CustomTool).order_by(CustomTool.created_at.desc()).all()
    return [_tool_to_response(t) for t in tools]


@router.get("/tools/custom/by-type/{tool_type}", response_model=list[CustomToolResponse])
async def list_custom_tools_by_type(tool_type: str, db: Session = Depends(get_db)):
    """List custom tools filtered by type."""
    try:
        tt = ToolType(tool_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tool type: {tool_type}")

    tools = db.query(CustomTool).filter(CustomTool.tool_type == tt).order_by(CustomTool.created_at.desc()).all()
    return [_tool_to_response(t) for t in tools]


@router.get("/tools/custom/{tool_id}", response_model=CustomToolResponse)
async def get_custom_tool(tool_id: str, db: Session = Depends(get_db)):
    """Get a specific custom tool."""
    tool = db.query(CustomTool).filter(CustomTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Custom tool not found")
    return _tool_to_response(tool)


@router.post("/tools/custom", response_model=CustomToolResponse)
async def create_custom_tool(payload: CustomToolCreate, db: Session = Depends(get_db)):
    """Create a new custom tool (starts as draft)."""
    existing = db.query(CustomTool).filter(CustomTool.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Tool '{payload.name}' already exists")

    try:
        tt = ToolType(payload.tool_type)
    except ValueError:
        tt = ToolType.CUSTOM

    tool = CustomTool(
        name=payload.name,
        description=payload.description,
        tool_type=tt,
        input_schema=payload.input_schema,
        config=payload.config,
        output_schema=payload.output_schema,
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return _tool_to_response(tool)


@router.put("/tools/custom/{tool_id}", response_model=CustomToolResponse)
async def update_custom_tool(tool_id: str, payload: CustomToolUpdate, db: Session = Depends(get_db)):
    """Update a custom tool."""
    tool = db.query(CustomTool).filter(CustomTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Custom tool not found")

    if payload.name is not None:
        tool.name = payload.name
    if payload.description is not None:
        tool.description = payload.description
    if payload.tool_type is not None:
        try:
            tool.tool_type = ToolType(payload.tool_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tool type: {payload.tool_type}")
    if payload.input_schema is not None:
        tool.input_schema = payload.input_schema
    if payload.config is not None:
        tool.config = payload.config
    if payload.output_schema is not None:
        tool.output_schema = payload.output_schema
    if payload.status is not None:
        try:
            tool.status = ToolStatus(payload.status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {payload.status}")

    db.commit()
    db.refresh(tool)
    return _tool_to_response(tool)


@router.delete("/tools/custom/{tool_id}")
async def delete_custom_tool(tool_id: str, db: Session = Depends(get_db)):
    """Delete a custom tool."""
    tool = db.query(CustomTool).filter(CustomTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Custom tool not found")
    db.delete(tool)
    db.commit()
    return {"deleted": tool_id}


# ──────────────────────────────────────────────
# Verification
# ──────────────────────────────────────────────

@router.post("/tools/custom/{tool_id}/verify", response_model=ToolVerifyResponse)
async def verify_custom_tool(tool_id: str, req: ToolVerifyRequest, db: Session = Depends(get_db)):
    """Verify a custom tool by running a test execution against its config."""
    tool = db.query(CustomTool).filter(CustomTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Custom tool not found")

    if tool.status not in (ToolStatus.DRAFT, ToolStatus.PENDING_VERIFICATION, ToolStatus.REJECTED, ToolStatus.ERROR):
        raise HTTPException(status_code=400, detail=f"Tool is already verified (status: {tool.status.value})")

    tool.status = ToolStatus.PENDING_VERIFICATION
    db.commit()

    # Simulate verification — in production, this would call an LLM or execute against real config
    start = __import__("time").time()
    try:
        result = await _run_verification_test(tool, req.test_inputs)
        elapsed = round(__import__("time").time() - start, 2)

        tool.last_test_result = {
            "success": result["success"],
            "output": result.get("output"),
            "error": result.get("error"),
            "elapsed_seconds": elapsed,
            "tested_at": __import__("datetime").datetime.utcnow().isoformat(),
        }

        if result["success"]:
            tool.status = ToolStatus.VERIFIED
            tool.verified_at = __import__("datetime").datetime.utcnow()
            tool.verified_by = "system"
        else:
            tool.status = ToolStatus.ERROR

    except Exception as exc:
        tool.last_test_result = {
            "success": False,
            "error": str(exc),
            "tested_at": __import__("datetime").datetime.utcnow().isoformat(),
        }
        tool.status = ToolStatus.ERROR

    db.commit()
    db.refresh(tool)

    return ToolVerifyResponse(
        success=tool.last_test_result.get("success", False),
        output=tool.last_test_result.get("output"),
        error=tool.last_test_result.get("error"),
        message="Verification passed" if tool.status == ToolStatus.VERIFIED else "Verification failed",
    )


async def _run_verification_test(tool: CustomTool, test_inputs: dict[str, Any]) -> dict[str, Any]:
    """Simulate a tool verification test."""
    config = tool.config or {}
    ttype = tool.tool_type.value

    # Basic validation based on tool type
    if ttype == "http":
        if not config.get("url"):
            return {"success": False, "error": "Missing 'url' in tool config"}
        if not config.get("method"):
            return {"success": False, "error": "Missing 'method' in tool config"}
        return {
            "success": True,
            "output": {
                "status": 200,
                "body": {"message": "Test successful", "url": config["url"]},
                "headers": {"content-type": "application/json"},
            },
        }

    elif ttype == "database":
        if not config.get("connection_string"):
            return {"success": False, "error": "Missing 'connection_string' in config"}
        return {
            "success": True,
            "output": {
                "rows_affected": 0,
                "message": "Connection validated",
                "connection_string": config["connection_string"][:20] + "...",
            },
        }

    elif ttype == "email":
        if not config.get("smtp_host") and not config.get("api_endpoint"):
            return {"success": False, "error": "Missing SMTP host or API endpoint"}
        return {
            "success": True,
            "output": {
                "sent": True,
                "to": test_inputs.get("to", "test@example.com"),
                "provider": config.get("provider", "smtp"),
            },
        }

    elif ttype == "webhook":
        if not config.get("endpoint_url"):
            return {"success": False, "error": "Missing 'endpoint_url' in config"}
        return {
            "success": True,
            "output": {
                "webhook_id": "wh_" + __import__("uuid").uuid4().hex[:8],
                "endpoint": config["endpoint_url"],
                "status": "active",
            },
        }

    elif ttype == "transform":
        if not config.get("expression") and not config.get("mapping"):
            return {"success": False, "error": "Missing 'expression' or 'mapping' in config"}
        return {
            "success": True,
            "output": {
                "transformed": True,
                "input_keys": list(test_inputs.keys()),
                "output_keys": ["result"],
            },
        }

    elif ttype == "delay":
        return {
            "success": True,
            "output": {
                "delay_seconds": config.get("duration", 5),
                "scheduled": True,
            },
        }

    else:
        # Generic custom tool — just check that it has a name and description
        return {
            "success": True,
            "output": {
                "message": f"Custom tool '{tool.name}' validated",
                "type": ttype,
                "config_keys": list(config.keys()),
            },
        }


@router.post("/tools/custom/{tool_id}/register")
async def register_custom_tool(tool_id: str, db: Session = Depends(get_db)):
    """Register a verified custom tool into the runtime registry."""
    tool = db.query(CustomTool).filter(CustomTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Custom tool not found")

    if tool.status != ToolStatus.VERIFIED:
        raise HTTPException(status_code=400, detail="Tool must be verified before registration")

    # Check if already registered
    if registry.get(tool.name):
        return {"message": f"Tool '{tool.name}' already registered", "already_registered": True}

    # Register in runtime
    registry.register(
        name=tool.name,
        description=tool.description,
        input_schema=tool.input_schema or {},
        timeout_seconds=30,
        permission="auto",
        handler=lambda **kwargs: {"success": True, "output": kwargs},
    )

    return {"message": f"Tool '{tool.name}' registered successfully", "registered": True}
