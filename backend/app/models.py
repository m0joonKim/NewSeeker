import uuid
from typing import Optional, List
from datetime import datetime, time
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import ConfigDict, EmailStr
from sqlalchemy import TEXT
from enum import Enum
from sqlmodel import Field, Relationship, SQLModel, Session
from sqlalchemy.sql import select

ktc = ZoneInfo("Asia/Seoul")
# Shared properties



#===============================================================
class ProviderEnum(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"
    KAKAO = "kakao"

class UserBase(SQLModel):
    email: EmailStr | None = Field(unique=True, index=True, max_length=100)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=100)
    provider: ProviderEnum = Field(default=ProviderEnum.LOCAL)
    provider_id: str | None = Field(default=None, max_length=100)
    profile_image: str | None = Field(default=None, max_length=200)

# Database model, database table inferred from class name
class User(UserBase, table=True):#USERBASE 상속
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str | None = Field(default=None, max_length=128)
    createAt: datetime = Field(default_factory=lambda: datetime.now(ktc))
    updateAt: datetime = Field(default_factory=lambda: datetime.now(ktc))
    alarm: list["Alarm"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})

class FrequencyEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NONE = None

class DayOfWeekEnum(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"


class Alarm(SQLModel, table=True):
    # model_config = ConfigDict(arbitrary_types_allowed=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id",unique=True)
    frequency: Optional[FrequencyEnum] = Field(default=FrequencyEnum.NONE)
    day_of_week: Optional[DayOfWeekEnum] = Field(default=DayOfWeekEnum.MONDAY)
    day_of_month: Optional[int] = None
    receive_time: Optional[time] = None
    email_on: bool = Field(default=False)
    kakao_on: bool = Field(default=False)
    slack_on: bool = Field(default=False)
    user: User = Relationship(back_populates="alarm")


class NewsPaperType(str, Enum):
    NEWS = "news"
    PAPER = "paper"

class Newspaper(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=150)
    summary: str = Field(max_length=300)
    contents: str = Field(sa_column=TEXT)
    date: datetime
    author: str = Field(max_length=100)
    source: str = Field(max_length=100)
    link: str = Field(max_length=200)
    hits: int = Field(default=0)
    type: NewsPaperType


class CategoryEnum(str, Enum):
    AI_ML = "ai_ml"
    DATA_SCIENCE = "data_science"
    CYBERSECURITY = "cybersecurity"
    CLOUD_COMPUTING = "cloud_computing"
    DEVOPS = "devops"
    BLOCKCHAIN = "blockchain"
    IOT = "iot"
    EDGE_COMPUTING = "edge_computing"
    VR_AR_METAVERSE = "vr_ar_metaverse"
    QUANTUM_COMPUTING = "quantum_computing"
    PROGRAMMING_LANGUAGES = "programming_languages"
    SOFTWARE_ARCHITECTURE = "software_architecture"
    DEVELOPER_TOOLS = "developer_tools"
    BIG_DATA = "big_data"
    OPEN_SOURCE = "open_source"
    UX_UI = "ux_ui"
    MOBILE_WEB_DEVELOPMENT = "mobile_web_development"
    NETWORKING = "networking"
    ROBOTICS = "robotics"
    FINTECH = "fintech"
    ETC = "etc"
    #프로젝트 구체화 후 수정 필요


class Category(SQLModel, table=True):
    # model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int = Field(default=None, primary_key=True)
    name: CategoryEnum
    # name: int


class UserCategory(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True)
    selected_at: datetime = Field(default_factory=lambda: datetime.now(ktc))


class NewspaperCategory(SQLModel, table=True):
    newspaper_id: int = Field(foreign_key="newspaper.id", primary_key=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True)



class UserNewspaperSave(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    newspaper_id: int = Field(primary_key=True)
    save_at: datetime = Field(default_factory=lambda: datetime.now(ktc))
    title: str = Field(max_length=150)
    summary: str = Field(max_length=300)
    link: str = Field(max_length=200)
    


class PreferenceEnum(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    NONE = "none"

class UserNewspaperPreference(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    newspaper_id: int = Field(foreign_key="newspaper.id", primary_key=True)
    preference: PreferenceEnum
    update_at: datetime = Field(default_factory=lambda: datetime.now(ktc))





#=============================schema==================================
# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)





# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int



# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)




# Function to populate Category table with all CategoryEnum values
def populate_categories(session: Session):
    for category in CategoryEnum:
        existing_category = session.exec(select(Category).where(Category.name == category.value)).first()
        if not existing_category:
            new_category = Category(name=category.value)  # Store as string
            session.add(new_category)
    session.commit()

