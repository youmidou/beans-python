#!/bin/bash
# PostgreSQL 数据库设置说明
#
# 注意：现在数据库和表会自动创建！
# - 数据库不存在时会自动创建
# - 表不存在时会根据 AutoMigrate 中的模型自动创建
#
# 只需要确保 PostgreSQL 服务正在运行：
# docker run -d --name postgres -p 10001:5432 -e POSTGRES_PASSWORD=12345678 postgres:latest
#
# 或者手动创建数据库（可选）：
# psql -h 127.0.0.1 -p 10001 -U postgres -c "CREATE DATABASE gamedb;"

echo "✅ 数据库会在程序启动时自动创建"
echo "✅ 表结构会根据 AutoMigrate 自动创建"
echo ""
echo "请确保 PostgreSQL 服务正在运行："
echo "  docker run -d --name postgres -p 10001:5432 -e POSTGRES_PASSWORD=12345678 postgres:latest"

