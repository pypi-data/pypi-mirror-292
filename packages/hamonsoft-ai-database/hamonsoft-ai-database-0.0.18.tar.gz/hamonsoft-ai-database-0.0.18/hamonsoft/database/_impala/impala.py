import impala.dbapi

from hamonsoft.database.db_wrapper import DBWrapper


class Impala(DBWrapper):
    def __init__(self):
        super().__init__()

    def __del__(self):
        pass

    def connect(self, *args, **kwargs):
        try:
            self.host = kwargs['host']
            self.port = kwargs['port']
            self.database = kwargs['database']

            self.connection = impala.dbapi.connect(**kwargs)
        except:
            raise

    def reconnect(self):
        try:
            self.connection.reconnect()
        except:
            raise

    def check_connection(self):
        try:
            result = self.execute('SELECT 1')
            if result:
                return True
            else:
                return False
        except:
            return False

    def execute(self, query, bindValue=None):
        try:
            self.cursor = self.connection.cursor()

            if bindValue is None:
                self.cursor.execute(query, self.bindValue)
            else:
                self.cursor.execute(query, bindValue)

            rowCount = self.cursor.rowcount
            self.cursor.close()

            return rowCount
        except:
            raise

    def execute_many(self, query, bindValue):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.executemany(query, bindValue)

            rowCount = self.cursor.rowcount
            self.cursor.close()

            return rowCount
        except:
            raise

    def select(self, query, bindValue=None):
        try:
            self.cursor = self.connection.cursor()
            if bindValue is None:
                self.cursor.execute(query, self.bindValue)
            else:
                self.cursor.execute(query, bindValue)

            # columns = [i[0].upper() for i in self.cursor.description ]
            columns = [i[0] for i in self.cursor.description]
            rows = self.cursor.fetchall()

            newRows = [dict(zip(columns, row)) for row in rows]

            self.cursor.close()

            return newRows
        except:
            raise

    def select_org(self, query, bindValue=None):
        try:
            self.cursor = self.connection.cursor()
            if bindValue is None:
                self.cursor.execute(query, self.bindValue)
            else:
                self.cursor.execute(query, bindValue)

            rows = self.cursor.fetchall()

            self.cursor.close()

            return rows
        except:
            raise

    def add_bind(self, key, value):
        self.bindValue[key] = value

    def clear_bind(self):
        self.bindValue.clear()

    def close(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()
