from pydantic import BaseModel
from typing import Literal


class Vector(BaseModel):
    x: float
    y: float

class Circle(BaseModel):
    t: Literal["Circle"] = "Circle"
    name: Literal["circle", "oval", "ellipse", "ball", "ellipsoid", "sphere"] = "circle"
    size: float = 50
    fill: str = "gray"
    position: Vector = Vector(x=0, y=0)
    lineWidth: float | None = None


class Polygon(BaseModel):
    t: Literal["Polygon"] = "Polygon"
    name: Literal["polygon", "triangle", "pentagon", "hexagon", "octagon"] = "polygon"
    sides: int = 5
    fill: str = "gray"
    size: float = 50
    position: Vector = Vector(x=0, y=0)
    lineWidth: float | None = None


class Rect(BaseModel):
    t: Literal["Rect"] = "Rect"
    name: Literal["rect", "square", "rectangle", "box"] = "rect"
    width: float = 50
    height: float = 50
    fill: str = "gray"
    position: Vector = Vector(x=0, y=0)
    lineWidth: float | None = None
