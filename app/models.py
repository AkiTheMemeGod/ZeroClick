from pydantic import BaseModel
from typing import Optional

class AppModel(BaseModel):
    id: str
    name: str
    download_url: str
    silent_args: str
    file_type: str
    hash: Optional[str] = None
    category: Optional[str] = "Utilities"
    icon_url: Optional[str] = None
