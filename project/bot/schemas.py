from pydantic import BaseModel


class UserFilterQuerySchema(BaseModel):
    history: list
    settings: dict


class ProspectProfile(BaseModel):
    profileAge: str | None = None
    profileGender: str | None = None
    profileIncomeBracket: str | None = None
    profileOccupation: str | None = None
    profileIndustry: str | None = None
    profileCompany: str | None = None
    profileLocation: str | None = None
    profileInterests: str | None = None
    profileGoals: str | None = None
    profileAdditionalInformation: str | None = None


class ChatSettings(BaseModel):
    prospect_profile: ProspectProfile | None = None
    goal: str | None = None
    reason: str | None = None
    productDetail: str | None = None
    companyDescription: str | None = None
