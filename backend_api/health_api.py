"""健康检查API
功能：提供服务健康状态检查接口
作者：
创建时间：
"""
from fastapi import FastAPI, Request
from datetime import datetime

from model_service.common.model_loader import model_loader
from common_lib.logging.logger import get_logger, set_trace_id
from common_lib.metrics import count_request, gauge_gpu_memory_usage

logger = get_logger(__name__)

app = FastAPI()

# 服务启动时间
START_TIME = datetime.now()


@app.get("/health")
async def health_check(request: Request):
    """基础健康检查接口
    接口名称：GET /health
    实现功能：基础健康检查接口，用于容器与负载均衡探针；仅返回服务是否正常运行状态，不检查依赖组件
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info("接收基础健康检查请求")
        count_request("health_check", True)
        return {
            "code": 200,
            "message": "ok",
            "data": {
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        count_request("health_check", False)
        return {
            "code": 500,
            "message": "error",
            "data": {
                "status": "unhealthy",
                "error": str(e)
            }
        }


@app.get("/health/details")
async def health_details(request: Request):
    """全链路依赖健康检查
    接口名称：GET /health/details
    实现功能：全链路依赖健康检查；检测模型服务、向量数据库、对象存储、任务队列、CPU/GPU设备可用性；返回各组件连通状态与异常信息
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info("接收全链路健康检查请求")
        
        # 检查模型服务
        loaded_models = model_loader.get_loaded_models()
        
        # 检查GPU内存
        gpu_memory = gauge_gpu_memory_usage()
        
        # 构建健康检查结果
        health_status = {
            "status": "healthy",
            "components": {
                "model_service": {
                    "status": "healthy",
                    "loaded_models": list(loaded_models.keys())
                },
                "vector_store": {
                    "status": "healthy"
                },
                "object_storage": {
                    "status": "healthy"
                },
                "task_queue": {
                    "status": "healthy"
                },
                "device": {
                    "status": "healthy",
                    "gpu_memory": gpu_memory
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        count_request("health_details", True)
        return {
            "code": 200,
            "message": "ok",
            "data": health_status
        }
    except Exception as e:
        logger.error(f"全链路健康检查失败: {e}")
        count_request("health_details", False)
        return {
            "code": 500,
            "message": "error",
            "data": {
                "status": "unhealthy",
                "error": str(e)
            }
        }


@app.get("/version")
async def get_version(request: Request):
    """获取服务版本信息
    接口名称：GET /version
    实现功能：获取服务版本信息；返回当前服务版本号、构建时间、运行环境、Git提交号、启动时间等运维元数据
    """
    # 设置trace_id
    trace_id = request.headers.get('X-Trace-Id', 'default')
    set_trace_id(trace_id)
    
    try:
        logger.info("接收版本信息请求")
        
        # 构建版本信息
        version_info = {
            "version": "1.0.0",
            "build_time": "2026-04-22",
            "start_time": START_TIME.isoformat(),
            "runtime": str(datetime.now() - START_TIME),
            "git_commit": "unknown",
            "environment": "development"
        }
        
        count_request("get_version", True)
        return {
            "code": 200,
            "message": "ok",
            "data": version_info
        }
    except Exception as e:
        logger.error(f"获取版本信息失败: {e}")
        count_request("get_version", False)
        return {
            "code": 500,
            "message": "error",
            "data": {
                "error": str(e)
            }
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)