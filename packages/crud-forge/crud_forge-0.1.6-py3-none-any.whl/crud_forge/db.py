from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
from sqlalchemy import create_engine, Engine, inspect, text
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from functools import lru_cache

@dataclass
class DBConfig:
    db_type: str  # database type (sqlite, postgresql, mysql)
    user: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    database: Optional[str] = None
    port: Optional[int] = None

    def __post_init__(self):
        """Initialize the DBConfig with default values for port and host based on the database type."""
        # * list of ['db_type', default_port, default_host]
        db_configs: List[Tuple[str, Optional[int], Optional[str]]] = [
            ('sqlite', None, None),
            ('postgresql', 5432, 'localhost'),
            ('mysql', 3306, 'localhost'),
            # * Add new database types here in the future
        ]

        for db, default_port, default_host in db_configs:
            if self.db_type == db:  # * if the db_type matches the current db
                match (self.port, self.host):  # * match the port and host
                    case (None, None): self.port, self.host = default_port, default_host
                    case (None, _): self.port = default_port
                    case (_, None): self.host = default_host
                break
        else: raise ValueError(f"Unsupported database type: {self.db_type}")
        if not self.database: raise ValueError("Database name must be provided")

    @property
    def url(self) -> str:
        match self.db_type:
            case 'sqlite': return f"{self.db_type}:///{self.database}"
            case 'postgresql' | 'mysql':
                if not all([self.user, self.password, self.host]):
                    raise ValueError(f"Incomplete configuration for {self.db_type}")
                return f"{self.db_type}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            case _: raise ValueError(f"Unsupported database type: {self.db_type}")


@dataclass
class ColumnMetadata:
    name: str
    type: str
    is_primary_key: bool
    is_foreign_key: bool = False
    is_enum: bool = False  # Add this line

@dataclass
class TableMetadata:
    name: str
    columns: List[ColumnMetadata] = field(default_factory=list)

@dataclass
class SchemaMetadata:
    name: str
    tables: Dict[str, TableMetadata] = field(default_factory=dict)


@dataclass
class EnumMetadata:
    name: str
    values: List[str]

class DatabaseManager:
    """Manages database connection, session creation, metadata retrieval, and enum information."""

    def __init__(self, db_url: Optional[str] = None, **kwargs):
        """Initialize the DatabaseManager."""
        try:
            self.db_config = self._create_db_config(db_url, **kwargs)
            self.engine: Engine = create_engine(self.db_config.url)
            self.SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.metadata: Dict[str, SchemaMetadata] = self._get_metadata()
            self.enums: Dict[str, Dict[str, EnumMetadata]] = self._get_enum_metadata()
        except Exception as e:
            print(f"Error initializing DatabaseManager: {str(e)}")
            raise

    @staticmethod
    def _create_db_config(db_url: Optional[str], **kwargs) -> DBConfig:
        if db_url:
            parts = db_url.split('://')
            if len(parts) != 2:
                raise ValueError("Invalid database URL format")
            db_type = parts[0]
            rest = parts[1].split('@')
            if len(rest) == 2:
                user_pass, host_port_db = rest
                user, password = user_pass.split(':')
                host_port, database = host_port_db.split('/')
                if ':' in host_port:
                    host, port = host_port.split(':')
                    return DBConfig(db_type=db_type, user=user, password=password, host=host, port=int(port), database=database)
                else:
                    return DBConfig(db_type=db_type, user=user, password=password, host=host_port, database=database)
            else:
                raise ValueError("Invalid database URL format")
        elif all(key in kwargs for key in ['db_type', 'user', 'password', 'host', 'database']):
            return DBConfig(**kwargs)
        else:
            raise ValueError("Insufficient database configuration provided")

    def get_db(self) -> Session:
        """Provide a database session."""
        db: Session = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Connection test successful")
            return True
        except SQLAlchemyError as e:
            print(f"Connection test failed: {str(e)}")
            return False


    @lru_cache(maxsize=None)
    def _get_metadata(self) -> Dict[str, SchemaMetadata]:
        """Retrieve all metadata including schemas, tables, and columns."""
        inspector = inspect(self.engine)
        metadata: Dict[str, SchemaMetadata] = {}

        match self.db_config.db_type:
            case 'postgresql':
                schemas = [schema for schema in inspector.get_schema_names() 
                           if schema not in ('information_schema', 'pg_catalog')]
            case 'mysql' | 'sqlite': schemas = ['default']
            case _: schemas = inspector.get_schema_names()

        for schema in schemas:
            schema_metadata = SchemaMetadata(name=schema)
            
            for table in inspector.get_table_names(schema=schema if schema != 'default' else None):
                columns = self._get_table_columns(inspector, schema, table)
                schema_metadata.tables[table] = TableMetadata(name=table, columns=columns)

            metadata[schema] = schema_metadata

        return metadata

    @staticmethod
    def _get_table_columns(inspector: Any, schema: str, table: str) -> List[ColumnMetadata]:
        """Get the columns of a specific table."""
        columns = inspector.get_columns(table, schema=None if schema == 'default' else schema)
        pk_constraint = inspector.get_pk_constraint(table, schema=None if schema == 'default' else schema)
        pk_columns = pk_constraint['constrained_columns'] if pk_constraint else []
        fk_constraints = inspector.get_foreign_keys(table, schema=None if schema == 'default' else schema)
        fk_columns = [fk['constrained_columns'][0] for fk in fk_constraints]
        
        return [ColumnMetadata(
            name=col['name'],
            type=str(col['type']),
            is_primary_key=col['name'] in pk_columns,
            is_foreign_key=col['name'] in fk_columns,
            is_enum=isinstance(col['type'], sqlalchemy.Enum)  # Add this line
        ) for col in columns]

    def get_table_columns(self, schema: str, table: str) -> List[ColumnMetadata]:
        """Get the columns of a specific table."""
        return self.metadata[schema].tables[table].columns

    # @property  # means that the method can be accessed as an attribute
    def _get_enum_metadata(self) -> Dict[str, Dict[str, EnumMetadata]]:
        """Retrieve all enum metadata."""
        if self.db_config.db_type != 'postgresql':
            return {}  # Return empty dict for non-PostgreSQL databases

        enum_query = """
        SELECT 
            n.nspname AS schema_name,
            t.typname AS enum_name,
            array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
        GROUP BY schema_name, enum_name
        ORDER BY schema_name, enum_name;
        """

        enum_metadata: Dict[str, Dict[str, EnumMetadata]] = {}

        with self.engine.connect() as connection:
            result = connection.execute(text(enum_query))
            for row in result:
                schema_name, enum_name, enum_values = row
                if schema_name not in enum_metadata:
                    enum_metadata[schema_name] = {}
                enum_metadata[schema_name][enum_name] = EnumMetadata(name=enum_name, values=enum_values)

        return enum_metadata

    # def get_enum_metadata(self, schema: str, enum_name: str) -> Optional[EnumMetadata]:
    #     """Get the metadata for a specific enum."""
    #     return self.enums.get(schema, {}).get(enum_name)

    # def print_enum_metadata(self):
    #     """Print all enum metadata in a formatted way."""
    #     for schema_name, schema_enums in self.enums.items():
    #         print(f"\n\033[93m[Schema]\033[0m {schema_name}")
    #         for enum_name, enum_metadata in schema_enums.items():
    #             print(f"\n\t\033[96m[Enum]\033[0m \033[1m{schema_name}.\033[4m{enum_name}\033[0m")
    #             for value in enum_metadata.values:
    #                 print(f"\t\t{value}")

# Example usage:
# db_manager = DatabaseManager(db_url="postgresql://user:pass@localhost/db")
# print(db_manager.schemas)
# print(db_manager.tables)
# print(db_manager.get_table_columns('public', 'users'))
