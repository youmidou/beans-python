from contextlib import contextmanager
from dataclasses import dataclass
import re
from typing import Optional, Any

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker
from pkg.logger import logger


@dataclass
class MysqlInfo:
    host: str
    port: int
    user: str
    password: str
    database: str
    pool_size: int = 30
    max_overflow: int = 50
    pool_recycle: int = 900
    pool_pre_ping: bool = True
    charset: str = "utf8mb4"


class MysqlClient:
    def __init__(self, info: MysqlInfo):
        self._info = info
        self._engine = None
        self._session_factory = None

    def _build_url(self, database: Optional[str] = None) -> URL:
        info = self._info
        return URL.create(
            "mysql+pymysql",
            username=info.user,
            password=info.password,
            host=info.host,
            port=info.port,
            database=database,
            query={"charset": info.charset},
        )

    def _create_engine(self, database: Optional[str] = None):
        info = self._info
        return create_engine(
            self._build_url(database),
            echo=False,
            pool_size=info.pool_size,
            max_overflow=info.max_overflow,
            pool_recycle=info.pool_recycle,
            pool_pre_ping=info.pool_pre_ping,
            pool_use_lifo=True,
        )

    def _ensure_database_exists(self) -> None:
        database = self._info.database
        if not database:
            raise ValueError("MysqlInfo.database is required.")
        if not re.fullmatch(r"[0-9A-Za-z_]+", self._info.charset):
            raise ValueError(f"Unsupported MySQL charset: {self._info.charset}")

        quoted_database = f"`{database.replace('`', '``')}`"
        bootstrap_engine = self._create_engine(database=None)
        try:
            logger.Log.Info(
                "MysqlClient ensure database start: host=%s port=%s database=%s",
                self._info.host,
                self._info.port,
                database,
            )
            with bootstrap_engine.connect() as conn:
                conn.execute(
                    text(
                        f"CREATE DATABASE IF NOT EXISTS {quoted_database} "
                        f"CHARACTER SET {self._info.charset}"
                    )
                )
                conn.commit()
            logger.Log.Info(
                "MysqlClient ensure database success: host=%s port=%s database=%s",
                self._info.host,
                self._info.port,
                database,
            )
        except Exception as e:
            logger.Log.Exception(
                "MysqlClient ensure database failed: host=%s port=%s database=%s error=%s",
                self._info.host,
                self._info.port,
                database,
                str(e),
            )
            raise
        finally:
            bootstrap_engine.dispose()

    def connect(self) -> None:
        if self._engine is not None:
            self.close()
        logger.Log.Info(
            "MysqlClient connect start: host=%s port=%s database=%s",
            self._info.host,
            self._info.port,
            self._info.database,
        )
        try:
            self._ensure_database_exists()
            self._engine = self._create_engine(database=self._info.database)
            # verify connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self._session_factory = sessionmaker(bind=self._engine, autoflush=False)
            logger.Log.Info(
                "MysqlClient connect success: host=%s port=%s database=%s",
                self._info.host,
                self._info.port,
                self._info.database,
            )
        except Exception as e:
            if self._engine is not None:
                self.close()
            logger.Log.Exception(
                "MysqlClient connect failed: host=%s port=%s database=%s error=%s",
                self._info.host,
                self._info.port,
                self._info.database,
                str(e),
            )
            raise

    def get_engine(self):
        if self._engine is None:
            raise RuntimeError("MysqlClient not connected. Call connect() first.")
        return self._engine

    def get_session_factory(self):
        if self._session_factory is None:
            raise RuntimeError("MysqlClient not connected. Call connect() first.")
        return self._session_factory

    @contextmanager
    def get_session(self) -> Session:
        if self._session_factory is None:
            raise RuntimeError("MysqlClient not connected. Call connect() first.")
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def auto_migrate(self, *models_or_bases: Any) -> None:
        if self._engine is None:
            raise RuntimeError("MysqlClient not connected. Call connect() first.")
        if not models_or_bases:
            raise ValueError("auto_migrate() requires at least one model, base, or metadata.")

        tables_by_metadata = {}
        metadata_list = []
        metadata_ids = set()

        for target in models_or_bases:
            if target is None:
                continue

            if isinstance(target, MetaData):
                target_metadata = target
                target_table = None
            elif hasattr(target, "__table__"):
                target_metadata = target.__table__.metadata
                target_table = target.__table__
            elif hasattr(target, "metadata"):
                target_metadata = target.metadata
                target_table = None
            else:
                raise TypeError(
                    f"Unsupported auto_migrate target: {target!r}. "
                    "Expected SQLAlchemy model, declarative base, or MetaData."
                )

            metadata_id = id(target_metadata)
            if target_table is None:
                if metadata_id not in metadata_ids:
                    metadata_list.append(target_metadata)
                    metadata_ids.add(metadata_id)
                tables_by_metadata.pop(metadata_id, None)
                continue

            if metadata_id in metadata_ids:
                continue
            tables_by_metadata.setdefault(metadata_id, (target_metadata, []))[1].append(target_table)

        for metadata in metadata_list:
            metadata.create_all(self._engine)
        for metadata, tables in tables_by_metadata.values():
            metadata.create_all(self._engine, tables=tables)

    def AutoMigrate(self, *models_or_bases: Any) -> None:
        self.auto_migrate(*models_or_bases)

    def close(self) -> None:
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
