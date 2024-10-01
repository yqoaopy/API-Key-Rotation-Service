from pydantic import BaseModel
from typing import Literal


# POST /api-key :request body 
class APIKeyRequest(BaseModel):
    type: Literal["service_1", "service_2", "service_3"]
