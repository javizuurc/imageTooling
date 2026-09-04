from fastmcp.server.context import Context


async def log_info(ctx: Context, message: str) -> None:
    """ctx.info only with active session (not available in direct calls/tests)."""

    if ctx.request_context is None:
        return

    await ctx.info(message)


async def report_progress(
    ctx: Context, progress: float, total: float, message: str | None = None
) -> None:
    """ctx.report_progress only with active session (not in direct calls/tests)."""

    if ctx.request_context is None:
        return

    await ctx.report_progress(progress=progress, total=total, message=message)
