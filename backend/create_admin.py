"""
直接创建管理员账户的简化脚本
"""
import bcrypt
from database import SessionLocal, User
from datetime import datetime

def create_admin():
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print("管理员账户已存在")
            return
        
        # 直接使用bcrypt加密密码
        password = "admin123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        admin = User(
            username="admin",
            email="admin@phantomflow.com",
            hashed_password=hashed.decode('utf-8'),
            full_name="系统管理员",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        
        print("✓ 管理员账户创建成功")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  邮箱: admin@phantomflow.com")
        
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
