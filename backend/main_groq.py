import uvicorn
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from typing_extensions import Annotated
from typing import Literal, Union, Type

from pydantic import Field

from backend.server_logging import get_logger
logger = get_logger(__name__)

from pydantic import BaseModel, create_model


from openai import OpenAI
import instructor

from dotenv import load_dotenv  # Import load_dotenv
# Load environment variables from .env file
import openai
from groq import Groq

from backend.models import Circle, Polygon, Rect

from backend.models import SuperNode
from typing import cast
from typing import Any

import importlib
import inspect
from typing import get_type_hints, Literal, get_origin


from fastapi.middleware.cors import CORSMiddleware



# from typing import get_origin, Literal


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
    prompt = f""" pull terms from the following text for building a knowledge graph: '{text}'"""
    logger.info("starting openai call: %s", prompt)

    completion = SearchTerms(search_terms=[])

    try:
        completion: SearchTerms = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            # model="llama-3.1-70b-versatile",
            # model="llama-3.1-8b-instant",
            # model="mixtral-8x7b-32768",
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
    models_module = importlib.import_module("backend.models")
    print("search terms: ", s.search_terms)
    matched_objects: list[type[BaseModel]] = []
    matched_interfaces: list[type[BaseModel]] = []

    for name, obj in inspect.getmembers(models_module, inspect.isclass):
        # Ensure the class is defined in the models_module
        # if inspect.getmodule(obj) != models_module:
        #     continue

        # # Check if the class has a 'name' attribute and it is a Literal
        # hints = get_type_hints(obj)
        # if 'name' not in hints or get_origin(hints['name']) != Literal:
        #     continue

        # # Extract the possible values from the Literal type hint for 'name'
        # synonyms = hints['name'].__args__
        # logger.info("synonyms: %s", synonyms)

        # check if class has a "names" attribute
        if not hasattr(obj, "names"):
            # print("continued 1")
            continue

        synonyms = obj.names

        obj = cast(type[SuperNode], obj)

        obj_instance = obj()

        # Convert search terms and synonyms to lowercase for case-insensitive comparison
        search_terms_lower = [term.lower() for term in s.search_terms]


        # Modified code to include both the original terms and the last word of each term if it contains spaces
        search_terms_lower: list[str] = []
        for term in s.search_terms:
            term_lower = term.lower()
            search_terms_lower.append(term_lower)
            # Split the term by spaces and add the last word if it's not the only word
            words = term_lower.split()
            if len(words) > 1:
                search_terms_lower.append(words[-1])

        # logger.info("expanded search terms: %s", search_terms_lower)

        synonyms_lower = [syn.lower() for syn in synonyms]
        synonyms_plural_lower = [f"{syn}s" for syn in synonyms_lower]
        synonyms_lower.extend(synonyms_plural_lower)

        # Check if any of the search terms match the class name or any of the synonyms
        if any(term in name.lower() or term in synonyms_lower for term in search_terms_lower):

            
            matched_objects.extend(obj_instance.model())

            matched_interfaces.extend(obj_instance.add_interface())

    return (matched_objects, matched_interfaces)




def matches_to_scene(matched_objects: list[type[BaseModel]], matched_interfaces: list[Union[type[BaseModel], Any]], text: str):

    # print("matched: ", matched_objects)

    # if len(matched_interfaces) == 0:
    #     matched_interfaces.append(Any)
    
    GenericObject = Annotated[Union[*matched_objects], Field(discriminator='t')] # type: ignore
    

    if len(matched_interfaces) == 0:
        ReturnType = create_model(
            'ReturnType',
            objects=(list[GenericObject], ...))
    else:
        GenericInterface = Union[*matched_interfaces] # type: ignore
        
        ReturnType = create_model(
            'ReturnType',
            objects=(list[GenericObject], ...),
            interfaces=(list[GenericInterface], ...))

        

    # class ReturnType(BaseModel):
    #     objects: list[GenericObject] = []
    #     interfaces: list[GenericInterface] = []

    # completion = ReturnType(scene=[Circle(name="circle", size=30, fill="green", position=Vector(x=0, y=0))])

    prompt = f"""Build a scene description. 
    Common object parameters:
    x: -480(left) > x < 480(right). 0 is center of screen.
    y: -270(bottom) > y < 270(top). 0 is center of screen.
    
    The scene description: {text}"""

    try:
        completion = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            # model="llama-3.1-70b-versatile",
            # model="llama-3.1-8b-instant",
            # model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_model=ReturnType,
        )
        print("completion: ", completion)
        # print("completion raw: ", completion._raw_response)

        # Its now a dict, no need to worry about json loading so many times
        # response_data = completion.model_dump()

        # for item in completion.objects:
        #     print(item)
        

    # except openai.RateLimitError as e:
    #     # request limit exceeded or something.
    #     logger.warning("%s", e)

    except Exception as e:
        # general exception handling
        logger.error("ERROR: %s", e)
        return None

    # print(completion.model_dump_json())

    return completion

    


# text_to_search("A circle is located next to a square. A triangle is to the left of both of them.")
# text_to_search("A blue circle and a square are on opposite sides of a vertical long and thin rectangle that's colored grey. By the way, the square is yellow.")