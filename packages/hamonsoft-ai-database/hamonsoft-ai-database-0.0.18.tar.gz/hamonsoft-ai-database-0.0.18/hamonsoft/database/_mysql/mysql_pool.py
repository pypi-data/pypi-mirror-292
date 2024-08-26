from hamonsoft.database._mysql.mysql import MySQL
from hamonsoft.database.db_pool import DBPool


class MySQLPool(DBPool):
    def __init__(self, max_count=1, **kwargs):
        super().__init__()
        try:
            for _ in range(max_count):
                dbImpl = MySQL()
                dbImpl.connect(**kwargs)

                self.queue.put(dbImpl)
                self.allList.append(dbImpl)

        except Exception:
            raise
