from pydantic import BaseSettings


class Config(BaseSettings):
    card_info_storage: str = 'Data/Card'
    card_skill_storage: str = 'Data/Card/Skill'
    memoir_storage: str = 'Data/Memoir'
    other_storage: str = 'Data/Other'

    class Config:
        extra = 'ignore'
