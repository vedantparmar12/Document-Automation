import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastAPIIntegration
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastAPIIntegration()],
            traces_sample_rate=1.0
        )
        logger.info("Sentry integration enabled")
    except ImportError:
        logger.warning("Sentry SDK or FastAPIIntegration not found. Skipping Sentry setup.")
    except Exception as e:
        logger.warning(f"Sentry setup failed: {e}, continuing without Sentry")

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError as e:
    logger.error(f"FastAPI or Pydantic not available: {e}, creating stubs")
    class FastAPI:
        def __init__(self, **kwargs): pass
        def post(self, path):
            def decorator(func): return func
            return decorator
        def get(self, path):
            def decorator(func): return func
            return decorator
    class BaseModel: pass
    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

from src.tools.register_tools import register_all_tools

app = FastAPI(title="Document Automation MCP Server")

class AnalyzeRequest(BaseModel):
    path: str
    type: str

@app.post("/analyze")
async def analyze_codebase(request: AnalyzeRequest):
    try:
        if request.type not in ['local', 'github']:
            raise HTTPException(status_code=400, detail="Invalid type")
        result = await register_all_tools(request.path, request.type)
        return result
    except Exception as e:
        logger.error(f"Error in analyze_codebase: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Document Automation MCP Server!"}

if __name__ == '__main__':
    import uvicorn
    # Cloud Run sets PORT environment variable
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host='0.0.0.0', port=port)