"""
数据库工具
"""

from .tools import now
from .tools import logger
from .tools import to_excel

__all__ = [
    "redisdb",
    "mongodb",
    "mongo_distinct",
    "mongo_insert",
    "mongo_sample",
    "mongo_tongji",
    "mongo_to_csv",
    "mongo_to_jsonl",
    "oss2_find_file",
    "oss2_upload_content",
    "oss2_upload_file",
]


def oss2_upload_file(bucket, key, filepath, proxies=None):
    """
    上传文件到 oss

    bucket: oss2.Bucket 对象
    key: 上传到OSS的文件名
    filepath: 本地文件路径
    proxies: 代理
    """
    import oss2

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return
    if proxies:
        bucket.proxies = proxies
    try:
        z = bucket.put_object_from_file(key, filepath)
        logger.success(f"文件 {filepath} 上传成功, 文件路径: {key}")
        return z
    except Exception as e:
        logger.error(f"oss2_upload_file 发生错误: {e}")
        return


def oss2_upload_content(bucket, key, content, proxies=None):
    """
    上传 content 到 oss

    bucket: oss2.Bucket 对象
    key: 上传到OSS的文件名
    content: 本地内容content
    proxies: 代理
    """
    import oss2

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return
    if proxies:
        bucket.proxies = proxies
    try:
        z = bucket.put_object(key, content)
        logger.success(f"文件上传成功, 文件路径: {key}")
        return z
    except Exception as e:
        logger.error(f"oss2_upload_content 发生错误: {e}")
        return


def oss2_find_file(bucket, prefix, size1=0, size2=1048576000):
    """
    寻找 oss 文件, 指定 size1 和 size2 可以筛选特定大小的文件。默认单位为 KB。返回值为字典。

    - 可以通过 len 统计文件数量。
    - 可以通过 sum 统计返回值字典的 values 统计文件夹文件的总大小, 单位为KB。

    bucket: oss2.Bucket 对象
    prefix: 文件夹路径, 例如 'etl/atk'
    size1: 文件大小下限,默认0
    size2: 文件大小上限,默认 1000G；如果需要筛选无用pdf, 可以设置上限20。
    """
    import oss2

    if not isinstance(bucket, oss2.Bucket):
        print("bucket 不符合要求")
        return
    d = {}
    for obj in oss2.ObjectIterator(bucket, prefix):
        t = obj.size / 1024
        if size1 < t < size2 and not obj.is_prefix():
            print(f"文件名:{obj.key}  文件大小: {t:.2f} KB")
            d[obj.key] = t
    return d


def redisdb(host="localhost", port=6379, db=0, password=None):
    """
    连接 redis 数据库
    """
    import redis

    return redis.Redis(host=host, port=port, db=db, password=password)


def mongodb(host, database, port: int | None = None, **kwargs):
    """
    连接 MongoDB

    host: mongo 链接
    database: 数据库名称
    port: mongo 端口

    host 有密码格式: "mongodb://username:password@192.168.0.1:27017/"
    host 无密码格式: "mongodb://192.168.0.1:27017/"
    """
    from pymongo import MongoClient

    try:
        client = MongoClient(host, port, **kwargs)
        db = client[database]
        db.list_collection_names()
        logger.success(f"MongoDB 成功连接到 {database}")
        return db
    except Exception as e:
        logger.error("MongoDB 连接失败:", str(e))
        return None


def mongo_sample(
    table,
    match: dict = {},
    *,
    size: int = 1000,
    excel: bool = True,
) -> list:
    """
    mongodb 随机样本抽样

    table: mongo 表(集合), Collection 对象
    match: 匹配条件，默认不筛选
    size: 随机样本数量
    excel: 是否导出 excel文件, 默认 True
    """
    results = list(
        table.aggregate([
            {"$match": match},
            {"$sample": {"size": size}},
        ])
    )
    if excel:
        import pandas as pd

        filename = f"{now(7)}_{table}_sample_{size}.xlsx"
        df = pd.DataFrame(results)
        to_excel(df, filename)

    return results


def mongo_tongji(
    mongodb,
    prefix: str = "",
    tongji_table: str = "tongji",
) -> dict:
    """
    统计 mongodb 每个集合的`文档数量`

    mongodb: mongo 库
    prefix: mongo 表(集合)前缀, 默认空字符串可以获取所有表, 字段名称例如 `统计_20240101`。
    tongji_table: 统计表名称，默认为 tongji
    """

    tongji = mongodb[tongji_table]
    key = prefix if prefix else f"统计_{now(7)}"
    collection_count_dict = {
        **(
            tongji.find_one({"key": key}).get("count")
            if tongji.find_one({"key": key})
            else {}
        ),
        **({
            i: mongodb[i].estimated_document_count()
            for i in mongodb.list_collection_names()
            if i.startswith(prefix)
        }),
    }
    tongji.update_one(
        {"key": prefix if prefix else f"统计_{now(7)}"},
        {"$set": {"count": collection_count_dict}},
        upsert=True,
    )
    return dict(sorted(collection_count_dict.items()))


def mongo_distinct(table, *fields):
    """
    mongo distinct 去重

    table: mongo 表(集合), Collection 对象
    fields: 字段名称，支持多个字段
    """
    pipeline = [{"$group": {"_id": {i: f"${i}" for i in fields}}}]
    agg_results = table.aggregate(pipeline)
    results = [i["_id"] for i in agg_results]
    return results


def mongo_to_csv(table, output_file: str | None = None, batch_size: int = 1000):
    """
    从MongoDB集合中导出数据到CSV文件

    table: MongoDB的集合名称或Collection对象
    output_file: 导出的CSV文件路径, 默认值为`表名.csv`
    batch_size: 批处理大小，默认为1000
    """
    import pymongo
    import csv

    if not isinstance(table, pymongo.collection.Collection):
        raise ValueError("table 必须是 MongoDB Collection对象")

    table_name = table.name

    if not output_file:
        output_file = f"{table_name}.csv"

    try:
        count_documents = table.estimated_document_count()
        logger.info(f"开始导出 {table_name}, 总数据量 {count_documents}")
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=1)
            cursor = table.find().batch_size(batch_size)
            header = table.find_one().keys() if table.find_one() else []
            writer.writerow(header)
            for doc in cursor:
                record = []
                for key in header:
                    if key not in doc:
                        record.append("")
                    else:
                        record.append(str(doc[key]))
                writer.writerow(record)
        logger.success(f"{table_name} 导出成功, 文件路径: {output_file}")
    except Exception as e:
        logger.error(f"{table_name} 导出发生错误: {e}")


def mongo_to_jsonl(table, output_file: str | None = None, batch_size: int = 1000):
    """
    mongo 导出 jsonl

    table: mongo 表(集合), Collection 对象
    output_file: 导出的 jsonl 文件名, 默认值为`表名.jsonl`
    batch_size: 批处理大小，默认为1000
    """
    import pymongo
    import json

    if not isinstance(table, pymongo.collection.Collection):
        raise ValueError("table 必须是 MongoDB Collection对象")
    
    table_name = table.name

    if not output_file:
        output_file = f"{table_name}.jsonl"
    try:
        count_documents = table.estimated_document_count()
        logger.info(f"开始导出 {table_name}, 总数据量 {count_documents}")
        with open(output_file, "w", encoding="utf-8") as f:
            cursor = table.find().batch_size(batch_size)
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
        logger.success(f"{table_name} 导出成功, 文件路径: {output_file}")
    except Exception as e:
        logger.error(f"{table_name} 导出发生错误: {e}")


def mongo_insert(table, data: list[dict] | dict):
    """
    mongo 批量插入

    table: mongo 表(集合), Collection 对象
    data: 数据列表，每个元素为一个字典
    """
    try:
        if isinstance(data, dict):
            data = [data]
        table.insert_many(data, ordered=False)
    except Exception:
        pass
