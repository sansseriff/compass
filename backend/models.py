from pydantic import BaseModel, Field
from typing import Literal


# class Vector(BaseModel):
#     x: float
#     y: float

class Circle(BaseModel):
    t: Literal["Circle"] = "Circle"
    name: Literal["circle", "oval", "ellipse", "ball", "ellipsoid", "sphere"] = "circle"
    size: float = 50
    fill: str = "gray"
    x: float = Field(..., description="x location. 0 is center, positive is right (max: 480), negative is left (min: -480)")
    y: float = Field(..., description="y location. 0 is center, positive is up (max: 270), negative is down (min: -270)")
    lineWidth: float | None = None


class Polygon(BaseModel):
    t: Literal["Polygon"] = "Polygon"
    name: Literal["polygon", "triangle", "pentagon", "hexagon", "octagon"] = "polygon"
    sides: int = Field(..., description="number of polygon sides. 3 is triangle, 5 is pentagon, etc.")
    fill: str = "gray"
    size: float = 50
    x: float = Field(..., description="x location. 0 is center, positive is right (max: 480), negative is left (min: -480)")
    y: float = Field(..., description="y location. 0 is center, positive is up (max: 270), negative is down (min: -270)")
    lineWidth: float | None = None


class Rect(BaseModel):
    t: Literal["Rect"] = "Rect"
    name: Literal["rect", "square", "rectangle", "box"] = "rect"
    width: float = 50
    height: float = 50
    fill: str = "gray"
    x: float = Field(..., description="x location. 0 is center, positive is right (max: 480), negative is left (min: -480)")
    y: float = Field(..., description="y location. 0 is center, positive is up (max: 270), negative is down (min: -270)")
    lineWidth: float | None = None


# y: float = Field(..., description="y location. 0 is center, -270 is top, 270 is bottom")