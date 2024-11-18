from typing import Annotated, Any

from pydantic import BaseModel, Field, StringConstraints


class Subrule(BaseModel):
    name: Annotated[
        str, StringConstraints(to_lower=True, strip_whitespace=True)
    ]
    params: dict[str, Any] = Field(default={})


class DiscountRule(BaseModel):
    discount_id: int
    size_rule: Subrule
    eligibility_rules: list[Subrule] | None = Field(default=None)
    size_correction_rule: Subrule | None = Field(default=None)
