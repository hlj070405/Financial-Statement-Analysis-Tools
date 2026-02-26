"""
创建测试用户脚本
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def create_test_user():
    """创建测试用户"""
    
    # 测试账号信息
    test_users = [
        {
            "username": "admin",
            "email": "admin@phantomflow.com",
            "password": "admin123",
            "full_name": "系统管理员"
        },
        {
            "username": "analyst",
            "email": "analyst@phantomflow.com", 
            "password": "analyst123",
            "full_name": "金融分析师"
        },
        {
            "username": "test",
            "email": "test@phantomflow.com",
            "password": "test123",
            "full_name": "测试用户"
        }
    ]
    
    print("=" * 60)
    print("幻流 (Phantom Flow) - 测试账号创建工具")
    print("=" * 60)
    print()
    
    for user_data in test_users:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功创建用户: {user_data['username']}")
                print(f"   用户名: {user_data['username']}")
                print(f"   密码: {user_data['password']}")
                print(f"   邮箱: {user_data['email']}")
                print(f"   姓名: {user_data['full_name']}")
                print()
            else:
                error_detail = response.json().get('detail', '未知错误')
                if '已存在' in error_detail or 'already' in error_detail.lower():
                    print(f"ℹ️  用户已存在: {user_data['username']}")
                    print(f"   用户名: {user_data['username']}")
                    print(f"   密码: {user_data['password']}")
                    print()
                else:
                    print(f"❌ 创建失败: {user_data['username']} - {error_detail}")
                    print()
        
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到后端服务 ({API_BASE_URL})")
            print("   请确保后端服务已启动")
            return
        except Exception as e:
            print(f"❌ 创建用户时出错: {str(e)}")
    
    print("=" * 60)
    print("测试账号信息汇总")
    print("=" * 60)
    print()
    print("推荐使用以下账号登录:")
    print()
    print("1. 管理员账号")
    print("   用户名: admin")
    print("   密码: admin123")
    print()
    print("2. 分析师账号")
    print("   用户名: analyst")
    print("   密码: analyst123")
    print()
    print("3. 测试账号")
    print("   用户名: test")
    print("   密码: test123")
    print()
    print("=" * 60)
    print("访问地址: http://localhost:3001")
    print("=" * 60)

if __name__ == "__main__":
    create_test_user()
