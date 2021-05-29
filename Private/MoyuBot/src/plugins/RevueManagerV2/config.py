from pydantic import BaseSettings


class Config(BaseSettings):
    AUTHOR = 476121826
    ADMIN = [476121826, 1282403844]

    SHARED_DATA = 'Shared'
    PRIVATE_DATA = 'Private/MoyuBot/Data'

    card_directory = 'Card'
    card_info_directory = 'Values'
    card_skill_directory = 'Skill'
    card_art_directory = 'Art'

    company_directory = 'Company'
    company_record: str = 'ORMTest'

    default_revue_turn = 6

    separator: str = ','

    class Config:
        extra = 'ignore'
