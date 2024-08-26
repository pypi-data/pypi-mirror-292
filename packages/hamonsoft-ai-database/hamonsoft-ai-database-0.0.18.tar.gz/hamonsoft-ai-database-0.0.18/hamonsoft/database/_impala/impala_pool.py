from hamonsoft.database._impala.impala import Impala
from hamonsoft.database.db_pool import DBPool


class ImpalaPool(DBPool):
    def __init__(self, max_count=1, **kwargs):
        super().__init__()
        try:
            for _ in range(max_count):
                dbImpl = Impala()
                dbImpl.connect(**kwargs)
                self.queue.put(dbImpl)
                self.allList.append(dbImpl)

        except Exception:
            raise