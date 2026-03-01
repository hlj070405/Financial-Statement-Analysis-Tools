import json
from sqlalchemy.orm import Session
from database import ChatHistory
from deepseek_service import DeepSeekService
from typing import List, Optional
import asyncio

class ChatHistoryService:
    """聊天历史管理服务"""
    
    @staticmethod
    async def save_or_update_chat(
        db: Session,
        user_id: int,
        conversation_id: str,
        message: str,
        response: str,
        deepseek_service: DeepSeekService,
        is_first_message: bool = False
    ):
        """保存或更新聊天历史"""
        try:

            from fastapi.concurrency import run_in_threadpool
            
            # 查找现有会话
            chat = await run_in_threadpool(
                lambda: db.query(ChatHistory).filter(ChatHistory.conversation_id == conversation_id).first()
            )
            
            if chat:
                # 更新现有会话
                messages = json.loads(chat.messages) if chat.messages else []
                messages.append({
                    "role": "user",
                    "content": message
                })
                messages.append({
                    "role": "assistant",
                    "content": response
                })
                chat.messages = json.dumps(messages, ensure_ascii=False)
                
                await run_in_threadpool(lambda: db.commit())
                print(f"[聊天历史] 更新会话: {conversation_id}")
            else:
                # 创建新会话
                # 异步生成标题 (这是真正的异步调用)
                title = await deepseek_service.generate_chat_title(message, response)
                print(f"[聊天历史] AI生成标题: {title}")
                
                messages = [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response}
                ]
                
                chat = ChatHistory(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    title=title,
                    first_message=message,
                    messages=json.dumps(messages, ensure_ascii=False)
                )
                
                def add_and_commit():
                    db.add(chat)
                    db.commit()
                
                await run_in_threadpool(add_and_commit)
                print(f"[聊天历史] 创建新会话: {conversation_id}, 标题: {title}")
                
        except Exception as e:
            print(f"[聊天历史] 保存失败: {str(e)}")
            # Rollback also needs to be in threadpool if we are strict, but it's rare
            db.rollback()
    
    @staticmethod
    def get_user_chat_history(db: Session, user_id: int, limit: int = 50) -> List[dict]:
        """获取用户的聊天历史列表"""
        chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.updated_at.desc()).limit(limit).all()
        
        return [
            {
                "conversation_id": chat.conversation_id,
                "title": chat.title,
                "first_message": chat.first_message,
                "created_at": chat.created_at.isoformat() if chat.created_at else None,
                "updated_at": chat.updated_at.isoformat() if chat.updated_at else None
            }
            for chat in chats
        ]
    
    @staticmethod
    def get_chat_messages(db: Session, conversation_id: str, user_id: int) -> Optional[dict]:
        """获取特定会话的消息历史"""
        chat = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == conversation_id,
            ChatHistory.user_id == user_id
        ).first()
        
        if not chat:
            return None
        
        return {
            "conversation_id": chat.conversation_id,
            "title": chat.title,
            "messages": json.loads(chat.messages) if chat.messages else [],
            "created_at": chat.created_at.isoformat() if chat.created_at else None,
            "updated_at": chat.updated_at.isoformat() if chat.updated_at else None
        }
    
    @staticmethod
    def delete_chat(db: Session, conversation_id: str, user_id: int) -> bool:
        """删除聊天历史"""
        chat = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == conversation_id,
            ChatHistory.user_id == user_id
        ).first()
        
        if chat:
            db.delete(chat)
            db.commit()
            return True
        return False
