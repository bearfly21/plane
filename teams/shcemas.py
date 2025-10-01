from pydantic import BaseModel

class TeamCreateSchema(BaseModel):
    name:str
    