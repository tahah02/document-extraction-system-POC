from pydantic import BaseModel, Field
from typing import Optional

class PayslipData(BaseModel):
    name: str = Field(..., description="Employee name")
    id_number: str = Field(..., description="National ID number")
    gross_income: str = Field(..., description="Gross income")
    net_income: str = Field(..., description="Net income")
    total_deduction: str = Field(..., description="Total deductions")
    month_year: str = Field(..., description="Pay period (MM/YYYY)")
    
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
