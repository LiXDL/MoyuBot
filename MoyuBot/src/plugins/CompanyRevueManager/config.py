from pydantic import BaseSettings


class Config(BaseSettings):
    AUTHOR = 476121826
    ADMIN = [476121826, 1282403844]

    card_info_storage: str = 'Data/Card'
    card_skill_storage: str = 'Data/Card/Skill'
    memoir_storage: str = 'Data/Memoir'
    other_storage: str = 'Data/Other'

    company_storage: str = 'Data/Company'
    company_record: str = 'Test'

    default_revue_turn = 6

    separator: str = ','

    class Config:
        extra = 'ignore'
