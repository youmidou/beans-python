from dataclasses import dataclass
from typing import Any, List, Optional, Dict, Type
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool

Base = declarative_base()


@dataclass
class PostgresqlInfo:
    host: str
    port: int
    user: str
    password: str
    database: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600
    echo: bool = False


class PostgresqlClient:
    def __init__(self, info: PostgresqlInfo):
        self._info = info
        self._engine = None
        self._session_factory = None

    def connect(self):
        """连接数据库"""
        connection_string = (
            f"postgresql://{self._info.user}:{self._info.password}"
            f"@{self._info.host}:{self._info.port}/{self._info.database}"
        )

        self._engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=self._info.pool_size,
            max_overflow=self._info.max_overflow,
            pool_recycle=self._info.pool_recycle,
            echo=self._info.echo,
        )

        self._session_factory = sessionmaker(bind=self._engine)

    def AutoMigrate(self, *models_or_bases: Any) -> None:
        """自动迁移表结构"""
        if self._engine is None:
            raise RuntimeError("Database not connected. Call connect() first.")

        # 设置表的基类
        for model in models_or_bases:
            if not hasattr(model, '__table__'):
                # 动态创建表类
                model.__bases__ = (Base,)

        Base.metadata.create_all(self._engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        if self._session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._session_factory()

    def close(self):
        """关闭连接"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None

    # CRUD 操作
    def insert(self, obj: Any) -> bool:
        """插入单条记录"""
        session = self.get_session()
        try:
            session.add(obj)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def insert_many(self, objs: List[Any]) -> bool:
        """批量插入记录"""
        session = self.get_session()
        try:
            session.add_all(objs)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update(self, obj: Any) -> bool:
        """更新记录"""
        session = self.get_session()
        try:
            session.merge(obj)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete(self, obj: Any) -> bool:
        """删除记录"""
        session = self.get_session()
        try:
            session.delete(obj)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def query(self, model: Type, filters: Optional[Dict] = None) -> List[Any]:
        """查询记录"""
        session = self.get_session()
        try:
            query = session.query(model)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(model, key) == value)
            return query.all()
        finally:
            session.close()

    def query_one(self, model: Type, filters: Optional[Dict] = None) -> Optional[Any]:
        """查询单条记录"""
        session = self.get_session()
        try:
            query = session.query(model)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(model, key) == value)
            return query.first()
        finally:
            session.close()

    def query_by_id(self, model: Type, id_value: Any) -> Optional[Any]:
        """根据主键查询"""
        session = self.get_session()
        try:
            return session.query(model).get(id_value)
        finally:
            session.close()

    def execute_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """执行原生 SQL"""
        session = self.get_session()
        try:
            result = session.execute(text(sql), params or {})
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def count(self, model: Type, filters: Optional[Dict] = None) -> int:
        """统计记录数"""
        session = self.get_session()
        try:
            query = session.query(model)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(model, key) == value)
            return query.count()
        finally:
            session.close()