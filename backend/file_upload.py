"""
文件上传到Dify的辅助模块
"""
import httpx
import os
from typing import Optional
from fastapi import UploadFile, HTTPException

async def upload_file_to_dify(
    file: UploadFile,
    dify_api_url: str,
    dify_api_key: str,
    user: str
) -> dict:
    """
    上传文件到Dify并返回文件信息
    
    Args:
        file: FastAPI UploadFile对象
        dify_api_url: Dify API基础URL
        dify_api_key: Dify API密钥
        user: 用户标识
        
    Returns:
        dict: 包含文件ID和其他信息的字典
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                'Authorization': f'Bearer {dify_api_key}'
            }
            
            # 读取文件内容
            file_content = await file.read()
            
            # 准备multipart/form-data
            files = {
                'file': (file.filename, file_content, file.content_type)
            }
            
            data = {
                'user': user
            }
            
            # 上传到Dify
            response = await client.post(
                f"{dify_api_url}/files/upload",
                headers=headers,
                files=files,
                data=data
            )
            
            if response.status_code != 200 and response.status_code != 201:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get('message', error_detail)
                except:
                    pass
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"文件上传到Dify失败: {error_detail}"
                )
            
            result = response.json()
            
            # 打印Dify返回的完整数据以便调试
            print(f"[文件上传] Dify返回数据: {result}")
            
            return {
                "id": result.get("id"),
                "name": result.get("name"),
                "size": result.get("size"),
                "extension": result.get("extension"),
                "mime_type": result.get("mime_type"),
                "created_at": result.get("created_at"),
                "created_by": result.get("created_by"),
                "type": "document"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
