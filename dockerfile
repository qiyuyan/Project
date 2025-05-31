# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到容器的/app目录
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露Flask默认端口
EXPOSE 8080

# 定义环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 运行应用
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app"]