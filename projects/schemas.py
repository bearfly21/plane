from pydantic import BaseModel

class ProjectSchema(BaseModel):
    name:str


from typing import Optional

class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = None



from pydantic import BaseModel
from typing import List
from teams.schemas import TeamOutSchema  
from users.shcemas import UserOutSchema  

class ProjectOut(BaseModel):
    id: int
    name: str
    owner: UserOutSchema
    teams: List[TeamOutSchema]
        
    class Config:
        from_attributes = True

