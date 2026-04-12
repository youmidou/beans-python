# YmdDataAccessBase 数据访问基础类

## 概述

`YmdDataAccessBase` 是一个完整的数据访问基础类，提供了统一的数据访问接口，支持 Redis、MySQL、MongoDB 三种数据库，并实现了智能缓存管理和自动数据同步功能。

## 核心特性

### 1. 多数据库支持
- **Redis**: 高性能缓存和会话存储
- **MySQL**: 主数据库，持久化存储
- **MongoDB**: 文档数据库，适合日志和复杂数据结构

### 2. 智能缓存管理
- 内存缓存 + Redis 缓存的双层架构
- 支持脏数据标记和自动同步
- 可配置的同步间隔（默认15分钟）
- 关闭时自动保存所有未同步数据

### 3. 数据访问策略
- 读取策略：内存缓存 → Redis → MySQL
- 写入策略：内存缓存 → Redis → MySQL（可选）
- 支持强制立即存储到MySQL

## 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   应用层        │    │   缓存层        │    │   存储层        │
│                 │    │                 │    │                 │
│ DataAccessManager│───▶│ YmdDataAccessBase│───▶│ Redis/MySQL/Mongo│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 使用方法

### 1. 基本配置

```go
import (
    "ricebean/pkg/ymd_dataaccess"
    "ricebean/pkg/ymd_dataaccess/ymd_mysql"
    "ricebean/pkg/ymd_dataaccess/ymd_redis"
    "ricebean/pkg/ymd_dataaccess/ymd_mongo"
)

// 创建配置信息
dataAccessInfo := &ymd_dataaccess.DataAccessInfo{
    MysqlInfo: &ymd_mysql.MysqlInfo{
        Address:  "127.0.0.1:3306",
        Root:     "root",
        Password: "12345678",
        Database: "game_db",
    },
    RedisInfo: &ymd_redis.RedisInfo{
        Addr:         "127.0.0.1:6379",
        Password:     "",
        DB:           0,
        PoolSize:     10,
        MinIdleConns: 5,
    },
    MongoInfo: &ymd_mongo.MongoDBInfo{
        Address:  "127.0.0.1:27017",
        Root:     "admin",
        Password: "password",
        Database: "game_logs",
    },
}
```

### 2. 创建实例

```go
// 创建数据访问基础实例
dataAccess := ymd_dataaccess.NewYmdDataAccessBase(app, dataAccessInfo)

// 初始化
err := dataAccess.Init()
if err != nil {
    log.Fatalf("初始化失败: %v", err)
}

// 启动定时同步任务
dataAccess.AfterInit()
```

### 3. 缓存操作

```go
// 设置缓存（不强制存储到MySQL）
err := dataAccess.SetCache("user:1001", userData, false)

// 设置缓存（强制存储到MySQL）
err := dataAccess.SetCache("user:1002", userData, true)

// 获取缓存
if value, exists := dataAccess.GetCache("user:1001"); exists {
    // 使用缓存数据
}

// 删除缓存
err := dataAccess.DeleteCache("user:1001")
```

### 4. 数据库操作

```go
// 获取Redis客户端
redisClient := dataAccess.GetRedisClient()
if redisClient != nil {
    err := redisClient.Set("key", "value", time.Hour)
}

// 获取MySQL客户端
mysqlClient := dataAccess.GetMysqlClient()
if mysqlClient != nil {
    db := mysqlClient.GetDBSession()
    // 执行SQL操作
}

// 获取MongoDB客户端
mongoClient := dataAccess.GetMongoClient()
if mongoClient != nil {
    collection := mongoClient.GetCollection("users")
    // 执行MongoDB操作
}
```

### 5. 数据同步

```go
// 强制同步所有数据到MySQL
err := dataAccess.ForceSyncToMysql()

// 设置同步间隔
dataAccess.SetSyncInterval(10 * time.Minute)

// 获取缓存统计信息
stats := dataAccess.GetCacheStats()
fmt.Printf("缓存统计: %+v\n", stats)
```

### 6. 高级缓存操作

```go
// 获取所有缓存键
keys := dataAccess.GetCacheKeys()

// 获取缓存项详情
if item, exists := dataAccess.GetCacheItem("user:1001"); exists {
    fmt.Printf("是否脏数据: %v\n", item.IsDirty)
    fmt.Printf("是否强制存储: %v\n", item.IsMysql)
    fmt.Printf("最后修改时间: %v\n", item.Timestamp)
}

// 清空缓存
dataAccess.ClearCache()
```

## 继承使用

### 创建具体的数据访问管理器

```go
type DataAccessManager struct {
    ymd_dataaccess.YmdDataAccessBase
}

func NewDataAccessManager(app pitaya.Pitaya, dataAccessInfo *ymd_dataaccess.DataAccessInfo) *DataAccessManager {
    return &DataAccessManager{
        YmdDataAccessBase: ymd_dataaccess.NewYmdDataAccessBase(app, dataAccessInfo),
    }
}

// 实现具体的业务逻辑
func (dm *DataAccessManager) SaveUser(userID string, userData interface{}) error {
    // 1. 先保存到缓存
    err := dm.SetCache(fmt.Sprintf("user:%s", userID), userData, false)
    if err != nil {
        return fmt.Errorf("保存用户数据到缓存失败: %v", err)
    }

    // 2. 如果有Redis客户端，也保存到Redis
    if redisClient := dm.GetRedisClient(); redisClient != nil {
        // Redis存储逻辑
    }

    return nil
}

func (dm *DataAccessManager) LoadUser(userID string) (interface{}, error) {
    // 1. 先从缓存读取
    if value, exists := dm.GetCache(fmt.Sprintf("user:%s", userID)); exists {
        return value, nil
    }

    // 2. 缓存没有，从Redis读取
    if redisClient := dm.GetRedisClient(); redisClient != nil {
        // Redis读取逻辑
    }

    // 3. Redis没有，从MySQL读取
    if mysqlClient := dm.GetMysqlClient(); mysqlClient != nil {
        // MySQL读取逻辑
    }

    return nil, fmt.Errorf("用户数据不存在: %s", userID)
}
```

## 生命周期管理

### 1. 初始化阶段
- 连接数据库（MySQL、Redis、MongoDB）
- 验证连接状态
- 设置默认配置

### 2. 运行阶段
- 处理缓存操作
- 执行定时同步任务
- 监控缓存状态

### 3. 关闭阶段
- 停止定时器
- 强制同步所有脏数据
- 关闭数据库连接

## 配置选项

### 同步间隔
```go
// 默认15分钟，可自定义
dataAccess.SetSyncInterval(5 * time.Minute)  // 5分钟
dataAccess.SetSyncInterval(30 * time.Minute) // 30分钟
```

### 缓存策略
- **普通缓存**: `SetCache(key, value, false)` - 按定时策略同步
- **强制缓存**: `SetCache(key, value, true)` - 立即同步到MySQL

## 性能优化

### 1. 缓存命中率
- 优先使用内存缓存
- Redis作为二级缓存
- MySQL作为最终存储

### 2. 批量操作
- 定时批量同步减少数据库压力
- 支持事务操作提高数据一致性

### 3. 连接池管理
- MySQL连接池配置
- Redis连接池优化
- 自动重连机制

## 错误处理

### 1. 连接失败
- 数据库连接失败时记录错误日志
- 支持部分服务降级

### 2. 同步失败
- 同步失败时记录详细错误信息
- 支持重试机制

### 3. 数据一致性
- 关闭时强制同步确保数据不丢失
- 支持手动触发同步

## 监控和调试

### 1. 缓存统计
```go
stats := dataAccess.GetCacheStats()
// 返回：
// - total_items: 总缓存项数
// - dirty_items: 脏数据项数
// - mysql_items: 强制存储项数
// - cache_size_mb: 缓存大小(MB)
// - last_sync: 最后同步时间
```

### 2. 日志记录
- 初始化过程日志
- 同步操作日志
- 错误和警告日志

## 最佳实践

### 1. 缓存键命名
```go
// 使用冒号分隔的层次结构
"user:1001"           // 用户数据
"user:1001:profile"   // 用户档案
"user:1001:inventory" // 用户背包
"room:2001:players"   // 房间玩家列表
```

### 2. 数据更新策略
```go
// 频繁更新的数据使用普通缓存
dataAccess.SetCache("user:1001:position", position, false)

// 重要数据使用强制缓存
dataAccess.SetCache("user:1001:profile", profile, true)
```

### 3. 错误处理
```go
if err := dataAccess.SetCache(key, value, false); err != nil {
    // 记录错误日志
    logger.Log.Errorf("设置缓存失败: %v", err)
    
    // 尝试降级处理
    if mysqlClient := dataAccess.GetMysqlClient(); mysqlClient != nil {
        // 直接存储到MySQL
    }
}
```

## 注意事项

1. **内存使用**: 缓存数据会占用内存，注意监控内存使用情况
2. **同步频率**: 同步频率过高会增加数据库压力，过低可能丢失数据
3. **错误处理**: 数据库连接失败时，缓存功能仍可正常使用
4. **关闭顺序**: 确保在应用关闭前调用 `BeforeShutdown()` 和 `Shutdown()`

## 扩展功能

### 1. 自定义序列化
- 支持自定义数据序列化方式
- 可扩展支持更多数据类型

### 2. 事件回调
- 支持缓存更新事件
- 支持同步完成事件

### 3. 集群支持
- 支持多实例间的缓存同步
- 支持分布式锁机制
