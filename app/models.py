from pydantic import BaseModel, HttpUrl


class CreateIn(BaseModel):
    long_url: HttpUrl

class CreateOut(BaseModel):
    code: str
    short_url: str