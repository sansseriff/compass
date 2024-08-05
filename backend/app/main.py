import uvicorn
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from typing import Unpack


from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat import ChatCompletion


from typing_extensions import Annotated
from typing import Literal, Union, Type

from pydantic import Field

from app.server_logging import get_logger
logger = get_logger(__name__)

from pydantic import BaseModel, create_model


from openai import OpenAI

from anthropic import Anthropic
import instructor

from instructor import Instructor

from dotenv import load_dotenv  # Import load_dotenv
# Load environment variables from .env file
import openai
from groq import Groq

from app.models import Circle, Polygon, Rect

from app.models import SuperNode
from typing import cast
from typing import Any

import importlib
import inspect
from typing import get_type_hints, Literal, get_origin

import json
from dataclasses import dataclass


from fastapi.middleware.cors import CORSMiddleware


@dataclass
class DecoderModel:
    client: Instructor
    model: str

@dataclass
class SceneModel:
    client: Instructor
    model: str





load_dotenv()

app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://localhost:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



client_groq = instructor.from_groq(Groq(), mode=instructor.Mode.TOOLS)
client_openai = instructor.from_openai(OpenAI())
client_anthropic = instructor.from_anthropic(Anthropic())


decoder_model = DecoderModel(client=client_groq, model="llama3-groq-70b-8192-tool-use-preview")
scene_model = SceneModel(client=client_openai, model="gpt-4o-mini")


class SearchTerms(BaseModel):
    search_terms: list[str]


# class Scene(BaseModel):
#     scene: list[BaseModel]

class Message(BaseModel):
    message: str

    # Examples:
    # INPUT: A triangle sits on top of a long and thing blue rectangle. Hovering above the triangle is a small red circle.
    # OUTPUT: "triangle", "long blue rectangle", "rectangle", "small red circle", "circle"

    # INPUT: "Below a square is a large green circle. To the right of the circle is a small yellow triangle."
    # OUTPUT: "square", "large green circle", "circle", "small yellow triangle", "triangle"

@app.post("/scene")
def text_to_search(msg: Message):

    text = msg.message
    prompt = f""" pull terms from the following text for building a knowledge graph. Break into 1-3 word terms.: '{text}'"""
    logger.info("starting openai call: %s", prompt)

    completion = SearchTerms(search_terms=[])

    try:
        print("USING DECODER MODEL: ", decoder_model.model)
        completion: SearchTerms = decoder_model.client.chat.completions.create(
            model=decoder_model.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_model=SearchTerms,
        )

    except openai.RateLimitError as e:
        # request limit exceeded or something.
        logger.warning("%s", e)

    except Exception as e:
        # general exception handling
        
        logger.error("ERROR! %s", e)
        return None

    # words = msg.message.split(" ")
    # completion = SearchTerms(search_terms=words)

    models, interfaces = search_search(completion)
    return matches_to_scene(models, interfaces, text)

        


def search_search(s: SearchTerms):
    models_module = importlib.import_module("app.models")
    print("search terms: ", s.search_terms)
    matched_objects: list[type[BaseModel]] = []
    matched_interfaces: list[type[BaseModel]] = []

    # Convert search terms and synonyms to lowercase for case-insensitive comparison
    search_terms_lower = [term.lower() for term in s.search_terms]

    print("starting search terms: ", search_terms_lower)
    for term in s.search_terms:
        term_lower = term.lower()
        search_terms_lower.append(term_lower)
        # Split the term by spaces and add the last word if it's not the only word
        words = term.split()
        if len(words) > 1:
            search_terms_lower.append(words[-1])

    print("NEXT search terms: ", search_terms_lower)

    search_terms_lower_singular_1 = [f"{term[:-1]}" for term in search_terms_lower if term[-1] == "s"]
    search_terms_lower_singular_2 = [f"{term[:-2]}" for term in search_terms_lower if term[-2:] == "es"]
    search_terms_lower.extend(search_terms_lower_singular_1)
    search_terms_lower.extend(search_terms_lower_singular_2)

    print("FINAL search terms: ", search_terms_lower)

    for name, obj in inspect.getmembers(models_module, inspect.isclass):
        # check if class has a "names" attribute
        if not hasattr(obj, "names"):
            # print("continued 1")
            continue

        synonyms: list[str] = obj.names

        obj = cast(type[SuperNode], obj)

        synonyms_lower = [syn.lower() for syn in synonyms]
        synonyms_plural_lower = [f"{syn}s" for syn in synonyms_lower]
        synonyms_singular_lower = [f"{syn[:-1]}" for syn in synonyms_lower if syn[-1] == "s"]
        synonyms_singular_lower_es = [f"{syn[:-2]}" for syn in synonyms_lower if syn[-2:] == "es"]


        synonyms_lower.extend(synonyms_plural_lower)
        synonyms_lower.extend(synonyms_singular_lower)
        synonyms_lower.extend(synonyms_singular_lower_es)
        synonyms_lower.append(name.lower())
        # print("synonyms_lower: ", synonyms_lower, "and search_terms_lower: ", search_terms_lower)


        # Check if any of the search terms match the class name or any of the synonyms
        if any(term in synonyms_lower for term in search_terms_lower):

            obj_instance = obj()
            
            matched_objects.extend(obj_instance.model())

            matched_interfaces.extend(obj_instance.add_interface())

    print("matched_objects: ", matched_objects)
    print("matched_interfaces: ", matched_interfaces)

    return (matched_objects, matched_interfaces)




def matches_to_scene(matched_objects: list[type[BaseModel]], matched_interfaces: list[Union[type[BaseModel], Any]], text: str):

    # print("matched: ", matched_objects)

    # if len(matched_interfaces) == 0:
    #     matched_interfaces.append(Any)

    if len(matched_objects) == 0:
        return None
    

    # UnionMatchedObjects = Union[*matched_objects]
    GenericObject = Annotated[Union[*matched_objects], Field(discriminator='t')]
    

    if len(matched_interfaces) == 0:
        ReturnType = create_model(
            'ReturnType',
            objects=(list[GenericObject], ...))
    else:
        GenericInterface = Union[*matched_interfaces]
        
        ReturnType = create_model(
            'ReturnType',
            objects=(list[GenericObject], ...),
            interfaces=(list[GenericInterface], ...))

    print("DONE CREATING RETURN TYPE")

    # print("Recturn Type schema: ", ReturnType.model_json_schema())

    # ReturnType.model_json_schema()


    completion_schema = json.dumps(ReturnType.model_json_schema(), indent=4)

    with open("completion_schema.json", "w") as f:
            f.write(completion_schema)

    # Build a scene description. Interfaces MUST be used between every object-object connection. 
    # If Interface<name> MUST connect to an object with name <name>.

    # example: 
    # InterfaceRF must connect to an object with name RF.
    # InterfaceLight must connect to an object with name Light.

    # You MUST include object <name> if you also include Interface<name> in the scene.
    # print(ReturnType.model_json_schema())

    prompt = f"""
    
    If you use <InterfaceFiber>, you must connected it to an object with name <Fiber>.
    Every <Fiber> requires 2 <InterfaceFiber> connections on both ends. 

    examples: 
    <box> <--InterfaceFiber--> <Fiber> <--InterfaceFiber--> <box> <--InterfaceFiber--> <Fiber> <--InterfaceFiber--> <switch>
    <laser> <--InterfaceFiber--> <Fiber> <--InterfaceFiber--> <switch> <--InterfaceFiber--> <Fiber> <--InterfaceFiber--> <box>


    Common object parameters:
    x: -480(left) > x < 480(right). 0 is center of screen. x location + width/2 must be less than 480.
    y: -270(bottom) > y < 270(top). 0 is center of screen. y location + height/2 must be less than 270.
    
    The scene description: {text}"""

    print("USING SCENE MODEL: ", scene_model.model)

    print("this is return type: ", ReturnType)

    # try:
    user, completion = scene_model.client.chat.completions.create_with_completion(
        model=scene_model.model,
        max_tokens = 3000,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_model=ReturnType,
    )

    # except Exception as e:
    #         # general exception handling
    #         logger.error("ERROR: %s", e)
    #         return None
    

    # print("completion: ", completion.model_dump_json())

    # print("completion: ", completion)

    # print("choices 0, tool calls", completion.choices[0])
    # print("choices 0, tool calls", completion.choices[0].message.tool_calls)

    completion = cast(ChatCompletion, completion)


    
    # completion.choices[0].message.tool_calls[0].function.arguments

    # completion.choices[0].

    if scene_model.client == client_anthropic:

        # print(completion.content[0].text)
        completion_string = cast(str, completion.content[0].text)
        completion_model = ReturnType.model_validate_json(completion.content[0].text)

    else:
        completion_string = cast(str, completion.choices[0].message.tool_calls[0].function.arguments)

    # Parse the JSON string to a Python dictionary
    parsed_completion_string = json.loads(completion_string)

    # Pretty-print the raw completion string
    pretty_raw_json = json.dumps(parsed_completion_string, indent=4)
    with open("completion_raw.json", "w") as f:
        f.write(pretty_raw_json)

    completion_model = ReturnType.model_validate_json(completion_string)

    # print("completion model: ", completion_model)

    print(completion.usage)

    # Pretty-print the completion model
    pretty_json = json.dumps(json.loads(completion_model.model_dump_json()), indent=4)
    with open("completion.json", "w") as f:
        f.write(pretty_json)


    print("COMPLETION: ", completion_model)

    


    # print("completion raw: ", completion._raw_response)

    # Its now a dict, no need to worry about json loading so many times
    # response_data = completion.model_dump()

    # for item in completion.objects:
    #     print(item)
    

# except openai.RateLimitError as e:
#     # request limit exceeded or something.
#     logger.warning("%s", e)



    # print(completion.model_dump_json())

    # return completion
    return completion_model



class ModelRequest(BaseModel):
    value: str


@app.post("/set-scene-model")
def set_scene_model(request: ModelRequest):
    model_str = request.value

    if model_str == "gpt-4o":
        scene_model.model = model_str
        scene_model.client = client_openai

    elif model_str == "gpt-4o-mini":
        scene_model.model = model_str
        scene_model.client = client_openai

    elif model_str == "llama3-groq-70b-8192-tool-use-preview":
        scene_model.model = model_str
        scene_model.client = client_groq

    elif model_str == "llama3-groq-8b-8192-tool-use-preview":
        scene_model.model = model_str
        scene_model.client = client_groq

    elif model_str == "mixtral-8x7b-32768":
        scene_model.model = model_str
        scene_model.client = client_groq

    elif model_str == "claude-3-5-sonnet-20240620":
        scene_model.model = model_str
        scene_model.client = client_anthropic

    elif model_str == "llama-3.1-70b-versatile":
        scene_model.model = model_str
        scene_model.client = client_groq


@app.post("/set-decoder-model")
def set_decoder_model(request: ModelRequest):
    model_str = request.value

    print("received model_str: ", model_str)

    if model_str == "gpt-4o":
        decoder_model.model = model_str
        decoder_model.client = client_openai

    elif model_str == "gpt-4o-mini":
        decoder_model.model = model_str
        decoder_model.client = client_openai

    elif model_str == "llama3-groq-70b-8192-tool-use-preview":
        decoder_model.model = model_str
        decoder_model.client = client_groq

    elif model_str == "llama3-groq-8b-8192-tool-use-preview":
        decoder_model.model = model_str
        decoder_model.client = client_groq

    elif model_str == "mixtral-8x7b-32768":
        decoder_model.model = model_str
        decoder_model.client = client_groq

    elif model_str == "claude-3-5-sonnet-20240620":
        decoder_model.model = model_str
        decoder_model.client = client_anthropic

    elif model_str == "llama-3.1-70b-versatile":
        scene_model.model = model_str
        scene_model.client = client_groq

    

    


# text_to_search("A circle is located next to a square. A triangle is to the left of both of them.")
# text_to_search("A blue circle and a square are on opposite sides of a vertical long and thin rectangle that's colored grey. By the way, the square is yellow.")