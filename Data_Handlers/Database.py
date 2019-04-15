from asyncio import events
import tormysql

# Allow for nested asyncio to stop "RuntimeError: This event loop is already running"
import nest_asyncio
nest_asyncio.apply()

class Database():

    def __init__(self, host="127.0.0.1", user="root", passwd="", db="mud"):
        self.pool = tormysql.ConnectionPool(
            max_connections=20,  # max open connections
            idle_seconds=7200,  # connection idle timeout time, 0 is not timeout
            wait_connection_timeout=3,  # wait connection timeout
            host=host,
            user=user,
            passwd=passwd,
            db=db,
            charset="utf8"
        )

    def Commit(self, sql, args, callback = None):
        events.get_event_loop().run_until_complete(self._Commit(sql, args, callback))

    async def _Commit(self, sql, args, callback = None):
        success = True
        async with await self.pool.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql, args)
            except:
                print("MySQL error: ...")
                success = False
                await conn.rollback()
            else:
                await conn.commit()

        if callback is not None:
            callback(success)

    def Fetch(self, sql, callback = None):
        events.get_event_loop().run_until_complete(self._Fetch(sql, callback))

    async def _Fetch(self, sql, callback = None):
        async with await self.pool.Connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql)
                data = cursor.fetchall()

        if callback is not None:
            callback(data)

    def Stop(self):
        self.pool.close()