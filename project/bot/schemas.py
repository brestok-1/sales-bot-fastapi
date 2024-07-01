from pydantic import BaseModel


class UserFilterQuerySchema(BaseModel):
    history: list
    settings: dict


class ProspectProfile(BaseModel):
    profileAge: str
    profileGender: str
    profileIncomeBracket: str
    profileOccupation: str
    profileIndustry: str
    profileLocation: str
    profileEducationLevel: str
    profileFamilySize: str
    profileHomeOwnership: str
    profileInterests: str


class ChatSettings(BaseModel):
    prospect_profile: ProspectProfile | None = None
    goal: str | None
    reason: str | None
    productDetail: str | None
    companyDescription: str | None
