from pydantic import BaseModel, Field


class BankStatementData(BaseModel):
    
    account_holder_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of account holder"
    )
    
    account_number: str = Field(
        ...,
        pattern=r"^\d{2}-\d{7}-\d$",
        description="Bank account number (XX-XXXXXXX-X)"
    )
    
    statement_date: str = Field(
        ...,
        pattern=r"^\d{2}/\d{2}/\d{4}$",
        description="Statement date (DD/MM/YYYY)"
    )
    
    opening_balance: str = Field(
        ...,
        description="Opening balance amount"
    )
    
    closing_balance: str = Field(
        ...,
        description="Closing balance amount"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_holder_name": "SITI AISAH BINTI GHAZALI",
                "account_number": "51-1103355-2",
                "statement_date": "28/02/2026",
                "opening_balance": "550.00",
                "closing_balance": "348.77"
            }
        }
