# 基础镜像,建议选择官方 python 镜像
# FROM python:3.13-slim
# 替换国内镜像
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.13-slim-bookworm

# setup work dir
WORKDIR /app

# 核心：将项目根目录 /app 加入 Python 模块搜索路径
ENV PYTHONPATH=/app

# 复制项目依赖清单到容器内
COPY REQUIREMENTS.txt .


# 安装项目依赖
# --no-cache-dir  不缓存安装包，减小镜像体积
# -i https://pypi.tuna.tsinghua.edu.cn/simple：可选，使用清华镜像源加速安装（国内环境推荐）
RUN pip install --no-cache-dir -r REQUIREMENTS.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制所有文件到工作目录
# 注意， 通过.dockerignore 排除不必要的文件
COPY . .

# web server 需要暴露端口
EXPOSE 5000

# 启动命令
# 可适配uvicorn 运行服务  CMD ["uvicorn", "agent.web.ChatServer:app", "--host", "0.0.0.0", "--port", "8080"]
CMD ["python", "agent/web/app.py" ]

