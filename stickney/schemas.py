from pydantic import BaseModel
from typing import  Optional
# ======================================================================
# Define validation schemas for API
# ======================================================================
    
class ReloadQuery(BaseModel):
    """
    When reloading a model we need a new config dictionary.
    For the moment, only the model id is supported
    """
    model_id: str
    
class ResponseUpdate(BaseModel):
    """
    When reloading a model we return a msg
    """
    message: str
    
class ConfigResponse(BaseModel):
    API_KEY: Optional[str] = None 
    API_INTERNAL_URL: Optional[str] = None
    MODEL_ID: str