from sqlalchemy import Column, Integer, String
from database import Base

class UrlMapping(Base):
    __tablename__ = 'url_mapping'
    id = Column(Integer, index=True, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    short_code = Column(String, unique=True, index=True)
    clicks = Column(Integer, default=0)