from pydantic import BaseSettings


class Config(BaseSettings):
    card_info_storage: str = 'Data/Card'
    card_skill_storage: str = 'Data/Card/Skill'
    memoir_storage: str = 'Data/Memoir'
    other_storage: str = 'Data/Other'

    company_storage: str = 'Data/Company'

    max_card_number: int = 30

    class Config:
        extra = 'ignore'
