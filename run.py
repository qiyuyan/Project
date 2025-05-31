import os

from flask import Flask
from app.routes import bp
from app.database import db

app = Flask(__name__)

# 设置统一数据库路径
def setup_instance_folder(app):
    """
    确保 instance 文件夹存在，并返回统一数据库的路径
    :param app: Flask 应用实例
    :return: 统一数据库的路径
    """
    instance_path = os.path.join(app.root_path, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    return os.path.join(instance_path, 'database.db')

db_path = setup_instance_folder(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SECRET_KEY'] = 'your_secret_key'
# 关闭追踪对象的修改并发送信号，这会消耗额外内存，生产环境建议关闭
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# 注册蓝图（如果使用蓝图）或直接使用路由
app.register_blueprint(blueprint=bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # 初始化数据（示例）
        # 检查权限是否已存在
        from app.database.models import Permission, Role, User
        view_permission = Permission.query.filter_by(name='view_protected').first()
        if not view_permission:
            view_permission = Permission(name='view_protected')
            db.session.add(view_permission)

        # 检查角色是否已存在
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            admin_role.permissions.extend([view_permission])

        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user')
            db.session.add(user_role)
            user_role.permissions.append(view_permission)

        # 检查用户是否已存在
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password='admin', nickname="Admin")  # 修改这里，直接设置明文密码
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)

        normal_user = User.query.filter_by(username='user').first()
        if not normal_user:
            normal_user = User(username='user', password='user', nickname="User")
            normal_user.roles.append(user_role)
            db.session.add(normal_user)

        db.session.commit()

    app.run(debug=False)