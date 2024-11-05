from pydantic import BaseModel
from typing import Union


class GetaroundModel(BaseModel):
    mileage: Union[int, float]
    engine_power: Union[int, float]
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool
    model_key: str
    fuel: str
    paint_color: str
    car_type: str
