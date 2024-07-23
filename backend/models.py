from pydantic import BaseModel, Field
from typing import Literal


# class Vector(BaseModel):
#     x: float
#     y: float


class InterfaceFiber(BaseModel):
    t: Literal["FiberInterface"] = "FiberInterface"
    name: Literal["fiber_interface"] = "fiber_interface"
    id: str = Field(..., description="a unique id for the interface. Like fiber_interface1, fiber_interface2, etc.")
    input_id: str = Field(..., description="the id of the node where the fiber starts")
    output_id: str = Field(..., description="the id of the node where the fiber ends")



class SuperNode:
    names: list[str] = []
    def __init__(self):
        pass
    def model(self) -> type[BaseModel] | None:
        return None
    def add_interface(self) -> type[BaseModel] | None:
        # if one object requires an interface of a particular type, then should a check be added to make sure there's something to connect to it?
        
        return None


class Location(BaseModel):
    x: float
    y: float

class Circle(BaseModel):
    t: Literal["Circle"] = "Circle"
    name: Literal["circle", "oval", "ellipse", "ball", "ellipsoid", "sphere"] = "circle"
    id: str = Field(..., description="a unique id for the circle. Like circle1, circle2, etc.")
    size: float = 50
    fill: str = "gray"
    x: float = Field(..., description="x location. 0 is center, positive is right (max: 480), negative is left (min: -480)")
    y: float = Field(..., description="y location. 0 is center, positive is up (max: 270), negative is down (min: -270)")
    lineWidth: float | None = None


class SuperCircle(SuperNode):
    names = ["circle", "oval", "ellipse", "ball", "ellipsoid", "sphere"]
    def __init__(self):
        pass
    def model(self) -> type[BaseModel] | None:
        return Circle


class Polygon(BaseModel):
    t: Literal["Polygon"] = "Polygon"
    name: Literal["polygon", "triangle", "pentagon", "hexagon", "octagon", "nonagon", "decagon", "dodecagon"] = "polygon"
    sides: int = Field(..., description="number of polygon sides. 3 is triangle, 5 is pentagon, etc.")
    id: str = Field(..., description="a unique id for the Polygon. Like poly1, poly2, etc.")
    fill: str = "gray"
    size: float = 50
    x: float = Field(..., description="x location. 0 is center, positive is right (max: 480), negative is left (min: -480)")
    y: float = Field(..., description="y location. 0 is center, positive is up (max: 270), negative is down (min: -270)")
    lineWidth: float | None = None


class SuperPolygon(SuperNode):
    names =  ["polygon", "triangle", "pentagon", "hexagon", "octagon", "nonagon", "decagon", "dodecagon"]
    def __init__(self):
        pass
    def model(self) -> type[BaseModel] | None:
        return Polygon


class Rect(BaseModel):
    t: Literal["Rect"] = "Rect"
    name: Literal["rect", "square", "rectangle"] = "rect"
    id: str = Field(..., description="a unique id for the Rect. Like rect1, rect2, etc.")
    width: float = 50
    height: float = 50
    fill: str = "gray"
    x: float = Field(..., description="x location. 0 is center, positive is right (max: 480), negative is left (min: -480)")
    y: float = Field(..., description="y location. 0 is center, positive is up (max: 270), negative is down (min: -270)")
    lineWidth: float | None = None

class SuperRect(SuperNode):
    names = ["rect", "square", "rectangle"]
    def __init__(self):
        pass
    def model(self):
        return Rect


class Box(BaseModel):
    t: Literal["Box"] = "Box"
    name: Literal["box", "object"] = "box"
    id: str = Field(..., description="a unique id for the Box. Like box1, box2, etc.")
    fiber_in_interface_id: str | None = Field(None, description="the id of this node's fiber input")
    fiber_out_interface_id: str | None = Field(None, description="the id of this node's fiber output")
    rect_props: Rect

class SuperBox(SuperNode):
    names = ["box", "object"]
    def __init__(self):
        pass
    def model(self):
        return Box
    def add_interface(self):
        return InterfaceFiber
    
class Fiber(BaseModel):
    t: Literal["Fiber"] = "Fiber"
    name: Literal["fiber", "cable", "wire"] = "fiber"
    id: str = Field(..., description="a unique id for the Fiber. Like fiber1, fiber2, etc.")
    start_id: str = Field(..., description="the id of this node's fiber input")
    end_id: str = Field(..., description="the id of this node's fiber output")
    lineWidth: float | None = None

class SuperFiber(SuperNode):
    names = ["fiber", "cable", "wire"]
    def __init__(self):
        pass
    def model(self):
        return Fiber
    def add_interface(self):
        return InterfaceFiber








    


