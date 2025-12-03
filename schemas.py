from pydantic import BaseModel, ConfigDict, HttpUrl

class Url(BaseModel):
    url: HttpUrl


class MappingsPrint(BaseModel):
    id: int
    url: str
    short_code: str
    short_url: str
    clicks: int

    model_config = ConfigDict(from_attributes=True)

class MappingsPrintDetail(MappingsPrint):
    detail: str