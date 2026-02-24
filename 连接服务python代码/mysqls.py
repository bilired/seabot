# /www/server/pyporject_evn/versions/3.10.14/bin/pip install mysql-connector-python
# /www/server/pyporject_evn/versions/3.10.14/bin/python3.10 mysql.py
import mysql.connector
from mysql.connector import Error, pooling


db_config = {
    'pool_name':"pool",
    'pool_size':10,
    'host': 'localhost',   # 数据库服务器地址
    'user': 'bw_tp_coding',  # 数据库用户名
    'password': 'bw_tp_coding',  # 数据库密码
    'database': 'bw_tp_coding' # 数据库名称
}

# 创建全局连接池（实际项目中可放在单独模块）
db_pool = pooling.MySQLConnectionPool(**db_config)


def upsert_data_pooled(table_name, primary_keys, data_dict, connection_pool=None):
    pool = connection_pool or db_pool
    
    # 验证关键字段
    missing_keys = [k for k in (primary_keys or []) if k not in data_dict]
    if missing_keys:
        raise ValueError(f"关键字段缺失: {', '.join(missing_keys)}")

    try:
        # 从池中获取连接
        conn = pool.get_connection()
        cursor = conn.cursor()

        # 1. 检查primary_keys是否为空
        if not primary_keys:  # 如果没有提供主键
            # 执行普通 INSERT
            columns = list(data_dict.keys())
            values = list(data_dict.values())
            placeholders = ['%s'] * len(columns)
            
            sql = f"""
            INSERT INTO `{table_name}`
                ({', '.join([f'`{c}`' for c in columns])})
            VALUES
                ({', '.join(placeholders)})
            """
            cursor.execute(sql, values)
        
        else:
            # 2. 有主键时，检查数据是否存在
            where_clause = " AND ".join([f"`{k}` = %s" for k in primary_keys])
            sql_check = f"SELECT COUNT(*) FROM `{table_name}` WHERE {where_clause}"
            cursor.execute(sql_check, [data_dict[k] for k in primary_keys])
            exists = cursor.fetchone()[0] > 0

            # 3. 根据存在性执行不同操作
            if exists:
                # 执行 UPDATE
                update_cols = [col for col in data_dict if col not in primary_keys]
                if not update_cols:
                    return 0  # 没有可更新字段
                
                set_clause = ", ".join([f"`{k}` = %s" for k in update_cols])
                where_values = [data_dict[k] for k in primary_keys]
                update_values = [data_dict[k] for k in update_cols] + where_values
                
                sql = f"""
                UPDATE `{table_name}`
                SET {set_clause}
                WHERE {where_clause}
                """
                cursor.execute(sql, update_values)
            else:
                # 执行 INSERT
                columns = list(data_dict.keys())
                values = list(data_dict.values())
                placeholders = ['%s'] * len(columns)
                
                sql = f"""
                INSERT INTO `{table_name}`
                    ({', '.join([f'`{c}`' for c in columns])})
                VALUES
                    ({', '.join(placeholders)})
                """
                cursor.execute(sql, values)
        
        conn.commit()
        return cursor.rowcount
    
    except Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"数据库操作失败: {e}") from e
    
    finally:
        # 归还连接到池
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def upsert_data_pooled_bak(table_name, primary_keys, data_dict, connection_pool=None):
    if primary_keys is None:
        primary_keys = []
    pool = connection_pool or db_pool
    
    # 验证关键字段
    missing_keys = [k for k in primary_keys if k not in data_dict]
    if missing_keys:
        raise ValueError(f"关键字段缺失: {', '.join(missing_keys)}")

    try:
        # 从池中获取连接
        conn = pool.get_connection()
        cursor = conn.cursor()

        # 准备SQL语句
        columns = list(data_dict.keys())
        values = list(data_dict.values())
        placeholders = ['%s'] * len(columns)
        
        # 核心修改：根据关键字段是否为空选择SQL语句
        if not primary_keys:
            # 当关键字段为空时，仅执行普通插入
            sql = f"""
            INSERT INTO `{table_name}`
                ({', '.join([f'`{c}`' for c in columns])})
            VALUES
                ({', '.join(placeholders)})
            """
        else:
            # 原逻辑：生成更新字段（排除关键字段）
            update_set = [f"`{k}` = VALUES(`{k}`)" 
                         for k in columns if k not in primary_keys]
            
            if not update_set:  # 全是关键字段的特殊处理
                update_set = [f"`{primary_keys[0]}` = VALUES(`{primary_keys[0]}`)"]

            sql = f"""
            INSERT INTO `{table_name}`
                ({', '.join([f'`{c}`' for c in columns])})
            VALUES
                ({', '.join(placeholders)})
            ON DUPLICATE KEY UPDATE
                {', '.join(update_set)}
            """
        
        # 执行操作
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount
    
    except Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"数据库操作失败: {e}") from e
    
    finally:
        # 归还连接到池
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()  # 实际上是归还到连接池

# # 批量处理优化
# def bulk_upsert(table_name, primary_keys, data_dicts, batch_size=100):
#     """
#     批量插入/更新优化
#     :param data_dicts: 字典列表
#     :param batch_size: 每批处理数量
#     :return: 总受影响行数
#     """
#     total_affected = 0
#     for i in range(0, len(data_dicts), batch_size):
#         batch = data_dicts[i:i + batch_size]
#         with db_pool.get_connection() as conn:
#             cursor = conn.cursor()
#             for data in batch:
#                 try:
#                     affected = upsert_data_pooled(
#                         table_name, 
#                         primary_keys, 
#                         data, 
#                         connection_pool=None
#                     )
#                     total_affected += affected
#                 except Exception as e:
#                     print(f"记录处理失败: {e}")
#             cursor.close()
#     return total_affected


# users_table = "test"
# keys = ["id"]

# result = upsert_data_pooled(
#     users_table,
#     keys,
#     {"id": 1, "name": "张三", "email": "zhang@example.com", "score": 95}
# )
# print(f"单条操作结果: 影响{result}行")

# 使用示例
if __name__ == "__main__":

    conn = db_pool.get_connection()  # 测试连接池获取连接
    # 使用cursor()方法创建游标
    cursor = conn.cursor()
    # 执行SQL查询
    cursor.execute("SELECT VERSION()")  # 示例：获取MySQL版本
    # 获取单条数据
    data = cursor.fetchone()
    print("MySQL版本:", data)
    # 关闭连接
    cursor.close()

    

    # 示例数据
    users_table = "test"
    keys = []
    
    # 单条操作
    result = upsert_data_pooled(
        users_table,
        keys,
        {"id": 1, "name": "张三", "email": "zhang@example.com", "score": 95}
    )
    print(f"单条操作结果: 影响{result}行")
    
    # 批量操作
    # user_list = [
    #     {"id": 2, "name": "李四", "email": "li@example.com"},
    #     {"id": 3, "name": "王五", "email": "wang@example.com", "age": 28},
    #     # ... 更多数据
    # ]
    
    # total = bulk_upsert(users_table, keys, user_list)
    # print(f"批量操作结果: 共影响{total}行")