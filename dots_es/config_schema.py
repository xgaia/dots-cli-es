from pydantic import BaseModel, Field, field_validator


class SourceConfig(BaseModel):
    DTS_URL: str
    TARGET_COLLECTION: str = ""
    CUSTOM_SETTINGS_PATH: str = ""
    ADDITIONAL_EXCLUDED_COLLECTIONS: list[str] = Field(default_factory=list)

    @field_validator("ADDITIONAL_EXCLUDED_COLLECTIONS")
    @classmethod
    def lower_excluded(cls, v: list[str]) -> list[str]:
        return [c.lower() for c in v]


class SearchConfig(BaseModel):
    ELASTICSEARCH_URL: str
    DOCUMENT_INDEX: str
    COLLECTION_INDEX: str
    SEARCH_RESULT_PER_PAGE: int = 200
