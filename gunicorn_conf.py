bind = "0.0.0.0:8000"
workers = 4  # 根据CPU核心数调整（2*CPU+1）
worker_class = "gevent"  # 异步处理
worker_connections = 1000  # 每个Worker的连接数
timeout = 30
keepalive = 2