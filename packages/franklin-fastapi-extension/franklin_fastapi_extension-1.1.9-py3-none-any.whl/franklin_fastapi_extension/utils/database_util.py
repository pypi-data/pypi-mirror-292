from sqlalchemy import create_engine
from config import logger

class Database:
    def __init__(self, db_name, db_user, db_password, db_host, db_port, db_type):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.db_type = db_type
        self._engine = None

    def _get_database_uri(self) -> str | None:
        if self.db_type == 'sqlite':
            return f'sqlite:///{self.db_name}.db'
        elif self.db_type == 'mysql':
            return (f'mysql+pymysql://{self.db_user}:'
                    f'{self.db_password}@{self.db_host}:'
                    f'{self.db_port}/{self.db_name}')
        else:
            logger.error('Database type not supported')
            return None


    def get_engine(self):
        if not self._engine:
            self._engine = create_engine(self._get_database_uri())
        return self._engine

    def get_session(self):
        from sqlalchemy.orm import sessionmaker
        session = sessionmaker(bind=self.get_engine())
        return session()
