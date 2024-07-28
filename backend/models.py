from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from pydantic.json_schema import SkipJsonSchema
from enum import Enum
from pydantic.json_schema import SkipJsonSchema

from typing import Any


# class Vector(BaseModel):
#     x: float
#     y: float

# class PortEnum(Enum):
#     INPUT = 1
#     OUTPUT = 2
#     LEFT = 3
#     RIGHT = 4
#     OTHER = 5




# class ObjectPointer(BaseModel):
#     obj_id: str = Field(..., description="id of existing object. Like box1, fiber2, circle1, etc.")
#     port: Literal["portInput", "portOutput", "portLeft", "portRight"]

# class FiberPointer(BaseModel):
#     fiber_id: str = Field(..., description="id of existing fiber object. Like fiber1, fiber2, etc.")
#     port: Literal["portInput", "portOutput"]


# portOutput of box1 connects to portInput of 
class Port(BaseModel):
    obj_id: str = Field(..., description="id of existing object . Like box1, fiber2, circle1, etc.")
    port: Literal["portInput", "portOutput", "portLeft", "portRight"]

class InterfaceFiber(BaseModel):
    t: Literal["InterfaceFiber"] = Field("InterfaceFiber")
    from_: Port
    to: Port

    model_config = ConfigDict(json_schema_extra={
        # 't': 'InterfaceFiber',
        'instructions': "either _from.obj_id or to.obj_id MUST be a Fiber object"})


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
    stroke: str = "gray"
    lineWidth: float = 0
    x: float
    y: float

    # model_config = ConfigDict(json_schema_extra={'t': 'Circle'})
    


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
    stroke: str = "gray"
    size: float = 50
    x: float
    y: float
    lineWidth: float = 0

    # model_config = ConfigDict(json_schema_extra={'t': 'Polygon'})


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
    stroke: str = "gray"
    x: float
    y: float
    lineWidth: float = 0

    # model_config = ConfigDict(json_schema_extra={'t': 'Rect'})

class SuperRect(SuperNode):
    names = ["rect", "square", "rectangle"]
    def __init__(self):
        pass
    def model(self):
        return [Rect]
    

# only used by frontend for dependency resolution
class FiberPort(BaseModel):
    donate_position: bool
    donate_light: bool

class Box(BaseModel):
    t: Literal["Box"] = "Box"
    id: str = Field(..., description="a unique id for the Box object. Like box1, box2, etc.")
    name: SkipJsonSchema[Literal["box", "object"]] = "box"
    width: float = 150
    height: float = 75
    x: float
    y: float
    fill: str = "gray"

    # hidden
    portInputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=True, donate_light=False)
    portOutputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=True, donate_light=True)

    model_config = ConfigDict(json_schema_extra={
        # 't': 'Box', 
        'available_ports': ["portInput", "portOutput"]})

    @classmethod
    def model_json_schema(cls, *args, **kwargs) -> dict[str, Any]:
        schema = super().model_json_schema(*args, **kwargs)

        schema.pop('title', None)
        for prop in schema.get('properties', {}).values():
            prop.pop('title', None)

        return schema

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
    name: SkipJsonSchema[Literal["fiber", "cable", "wire"]] = "fiber"
    id: str = Field(..., description="a unique id for the Fiber object. Like fiber1, fiber2, etc.")
    lineWidth: float = 10

    # hidden
    portInputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=False, donate_light=False)
    portOutputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=False, donate_light=True)

    model_config = ConfigDict(json_schema_extra={
        # 't': "Fiber", 
        # 'notes': "Fiber is an OBJECT. Fiber is NOT an edge-like or interface-like entity. ",
        'available_ports': ["portInput", "portOutput"]})

    @classmethod
    def model_json_schema(cls, *args, **kwargs) -> dict[str, Any]:
        schema = super().model_json_schema(*args, **kwargs)

        schema.pop('title', None)
        for prop in schema.get('properties', {}).values():
            prop.pop('title', None)

        return schema

class SuperFiber(SuperNode):
    names = ["fiber", "cable", "wire"]
    def __init__(self):
        pass
    def model(self):
        return [Fiber]
    def add_interface(self):
        return [InterfaceFiber]








    


