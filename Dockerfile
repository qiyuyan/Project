# 使用国内镜像源作为基础镜像（可选）
FROM ccr.ccs.tencentyun.com/library/python:3.9-slim

WORKDIR /app

# 配置 pip 国内源
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> /root/.pip/pip.conf && \
    echo "trusted-host = pypi.tuna.tsinghua.edu.cn" >> /root/.pip/pip.conf

# 安装系统依赖（SQLite需要libsqlite3-dev）
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 安装系统依赖（增加MySQL客户端库）
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 创建instance目录（确保权限）
RUN mkdir -p /app/instance && chmod 777 /app/instance

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--config", "gunicorn_conf.py", "run:app"]