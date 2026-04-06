from pydantic import BaseModel, Field

class BankStatementData(BaseModel):
    account_holder_name: str = Field(..., description="Account holder name")
    account_number: str = Field(..., description="Bank account number")
    statement_date: str = Field(..., description="Statement date (DD/MM/YYYY)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_holder_name": "SITI AISAH BINTI GHAZALI",
                "account_number": "51-1103355-2",
                "statement_date": "28/02/2026"
            }
        }
