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
        # completion: SearchTerms = client_openai.chat.completions.create(
        completion: SearchTerms = client_groq.chat.completions.create(
            # model="gpt-4o-mini",
            # model="llama-3.1-70b-versatile",
            # model="llama-3.1-8b-instant",
            # model="llama3-groq-8b-8192-tool-use-preview",
            model="llama3-groq-70b-8192-tool-use-preview",
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

    prompt = f"""Build a scene description. Interfaces MUST be used between every object-object connection.


    Common object parameters:
    x: -480(left) > x < 480(right). 0 is center of screen.
    y: -270(bottom) > y < 270(top). 0 is center of screen.
    
    The scene description: {text}"""

    try:
        completion = client_openai.chat.completions.create(
        # completion = client_groq.chat.completions.create(
            model="gpt-4o-mini",
            # model="llama3-groq-70b-8192-tool-use-preview",
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
        print("completion: ", completion.model_dump_json())
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