import asyncio
import time
from typing import Dict, Any, Union
from fastapi import Request
from app.utils.logging import log

class ActiveRequestsManager:
    """管理活跃API请求的类"""
    
    def __init__(self, requests_pool: Dict[str, asyncio.Task] = None):
        self.active_requests = requests_pool if requests_pool is not None else {}  # 存储活跃请求
    
    def add(self, key: str, task: asyncio.Task):
        """添加新的活跃请求任务"""
        task.creation_time = time.time()  # 添加创建时间属性
        self.active_requests[key] = task
    
    def get(self, key: str):
        """获取活跃请求任务"""
        return self.active_requests.get(key)
    
    def remove(self, key: str):
        """移除活跃请求任务"""
        if key in self.active_requests:
            del self.active_requests[key]
            return True
        return False
    
    def clean_completed(self):
        """清理所有已完成或已取消的任务"""
        
        for key, task in self.active_requests.items():
            if task.done() or task.cancelled():
                del self.active_requests[key]        
        
        # if keys_to_remove:
        #    log('info', f"清理已完成请求任务: {len(keys_to_remove)}个", cleanup='active_requests')
    
    def clean_long_running(self, max_age_seconds: int = 300):
        """清理长时间运行的任务"""
        now = time.time()
        long_running_keys = []
        
        for key, task in list(self.active_requests.items()):
            if (hasattr(task, 'creation_time') and
                task.creation_time < now - max_age_seconds and
                not task.done() and not task.cancelled()):
                
                long_running_keys.append(key)
                task.cancel()  # 取消长时间运行的任务
        
        if long_running_keys:
            log('warning', f"取消长时间运行的任务: {len(long_running_keys)}个", cleanup='long_running_tasks')


def process_fake_stream_request(http_request: Request, request_data: Union[Dict[str, Any], Any]) -> Union[Dict[str, Any], Any]:
    """
    处理请求的fake_stream参数设置
    
    Args:
        http_request: FastAPI请求对象
        request_data: 请求数据对象或字典
        
    Returns:
        处理后的请求数据
    """
    try:
        # 检查请求路径是否以 "/fake-stream" 开头
        path = str(http_request.url.path)
        is_fake_stream_path = path.startswith("/fake-stream")
        
        # 根据路径设置fake_stream参数
        if hasattr(request_data, 'fake_stream'):
            # 对于Pydantic模型，直接设置属性
            request_data.fake_stream = is_fake_stream_path
        elif isinstance(request_data, dict):
            # 对于字典类型，设置键值
            request_data['fake_stream'] = is_fake_stream_path
        else:
            # 尝试作为对象处理
            try:
                setattr(request_data, 'fake_stream', is_fake_stream_path)
            except (AttributeError, TypeError):
                log('warning', f"无法为请求数据设置fake_stream参数: {type(request_data)}")
        
        log('debug', f"请求路径: {path}, fake_stream设置为: {is_fake_stream_path}")
        return request_data
        
    except Exception as e:
        log('error', f"处理fake_stream请求时发生错误: {e}")
        return request_data
