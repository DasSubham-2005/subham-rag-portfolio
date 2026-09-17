from pydantic import BaseModel, ConfigDict
from typing import Optional

class LoginIn(BaseModel): username: str; password: str
class TokenOut(BaseModel): access_token: str; token_type: str = "bearer"
class ProfileIn(BaseModel):
    name: str = "Subham Das"; title: str = "AI/ML Engineer | Data Scientist | Data Analyst"; bio: str = ""
    photo_url: str = ""; resume_url: str = ""; email: str = ""; github_url: str = ""; linkedin_url: str = ""; location: str = ""
class SkillIn(BaseModel): name: str; category: str = "Tools"; icon_url: str = ""; sort_order: int = 0
class ProjectIn(BaseModel):
    name: str; short_description: str = ""; description: str = ""; tech_stack: str = ""; github_url: str = ""; live_url: str = ""; thumbnail_url: str = ""; video_url: str = ""; featured: bool = False; sort_order: int = 0
class ExperienceIn(BaseModel): role: str; company: str; duration: str = ""; description: str = ""; sort_order: int = 0
class EducationIn(BaseModel): degree: str; institution: str; duration: str = ""; details: str = ""
class CertificateIn(BaseModel): name: str; issuer: str = ""; issue_date: str = ""; credential_url: str = ""; file_url: str = ""

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
