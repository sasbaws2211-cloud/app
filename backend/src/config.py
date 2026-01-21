from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
   DATABASE_URL:str
   SECRET_KEY:str
   ALGORITHM:str
   ACCESS_TOKEN_EXPIRE_MINUTES:str
   HUBTEL_API_ID:str
   HUBTEL_API_KEY:str
   HUBTEL_MERCHANT_ACCOUNT:str 
   ALLOWED_HOSTS: list

   model_config = SettingsConfigDict(
        
        env_file =".env",  
        extra ="ignore"    
    )


# Initialize the settings
Config = Settings()



