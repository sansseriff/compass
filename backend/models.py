from pydantic import BaseModel, Field
from typing import Literal
from pydantic.json_schema import SkipJsonSchema
from enum import Enum


# class Vector(BaseModel):
#     x: float
#     y: float

class PortEnum(str, Enum):
    input = "portInput"
    output = "portOutput"
    left = "portLeft"
    right = "portRight"




class C(BaseModel):
    obj_id: str = Field(..., description="id of existing object. Like box1, fiber2, circle1, etc.")
    port: PortEnum = Field(..., description="match name of port on object.")


class InterfaceFiber(BaseModel):
    t: Literal["InterfaceFiber"] = "InterfaceFiber"
    input: C
    output: C


class SuperNode:
    names: list[str] = []
    def __init__(self):
        pass
    def model(self) -> list[type[BaseModel]]:
        return []
    def add_interface(self) -> list[type[BaseModel]]:
        # if one object requires an interface of a particular type, then should a check be added to make sure there's something to connect to it?
        return []


class Location(BaseModel):
    x: float
    y: float

class Circle(BaseModel):
    t: Literal["Circle"] = "Circle"
    name: Literal["circle", "oval", "ellipse", "ball", "ellipsoid", "sphere"] = "circle"
    id: str = Field(..., description="a unique id for the circle. Like circle1, circle2, etc.")
    size: float = 50
    fill: str = "gray"
    x: float
    y: float
    lineWidth: float | None = None


class SuperCircle(SuperNode):
    names = ["circle", "oval", "ellipse", "ball", "ellipsoid", "sphere"]
    def __init__(self):
        pass
    def model(self):
        return [Circle]


class Polygon(BaseModel):
    t: Literal["Polygon"] = "Polygon"
    name: Literal["polygon", "triangle", "pentagon", "hexagon", "octagon", "nonagon", "decagon", "dodecagon"] = "polygon"
    sides: int = Field(..., description="number of polygon sides. 3 is triangle, 5 is pentagon, etc.")
    id: str = Field(..., description="a unique id for the Polygon. Like poly1, poly2, etc.")
    fill: str = "gray"
    size: float = 50
    x: float
    y: float
    lineWidth: float | None = None


class SuperPolygon(SuperNode):
    names =  ["polygon", "triangle", "pentagon", "hexagon", "octagon", "nonagon", "decagon", "dodecagon"]
    def __init__(self):
        pass
    def model(self):
        return [Polygon]


class Rect(BaseModel):
    t: Literal["Rect"] = "Rect"
    name: Literal["rect", "square", "rectangle"] = "rect"
    id: str = Field(..., description="a unique id for the Rect. Like rect1, rect2, etc.")
    width: float = 50
    height: float = 50
    fill: str = "gray"
    x: float
    y: float
    lineWidth: float | None = None

class SuperRect(SuperNode):
    names = ["rect", "square", "rectangle"]
    def __init__(self):
        pass
    def model(self):
        return [Rect]


class Box(BaseModel):
    t: Literal["Box"] = "Box"
    id: str = Field(..., description="a unique id for the Box object. Like box1, box2, etc.")
    name: Literal["box", "object"] = "box"
    portInput: Literal["portInput"] = "portInput"
    portOutput: Literal["portOutput"] = "portOutput"
    width: float = 50
    height: float = 50
    x: float
    y: float
    fill: str = "gray"

class SuperBox(SuperNode):
    names = ["box", "object"]
    def __init__(self):
        pass
    def model(self):
        return [Box, Fiber]
    def add_interface(self):
        return [InterfaceFiber]
    
class Fiber(BaseModel):
    t: Literal["Fiber"] = "Fiber"
    name: Literal["fiber", "cable", "wire"] = "fiber"
    id: str = Field(..., description="a unique id for the Fiber object. Like fiber1, fiber2, etc.")
    portInput: Literal["portInput"] = "portInput"
    portOutput: Literal["portOutput"] = "portOutput"
    lineWidth: float | None = None

class SuperFiber(SuperNode):
    names = ["fiber", "cable", "wire"]
    def __init__(self):
        pass
    def model(self):
        return [Fiber]
    def add_interface(self):
        return [InterfaceFiber]








    


