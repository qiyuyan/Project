from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# CRM-定义客户模型
class Customer(db.Model):
    __tablename__ = 'customer'
    customer_code = db.Column(db.String(50), primary_key=True)
    customer_name = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    customer_address = db.Column(db.Text)
    customer_email = db.Column(db.String(100))
    contact = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    orders = db.relationship('Order', backref='customer', lazy=True)

# ORDER-定义订单模型
class Order(db.Model):
    __tablename__ = 'order'
    order_number = db.Column(db.String(50), primary_key=True)
    date = db.Column(db.Date)
    factory = db.Column(db.String(100))
    deal_term = db.Column(db.String(50))
    currency = db.Column(db.String(50))
    from_location = db.Column('from', db.String(100))  # 'from'是SQL关键字，需要特殊处理
    to_location = db.Column('to', db.String(100))  # 同上
    customer_code = db.Column(db.String(50), db.ForeignKey('customer.customer_code'))

# ORDER-定义配方模型
class Formula(db.Model):
    __tablename__ = 'formula'
    formula_code = db.Column(db.String(255), primary_key=True)
    name_en = db.Column(db.String(200))
    name_cn = db.Column(db.String(200))
    pet = db.Column(db.String(255))
    tech = db.Column(db.String(200))
    brand = db.Column(db.String(200))
    ingredient = db.Column(db.String(500))
    additive = db.Column(db.String(500))
    protein_design = db.Column(db.Float)
    fat_design = db.Column(db.Float)
    fiber_design = db.Column(db.Float)
    ash_design = db.Column(db.Float)
    cal_design = db.Column(db.Float)
    phos_design = db.Column(db.Float)
    moisture_design = db.Column(db.Float)

# ORDER-定义批次模型
class Batch(db.Model):
    __tablename__ = 'batch'
    batch_id = db.Column(db.String(255), primary_key=True)
    production_date = db.Column(db.Date, nullable=False)
    formula_code = db.Column(db.String(255), db.ForeignKey('formula.formula_code'))
    protein = db.Column(db.Float)
    fat = db.Column(db.Float)
    fiber = db.Column(db.Float)
    ash = db.Column(db.Float)
    cal = db.Column(db.Float)
    phos = db.Column(db.Float)
    moisture = db.Column(db.Float)

# ORDER-定义 SKU 模型
class SKU(db.Model):
    __tablename__ = 'sku'
    sku_id = db.Column(db.String(255), primary_key=True)
    formula = db.Column(db.String(255), db.ForeignKey('formula.formula_code'))
    size = db.Column(db.String(255))
    box_qty = db.Column(db.Integer)
    cbm = db.Column(db.Float)
    gross_weight = db.Column(db.Float)
    unit_price = db.Column(db.Float)

# ORDER-定义集装箱模型
class Container(db.Model):
    __tablename__ = 'container'
    container_id = db.Column(db.String(255), primary_key=True)
    order_id = db.Column(db.String(255), db.ForeignKey('order.order_number'))
    shipper = db.Column(db.String(200))
    voyage = db.Column(db.String(255))
    bl_number = db.Column(db.String(255))
    container_code = db.Column(db.String(255))
    seal = db.Column(db.String(255))
    type = db.Column(db.String(50))
    sub_bl_number = db.Column(db.String(255))
    comment = db.Column(db.Text)

# ORDER-定义装载模型
class Loading(db.Model):
    __tablename__ = 'loading'
    id = db.Column(db.Integer, primary_key=True)
    container_id = db.Column(db.String(255), db.ForeignKey('container.container_id'))
    sku_id = db.Column(db.String(255), db.ForeignKey('sku.sku_id'))
    loading_boxes = db.Column(db.Integer)

# DOC-定义文件模型
class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer)
    document_type = db.Column(db.String(255))
    create_date = db.Column(db.Date, default=db.func.current_date())
    customer = db.Column(db.String(255), db.ForeignKey('customer.customer_code'))
    order_id = db.Column(db.String(255), db.ForeignKey('order.order_number'))

# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nickname = db.Column(db.String(80), nullable=False, default='User')
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

# 定义角色模型
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary='role_permissions', backref=db.backref('roles', lazy='dynamic'))

# 定义权限模型
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

# 定义用户 - 角色关联表
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                      )

# 定义角色 - 权限关联表
role_permissions = db.Table('role_permissions',
                            db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                            db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                            )