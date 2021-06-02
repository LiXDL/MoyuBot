from . import MemberController, BossController, RecordController


async def start_up(db_path: str) -> tuple[MemberController, BossController, RecordController]:
    return MemberController.MemberController(db_path), \
           BossController.BossController(db_path), \
           RecordController.RecordController(db_path)
