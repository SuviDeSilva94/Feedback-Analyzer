from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TokenPayload(BaseModel):
    """Model representing the JWT token payload."""
    sub: str = Field(..., description="Subject (user ID)")
    exp: datetime = Field(..., description="Expiration time")
    iat: Optional[datetime] = Field(None, description="Issued at time")
    nbf: Optional[datetime] = Field(None, description="Not before time")
    iss: Optional[str] = Field(None, description="Issuer")
    aud: Optional[str] = Field(None, description="Audience")
    jti: Optional[str] = Field(None, description="JWT ID")
    type: str = Field(..., description="Token type (e.g., 'access', 'refresh')")
    scope: Optional[str] = Field(None, description="Token scope") 