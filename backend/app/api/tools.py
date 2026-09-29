"""Tools API routes."""

from fastapi import APIRouter

from app.tools.registry import registry

router = APIRouter()


@router.get("/tools")
async def list_tools():
    """List all registered tools with their metadata."""
    tools = registry.list_all()
    return [
        {
            "name": t.name,
            "description": t.description,
            "permission": t.permission.value,
            "timeout_seconds": t.timeout_seconds,
            "retryable": t.retryable,
            "input_schema": t.input_schema,
        }
        for t in tools
    ]


@router.get("/tools/{tool_name}")
async def get_tool(tool_name: str):
    """Get details for a specific tool."""
    tool = registry.get(tool_name)
    if not tool:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    return {
        "name": tool.name,
        "description": tool.description,
        "permission": tool.permission.value,
        "timeout_seconds": tool.timeout_seconds,
        "retryable": tool.retryable,
        "input_schema": tool.input_schema,
    }
