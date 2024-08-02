from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from pydantic.json_schema import SkipJsonSchema
from enum import Enum
from pydantic.json_schema import SkipJsonSchema

from typing import Any

from pydantic_core import CoreSchema


class PModel(BaseModel):

    # pass
    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        __core_schema: CoreSchema,
        __handler):
        schema = super().__get_pydantic_json_schema__(__core_schema, __handler)
        def remove_titles(d: dict):
            d.pop('title', None)
            for value in d.values():
                if isinstance(value, dict):
                    remove_titles(value)

        schema.pop('title', None)
        for prop in schema.get('properties', {}).values():
            remove_titles(prop)

        return schema


config_setter = False


# portOutput of box1 connects to portInput of 
class Port(PModel):
    obj_id: str = Field(..., description="id of existing object . Like box1, fiber2, circle1, etc.")
    # super weird error that appeared over night: I can't use a 
    # Literal["portInput", "portOutput"] here. It throws an error with openai specifically
    port: str = Field(..., description="portInput, portOutput, ...")


class Surface(PModel):
    obj_id: str = Field(..., description="id of existing object . Like box1, fiber2, circle1, etc.")
    surface: str = Field(..., description="surfaceTop, surfaceBottom, surfaceLeft, surfaceRight, ...")
    
    # Literal["portInput", "portOutput"] = "portInput"

    

    # @classmethod
    # def __get_pydantic_json_schema__(
    #     cls,
    #     __core_schema: CoreSchema,
    #     __handler):
    #     schema = super().__get_pydantic_json_schema__(__core_schema, __handler)
    #     def remove_titles(d: dict):
    #         d.pop('title', None)
    #         for value in d.values():
    #             if isinstance(value, dict):
    #                 remove_titles(value)

    #     schema.pop('title', None)
    #     for prop in schema.get('properties', {}).values():
    #         remove_titles(prop)

    #     return schema

class InterfaceFiber(PModel):
    t: Literal["InterfaceFiber"] #= Field("InterfaceFiber")
    from_: Port
    to: Port


class InterfacePosition(PModel):
    t: Literal["InterfacePosition"] = "InterfacePosition"
    from_: Surface
    to: Surface

class InterfaceCable(PModel):
    t: Literal["InterfaceCable"] = "InterfaceCable"
    from_: Port
    to: Port

    # # if config_setter:
    # model_config = ConfigDict(json_schema_extra={
    #     # 't': 'InterfaceFiber',
    #     'instructions': "either _from.obj_id or to.obj_id MUST be a Fiber object. Use the available Fiber object."})
    

class SuperNode:
    names: list[str] = []
    def __init__(self):
        pass
    def model(self) -> list[type[BaseModel]]:
        return []
    def add_interface(self) -> list[type[BaseModel]]:
        # if one object requires an interface of a particular type, then should a check be added to make sure there's something to connect to it?
        return []


class Location(PModel):
    x: float
    y: float

class Circle(PModel):
    t: Literal["Circle"] = "Circle"
    name: Literal["circle", "oval", "ellipse", "ball", "ellipsoid", "sphere"] = "circle"
    id: str = Field(..., description="a unique id for the circle. Like circle1, circle2, etc.")
    size: float = 50
    fill: str = "gray"
    stroke: str = Field("gray", description="color of stroke, edge, or border")
    lineWidth: float = Field(0, description="width of stroke, edge, or border. 0 means no border")
    x: float
    y: float

    # model_config = ConfigDict(json_schema_extra={'t': 'Circle'})
    


class SuperCircle(SuperNode):
    names = ["circle", "oval", "ellipse", "ball", "ellipsoid", "sphere"]
    def __init__(self):
        pass
    def model(self):
        return [Circle]


class Polygon(PModel):
    t: Literal["Polygon"] = "Polygon"
    name: Literal["polygon", "triangle", "pentagon", "hexagon", "octagon", "nonagon", "decagon", "dodecagon"] = "polygon"
    sides: int = Field(..., description="number of polygon sides. 3 is triangle, 5 is pentagon, etc.")
    id: str = Field(..., description="a unique id for the Polygon. Like poly1, poly2, etc.")
    fill: str = "gray"
    stroke: str = Field("gray", description="color of stroke, edge, or border")
    size: float = 50
    x: float
    y: float
    lineWidth: float = Field(0, description="width of stroke, edge, or border")


    # model_config = ConfigDict(json_schema_extra={'t': 'Polygon'})


class SuperPolygon(SuperNode):
    names =  ["polygon", "triangle", "pentagon", "hexagon", "octagon", "nonagon", "decagon", "dodecagon"]
    def __init__(self):
        pass
    def model(self):
        return [Polygon]


class Rect(PModel):
    t: Literal["Rect"] = "Rect"
    name: Literal["rect", "square", "rectangle"] = "rect"
    id: str = Field(..., description="a unique id for the Rect. Like rect1, rect2, etc.")
    width: float = 50
    height: float = 50
    fill: str = "gray"
    stroke: str = Field("gray", description="color of stroke, edge, or border")
    x: float
    y: float
    lineWidth: float = Field(0, description="width of stroke, edge, or border")


    # model_config = ConfigDict(json_schema_extra={'t': 'Rect'})

class SuperRect(SuperNode):
    names = ["rect", "square", "rectangle"]
    def __init__(self):
        pass
    def model(self):
        return [Rect]
    

# only used by frontend for dependency resolution
class FiberPort(PModel):
    donate_position: bool
    donate_light: bool

class SurfacePort(PModel):
    donate_position: bool


class Box(PModel):
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

    if config_setter:
        model_config = ConfigDict(json_schema_extra={
            # 't': 'Box', 
            'available_ports': ["portInput", "portOutput"]})
    if not config_setter:
        available_ports: Literal["portInput, portOutput"] = "portInput, portOutput"


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
    
class Fiber(PModel):
    t: Literal["Fiber"] = "Fiber"
    name: SkipJsonSchema[Literal["fiber", "fiber optic", "optical fiber"]] = "fiber"
    id: str = Field(..., description="a unique id for the Fiber object. Like fiber1, fiber2, etc.")
    lineWidth: float = 2

    # hidden
    portInputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=False, donate_light=False)
    portOutputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=False, donate_light=True)

    if config_setter:
        model_config = ConfigDict(json_schema_extra={
            # 't': "Fiber", 
            # 'notes': "Fiber is an OBJECT. Fiber is NOT an edge-like or interface-like entity. ",
            'available_ports': ["portInput", "portOutput"]})
    if not config_setter:
        available_ports: Literal["portInput, portOutput"] = "portInput, portOutput"


class SuperFiber(SuperNode):
    names = ["fiber", "fiber optic", "optical fiber"]
    def __init__(self):
        pass
    def model(self):
        return [Fiber]
    def add_interface(self):
        return [InterfaceFiber]
    

class Cable(PModel):
    t: Literal["Cable"] = "Cable"
    name: SkipJsonSchema[Literal["cable", "wire"]] = "cable"
    id: str = Field(..., description="a unique id for the Cable object. Like cable1, cable2, etc.")
    lineWidth: float = 2

    # hidden
    portInputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=False, donate_light=False)
    portOutputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=False, donate_light=True)

    if config_setter:
        model_config = ConfigDict(json_schema_extra={
            # 't': "Fiber", 
            # 'notes': "Fiber is an OBJECT. Fiber is NOT an edge-like or interface-like entity. ",
            'available_ports': ["portInput", "portOutput"]})
    if not config_setter:
        available_ports: Literal["portInput, portOutput"] = "portInput, portOutput"


class SuperCable(SuperNode):
    names = ["cable", "wire", "cord"]
    def __init__(self):
        pass
    def model(self):
        return [Cable]
    def add_interface(self):
        return [InterfaceCable]
    

class Podium(PModel):
    t: Literal["Podium"] = "Podium"
    name: SkipJsonSchema[Literal["podium", "stage", "platform"]] = "podium"
    id: str = Field(..., description="a unique id for the Podium object. Like podium1, podium2, etc.")
    width: float = 150
    x: float
    y: float

    # hidden
    surfaceType: SkipJsonSchema[SurfacePort] = SurfacePort(donate_position=True)


    if config_setter:
        model_config = ConfigDict(json_schema_extra={
            # 't': 'Podium', 
            'available_ports': ["surfaceTop"]})
    if not config_setter:
        available_ports: Literal["surfaceTop"] = "surfaceTop"


class SuperPodium(SuperNode):
    names = ["podium", "stage", "platform"]
    def __init__(self):
        pass
    def model(self):
        return [Podium]
    def add_interface(self):
        return [InterfacePosition]
    



class Laptop(PModel):
    t: Literal["Laptop"] = "Laptop"
    name: SkipJsonSchema[Literal["laptop", "computer", "notebook"]] = "laptop"
    id: str = Field(..., description="a unique id for the Laptop object. Like laptop1, laptop2, etc.")
    width: float = 150
    x: float
    y: float

    # hidden
    surfaceType: SkipJsonSchema[SurfacePort] = SurfacePort(donate_position=False)

    if config_setter:
        model_config = ConfigDict(json_schema_extra={
            # 't': 'Laptop', 
            'available_ports': ["surfaceBottom"]})
    if not config_setter:
        available_ports: Literal["surfaceBottom"] = "surfaceBottom"


class SuperLaptop(SuperNode):
    names = ["laptop", "computer", "notebook"]
    def __init__(self):
        pass
    def model(self):
        return [Laptop]
    def add_interface(self):
        return [InterfacePosition]
    


class SuperLaser(SuperNode):
    names = ["laser", "diode laser", "laser diode"]
    def __init__(self):
        pass
    def model(self):
        return [Laser]
    def add_interface(self):
        return [InterfaceFiber]
    
class Laser(PModel):
    t: Literal["Laser"] = "Laser"
    name: SkipJsonSchema[Literal["laser", "diode laser", "laser diode"]] = "laser"
    x: float
    y: float
    width: float = 145
    id: str = Field(..., description="a unique id. Like laser1, laser2, etc.")
    on: bool = False

    portOutputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=True, donate_light=True)

    if config_setter:
        model_config = ConfigDict(json_schema_extra={
            'available_ports': ["portOutput"]})
    if not config_setter:
        available_ports: Literal["portOutput"] = "portOutput"



class SuperSwitch(SuperNode):
    names = ["switch", "toggle", "modulator"]
    def __init__(self):
        pass
    def model(self):
        return [Switch, Fiber]
    def add_interface(self):
        return [InterfaceFiber]


class Switch(PModel):
    t: Literal["Switch"] = "Switch"
    id: str = Field(..., description="a unique id for the Switch object. Like switch1, switch2, etc.")
    name: SkipJsonSchema[Literal["switch", "controller", "toggle"]] = "switch"
    width: float = 120
    x: float
    y: float
    open: bool = Field(False, description="if switch is internally open or closed. Has no impact on connected ports")

    # hidden
    portInputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=True, donate_light=False)
    portOutputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=True, donate_light=True)

    if config_setter:
        model_config = ConfigDict(json_schema_extra={
            # 't': 'Box', 
            'available_ports': ["portInput", "portOutput"]})
    if not config_setter:
        available_ports: Literal["portInput, portOutput"] = "portInput, portOutput"


    @classmethod
    def model_json_schema(cls, *args, **kwargs) -> dict[str, Any]:
        schema = super().model_json_schema(*args, **kwargs)

        schema.pop('title', None)
        for prop in schema.get('properties', {}).values():
            prop.pop('title', None)

        return schema
    

class SuperDetector(SuperNode):
    names = ["detector", "photodetector", "photodiode"]
    def __init__(self):
        pass
    def model(self):
        return [Detector, Fiber]
    def add_interface(self):
        return [InterfaceFiber]


class Detector(PModel):
    t: Literal["Detector"] = "Detector"
    id: str = Field(..., description="a unique id for the Detector object. Like detector1, detector2, etc.")
    name: SkipJsonSchema[Literal["detector", "photodetector", "photodiode"]] = "detector"
    width: float = 110
    x: float
    y: float

    # hidden
    portInputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=True, donate_light=False)
    # portOutputType: SkipJsonSchema[FiberPort] = FiberPort(donate_position=True, donate_light=True)

    if config_setter:
        model_config = ConfigDict(json_schema_extra={
            # 't': 'Box', 
            'available_ports': ["portInput"]})
    if not config_setter:
        available_ports: Literal["portInput"] = "portInput"












    


