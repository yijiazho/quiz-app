from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class ParsedContentResponse(BaseModel):
    file_id: str
    filename: str
    title: str
    content: str
    sections: List[Dict[str, str]]
    metadata: Dict[str, str]
    parsed_at: datetime

    class Config:
        from_attributes = True 