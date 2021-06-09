from . import MemberController, BossController, RecordController, TeamController
from sqlalchemy.ext.asyncio import create_async_engine

from . import model

mc: MemberController.MemberController
bc: BossController.BossController
rc: RecordController.RecordController
tc: TeamController.TeamController


def init_database(db_path: str):
    global mc, bc, rc, tc
    mc = MemberController.MemberController(db_path)
    bc = BossController.BossController(db_path)
    rc = RecordController.RecordController(db_path)
    tc = TeamController.TeamController(db_path)


async def reset_database(db_path: str):
    aioengine = create_async_engine('sqlite+aiosqlite:///' + db_path)

    async with aioengine.begin() as conn:
        await conn.run_sync(model.Base.metadata.drop_all)
        await conn.run_sync(model.Base.metadata.create_all)
