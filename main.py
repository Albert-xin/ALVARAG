import uvicorn
from fastapi import FastAPI
from common_lib.database import init_database
from backend_api import intent_api, sample_api, version_api, operation_log_api

app = FastAPI(
    title="ALVARAG",
    description="Advanced Language Understanding and Retrieval Augmented Generation System",
    version="1.0.0"
)

# 注册路由
app.include_router(intent_api.router)
app.include_router(sample_api.router)
app.include_router(version_api.router)
app.include_router(operation_log_api.router)

@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    init_database()
    print("Database initialized successfully")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
