from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Optional

from ...const import AirBaseActionKind
from .airbase_equipment import DeckBuilderAirBaseEquipmentList


class DeckBuilderAirBase(BaseModel):
    name: str = Field(alias="name")
    equipment: DeckBuilderAirBaseEquipmentList = Field(alias="items")
    mode: AirBaseActionKind = Field(alias="mode")
    distance: int = Field("distance")
    strikePoint: Optional[list[int]] = Field(alias="sp", default=None)
