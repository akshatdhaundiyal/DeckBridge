from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DECKDISPATCH_", case_sensitive=False)

    APP_NAME: str = "DeckDispatch"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Presentation Widescreen 16:9 Defaults (Inches)
    SLIDE_WIDTH_INCHES: float = 13.333
    SLIDE_HEIGHT_INCHES: float = 7.5

    # Image payload restrictions
    MAX_IMAGE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit


settings = Settings()
