"""
04 — Request Bodies: Advanced Custom Validators

Run:
  uvicorn examples.04_request_bodies.advanced_custom_validators:app --reload

Try in /docs:
  POST /register

Examples:
1. Invalid email domain
2. Underage user
3. Password contains username
4. Password confirmation mismatch
5. Country-specific phone validation
"""

# before: runs before the normal parsing/validation of the fields
# after: runs after the parsing/validation of the fields has already been done and the model instance has been created

from datetime import date
import re

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, field_validator, model_validator

app = FastAPI(title="Advanced Custom Validators")


class RegisterData(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str
    birth_date: date
    country: str
    phone: str

    @model_validator(mode="before")
    @classmethod
    def preprocess_input(cls, data):
        """
        Runs before field parsing/validation.
        Good for cleanup/normalization of raw incoming data.
        """
        if isinstance(data, dict):
            if "username" in data and isinstance(data["username"], str):
                data["username"] = data["username"].strip().lower()

            if "email" in data and isinstance(data["email"], str):
                data["email"] = data["email"].strip().lower()

            if "country" in data and isinstance(data["country"], str):
                data["country"] = data["country"].strip().upper()

            if "phone" in data and isinstance(data["phone"], str):
                # remove spaces, dashes, parentheses
                data["phone"] = re.sub(r"[()\s-]+", "", data["phone"])

        return data

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Single-field validation for username rules.
        """
        if len(v) < 4:
            raise ValueError("Username must be at least 4 characters long")

        if not re.fullmatch(r"[a-z0-9_]+", v):
            raise ValueError("Username may contain only lowercase letters, numbers, and underscores")

        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Single-field validation for password complexity.
        """
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must include at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must include at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must include at least one digit")

        if not re.search(r"[^\w\s]", v):
            raise ValueError("Password must include at least one special character")

        return v

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v: EmailStr) -> EmailStr:
        """
        Single-field validation with business-specific rule.
        """
        blocked_domains = {"tempmail.com", "mailinator.com", "fakeinbox.com"}
        domain = v.split("@")[1]

        if domain in blocked_domains:
            raise ValueError("Disposable email addresses are not allowed")

        return v

    @field_validator("phone")
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        """
        Generic phone validation before country-specific checks.
        """
        if not re.fullmatch(r"\+?\d{8,15}", v):
            raise ValueError("Phone must contain 8 to 15 digits, optionally starting with +")

        return v

    @model_validator(mode="after")
    def validate_cross_field_rules(self):
        """
        Cross-field validation after all fields are parsed.
        """
        # Password confirmation
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")

        # Password should not contain username
        if self.username in self.password.lower():
            raise ValueError("Password must not contain the username")

        # Age validation
        today = date.today()
        age = today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

        if age < 18:
            raise ValueError("User must be at least 18 years old")

        # Country-specific phone rules
        if self.country == "GR" and not self.phone.startswith("+30"):
            raise ValueError("Greek phone numbers must start with +30")

        if self.country == "US" and not self.phone.startswith("+1"):
            raise ValueError("US phone numbers must start with +1")

        return self


@app.post("/register")
def register(data: RegisterData):
    """
    Demonstrates advanced custom validation in Pydantic:
    - @model_validator(mode="before"): preprocess raw input
    - @field_validator: validate individual fields
    - @model_validator(mode="after"): validate relationships between fields
    """
    return {
        "ok": True,
        "username": data.username,
        "email": data.email,
        "country": data.country,
        "phone": data.phone,
    }