"""Integrations API routes — manage real service configs for tools."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.database import get_db
from app.models.custom_tool import CustomTool
from app.schemas.custom_tool import CustomToolResponse
from app.schemas.integration import (
    IntegrationConfigUpdate,
    IntegrationTestRequest,
    IntegrationTestResponse,
)
from app.tools.integrations import integration_handler, _mask_credentials

router = APIRouter()


def _tool_to_response(tool: CustomTool) -> CustomToolResponse:
    """Build response with masked integration config."""
    ic = tool.integration_config or None
    if ic:
        ic = _mask_credentials(ic)
    return CustomToolResponse(
        id=tool.id,
        name=tool.name,
        description=tool.description,
        tool_type=tool.tool_type.value,
        status=tool.status.value,
        input_schema=tool.input_schema or {},
        config=tool.config or {},
        output_schema=tool.output_schema or {},
        integration_config=ic,
        last_test_result=tool.last_test_result,
        verified_at=tool.verified_at,
        verified_by=tool.verified_by,
        created_at=tool.created_at,
        updated_at=tool.updated_at,
    )


def _get_tool_or_404(tool_id: str, db: Session) -> CustomTool:
    tool = db.query(CustomTool).filter(CustomTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.get("/integrations")
async def list_integrations(db: Session = Depends(get_db)):
    """List all tools that have integration configs (credentials masked)."""
    tools = (
        db.query(CustomTool)
        .filter(CustomTool.integration_config.is_not(None))
        .order_by(CustomTool.updated_at.desc())
        .all()
    )
    return [
        {
            "id": t.id,
            "name": t.name,
            "tool_type": t.tool_type.value,
            "status": t.status.value,
            "integration_config": _mask_credentials(t.integration_config or {}),
            "verified_at": t.verified_at.isoformat() if t.verified_at else None,
            "last_test_result": t.last_test_result,
        }
        for t in tools
    ]


@router.get("/integrations/{tool_id}", response_model=CustomToolResponse)
async def get_integration(tool_id: str, db: Session = Depends(get_db)):
    """Get a single tool's integration config (credentials masked)."""
    tool = _get_tool_or_404(tool_id, db)
    ic = tool.integration_config or None
    if ic:
        ic = _mask_credentials(ic)
    return CustomToolResponse(
        id=tool.id,
        name=tool.name,
        description=tool.description,
        tool_type=tool.tool_type.value,
        status=tool.status.value,
        input_schema=tool.input_schema or {},
        config=tool.config or {},
        output_schema=tool.output_schema or {},
        integration_config=ic,
        last_test_result=tool.last_test_result,
        verified_at=tool.verified_at,
        verified_by=tool.verified_by,
        created_at=tool.created_at,
        updated_at=tool.updated_at,
    )


@router.put("/integrations/{tool_id}", response_model=CustomToolResponse)
async def set_integration(
    tool_id: str,
    payload: IntegrationConfigUpdate,
    db: Session = Depends(get_db),
):
    """Set or remove integration config for a tool."""
    tool = _get_tool_or_404(tool_id, db)
    tool.integration_config = payload.integration_config
    db.commit()
    db.refresh(tool)
    return _tool_to_response(tool)


@router.delete("/integrations/{tool_id}")
async def remove_integration(tool_id: str, db: Session = Depends(get_db)):
    """Remove integration config — reverts tool to mock execution."""
    tool = _get_tool_or_404(tool_id, db)
    tool.integration_config = None
    db.commit()
    return {"deleted": True, "tool_id": tool_id}


@router.post("/integrations/{tool_id}/verify", response_model=IntegrationTestResponse)
async def verify_integration(
    tool_id: str,
    req: IntegrationTestRequest,
    db: Session = Depends(get_db),
):
    """Test the real connection for a tool's integration config."""
    tool = _get_tool_or_404(tool_id, db)

    if not tool.integration_config:
        raise HTTPException(
            status_code=400,
            detail="No integration config set. Configure credentials first.",
        )

    import time
    start = time.monotonic()
    try:
        result = await integration_handler.execute(
            tool.integration_config, req.test_inputs
        )
        elapsed = round(time.monotonic() - start, 2)
        return IntegrationTestResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            message="Connection test passed" if result.success else "Connection test failed",
            elapsed_seconds=elapsed,
        )
    except Exception as exc:
        elapsed = round(time.monotonic() - start, 2)
        return IntegrationTestResponse(
            success=False,
            error=str(exc),
            message="Connection test error",
            elapsed_seconds=elapsed,
        )
