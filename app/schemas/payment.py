from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel



class CheckoutSessionRequest(BaseModel):

    order_id: int

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )


class CheckoutSessionResponse(BaseModel):

    checkout_url: str
    session_id: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )
