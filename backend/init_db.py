"""
数据库初始化脚本
运行此脚本创建数据库表和初始管理员账户
"""
from database import init_db, SessionLocal, User
from auth import get_password_hash

def create_initial_user():
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("管理员账户已存在")
            return
        
        # 使用简短密码避免bcrypt长度限制
        admin_user = User(
            username="admin",
            email="admin@phantomflow.com",
            hashed_password=get_password_hash("admin123"),
            full_name="系统管理员"
        )
        db.add(admin_user)
        db.commit()
        print("✓ 创建管理员账户成功")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  邮箱: admin@phantomflow.com")
    except Exception as e:
        print(f"✗ 创建管理员账户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始初始化数据库...")
    init_db()
    print("✓ 数据库表创建成功")
    
    print("\n创建初始管理员账户...")
    create_initial_user()
    
    print("\n数据库初始化完成！")
