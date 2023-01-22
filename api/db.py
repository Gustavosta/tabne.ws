from sqlalchemy import create_engine
import os


with open('api/schemas.sql', 'r', encoding='UTF-8') as f:
    schema = f.read()


class DB:
    def __init__(self):
        self.engine = create_engine(os.environ.get('DATABASE_URL'))
        self.engine.execute(schema)

    def get_engine(self):
        return self.engine

    def get_session(self):
        return self.engine.connect()
    

