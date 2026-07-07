"""Small shared constants used across routers."""

# Upper bound for ?limit=... on any paginated endpoint. Enforced directly
# via FastAPI's Query(..., le=MAX_PAGE_SIZE) so out-of-range values are
# rejected by Pydantic itself (see error_handlers.py for why that's fine
# under this contract).
MAX_PAGE_SIZE = 1000
