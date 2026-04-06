from pydantic import BaseModel, Field


class PayslipData(BaseModel):
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Employee full name"
    )
    
    id_number: str = Field(
        ...,
        pattern=r"^\d{6}-\d{2}-\d{4}$",
        description="National ID number (XXXXXX-XX-XXXX)"
    )
    
    gross_income: str = Field(
        ...,
        description="Gross income amount"
    )
    
    net_income: str = Field(
        ...,
        description="Net income after deductions"
    )
    
    total_deduction: str = Field(
        ...,
        description="Total deductions from gross income"
    )
    
    month_year: str = Field(
        ...,
        pattern=r"^\d{2}/\d{4}$",
        description="Pay period (MM/YYYY)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "SITI HAZIRAH BT MUSTAFA",
                "id_number": "800408-06-5592",
                "gross_income": "15898.00",
                "net_income": "9888.20",
                "total_deduction": "6009.80",
                "month_year": "02/2026"
            }
        }
