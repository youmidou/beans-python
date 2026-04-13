#!/usr/bin/env python3
"""测试 Redis 数据访问功能"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from examples.GameServer.game_modules.game_dataaccess.DataAccessManager import DataAccessManager
from examples.GameServer.game_modules.game_dataaccess.dbtable.DataGameUser import NewDataGameUser
from pkg.logger import logger


def test_redis_only():
    """测试 Redis 数据访问功能"""
    print("=" * 60)
    print("测试 Redis 数据访问功能")
    print("=" * 60)

    # 初始化 logger
    logger.Log.init_config("logs/test.log", level=logger.INFO)

    # 初始化 DataAccessManager
    print("\n1. 初始化 DataAccessManager...")
    manager = DataAccessManager()
    try:
        manager.initialize()
        print("✓ DataAccessManager 初始化成功")
    except Exception as e:
        import traceback
        print(f"✗ DataAccessManager 初始化失败: {e}")
        traceback.print_exc()
        return

    # 测试用户 ID 列表
    test_user_ids = [1001, 1002, 1003, 1004, 1005]

    # 创建并保存测试用户（仅 Redis）
    print("\n2. 创建并保存测试用户到 Redis...")
    for user_id in test_user_ids:
        print(f"\n  用户 {user_id}:")

        # 创建新用户数据
        game_user = NewDataGameUser(user_id)
        print(f"    - 创建用户数据: UserId={game_user.user_id}, NickName={game_user.DBRole.NickName}")

        # 仅保存到 Redis
        success = manager.SetDataGameUser(user_id, game_user, isPgsql=False)
        if success:
            print(f"    ✓ 保存到 Redis 成功")
        else:
            print(f"    ✗ 保存失败")

    # 测试从 Redis 读取
    print("\n3. 从 Redis 读取用户数据...")
    for user_id in test_user_ids:
        print(f"\n  用户 {user_id}:")
        data = manager.GetDataGameUser(user_id)
        if data:
            print(f"    ✓ 读取成功")
            print(f"      UserId: {data.user_id}")
            print(f"      NickName: {data.DBRole.NickName}")
            print(f"      Inbox UserId: {data.DBInbox.UserId}")
        else:
            print(f"    ✗ 读取失败")

    # 更新用户昵称测试
    print("\n4. 更新用户昵称测试...")
    test_user_id = test_user_ids[0]
    data = manager.GetDataGameUser(test_user_id)
    if data:
        old_nickname = data.DBRole.NickName
        data.DBRole.NickName = "SuperUser:1001"
        success = manager.SetDataGameUser(test_user_id, data, isPgsql=False)
        if success:
            print(f"  ✓ 用户 {test_user_id} 昵称更新成功")
            print(f"    旧昵称: {old_nickname}")
            print(f"    新昵称: {data.DBRole.NickName}")

            # 验证更新
            updated_data = manager.GetDataGameUser(test_user_id)
            if updated_data and updated_data.DBRole.NickName == "SuperUser:1001":
                print(f"  ✓ 验证更新成功")
            else:
                print(f"  ✗ 验证更新失败")
        else:
            print(f"  ✗ 更新失败")

    # 测试缓存过期
    print("\n5. 测试缓存清除...")
    redis_client = manager.dataAccess.get_redis()
    for user_id in test_user_ids[:2]:  # 只清除前两个
        key = f"GameUser:{user_id}"
        redis_client.delete(key)
        print(f"  ✓ 用户 {user_id} 缓存已清除")

    print("\n6. 验证缓存清除...")
    for user_id in test_user_ids[:2]:
        data = manager.GetDataGameUser(user_id)
        if data is None:
            print(f"  ✓ 用户 {user_id} 缓存已清除（读取为空）")
        else:
            print(f"  ✗ 用户 {user_id} 缓存仍然存在")

    # 统计测试
    print("\n7. Redis 操作统计...")
    print(f"  - 创建用户数: {len(test_user_ids)}")
    print(f"  - 成功读取数: {len([uid for uid in test_user_ids if manager.GetDataGameUser(uid)])}")
    print(f"  - 更新操作: 1 次")
    print(f"  - 删除操作: 2 次")

    print("\n" + "=" * 60)
    print("Redis 测试完成 ✓")
    print("=" * 60)


if __name__ == "__main__":
    test_redis_only()
