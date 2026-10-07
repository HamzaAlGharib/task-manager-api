from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        errors = []

        if not any(char.isupper() for char in password):
            errors.append("uppercase letter")

        if not any(char.islower() for char in password):
            errors.append("lowercase letter")

        if not any(char.isdigit() for char in password):
            errors.append("number")

        if not any(not char.isalnum() for char in password):
            errors.append("special character")

        if errors:
            raise ValueError("Password must contain at least one " + ", ".join(errors))

        return password

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
