import uvicorn
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from typing_extensions import Annotated
from typing import Literal, Union, Type

from pydantic import Field

from server_logging import get_logger
logger = get_logger(__name__)

from pydantic import BaseModel


from openai import OpenAI
import instructor

from dotenv import load_dotenv  # Import load_dotenv
# Load environment variables from .env file
import openai

from models import Circle, Polygon, Rect, Vector


import importlib
import inspect
from typing import get_type_hints, Literal, get_origin

# from typing import get_origin, Literal


load_dotenv()

app = FastAPI()
# Patch the OpenAI client
client = instructor.from_openai(OpenAI())


class SearchTerms(BaseModel):
    search_terms: list[str]


class Scene(BaseModel):
    scene: list[BaseModel]


@app.post("/text_to_search")
def text_to_search(text: str):

    prompt = f"""make a list of search terms that might label the nodes in the following text, if the text was expressed as a knowledge graph. Include both nouns and nouns with modifiers.

    {text}"""
    # logger.info("starting openai call: %s", prompt)

    completion = SearchTerms(search_terms=[])

    try:
        completion: SearchTerms = client.chat.completions.create(
            # model="gpt-4-turbo",
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_model=SearchTerms,
        )

        # Its now a dict, no need to worry about json loading so many times
        # response_data = completion.model_dump()

        # logger.info("result: %s", completion)
        

    except openai.RateLimitError as e:
        # request limit exceeded or something.
        logger.warning("%s", e)

    except Exception as e:
        # general exception handling
        logger.error("%s", e)

    models = search_search(completion)
    models_to_schema(models, text)

        


def search_search(s: SearchTerms):
    models_module = importlib.import_module("models")

    # print(models_module)
    matched_classes: list[BaseModel] = []

    for name, obj in inspect.getmembers(models_module, inspect.isclass):

        if inspect.getmodule(obj) == models_module:
            # Check if the class has a 'name' attribute and it is a Literal
            hints = get_type_hints(obj)
            if 'name' in hints and get_origin(hints['name']) == Literal:
                # Extract the possible values from the Literal type hint
                synonyms = hints['name'].__args__
                logger.info("synonyms: %s", synonyms)
                # Check if any of the search terms match the class name or any of the synonyms
                if any(search_term.lower() in name.lower() or search_term.lower() in (syn.lower() for syn in synonyms) for search_term in s.search_terms):
                    matched_classes.append(obj)


    # print("MATCHED CLASSES: ", matched_classes)


    # for cls in matched_classes:
    #     print(f"Class: {cls.__name__}")
    #     if hasattr(cls, "__fields__"):  # Check if Pydantic BaseModel or similar
    #         for field_name, field_info in cls.__fields__.items():
    #             print(f"  Field: {field_name}, Type: {field_info}")
    #     else:
    #         print("  No fields information available.")



    return matched_classes


# GenericObject = Annotated[Union[Circle, Polygon, Rect], Field(discriminator='t')] # type: ignore

# GenericObject = Union[Circle, Polygon, Rect] # type: ignore

#     # SpecificObject = Unnion

# print("generic object: ", GenericObject)

# class ReturnType(BaseModel):
#     scene: list[Circle | Polygon | Rect]



def models_to_schema(matched: list[BaseModel], text: str):

    
    GenericObject = Annotated[Union[*matched], Field(discriminator='t')] # type: ignore

    # SpecificObject = Unnion

    # print("generic object: ", GenericObject)

    class ReturnType(BaseModel):
        scene: list[GenericObject]

    # print("return type is: ", ReturnType.__fields__)


    completion = ReturnType(scene=[Circle(name="circle", size=30, fill="green", position=Vector(x=0, y=0))])

    prompt = f"Build a scene description that matches the following text: {text}"

    try:
        completion: ReturnType = client.chat.completions.create(
            # model="gpt-4-turbo",
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_model=ReturnType,
        )

        # Its now a dict, no need to worry about json loading so many times
        # response_data = completion.model_dump()

        for item in completion.scene:
            print(item)
        

    except openai.RateLimitError as e:
        # request limit exceeded or something.
        logger.warning("%s", e)

    except Exception as e:
        # general exception handling
        logger.error("%s", e)

    # print(completion)

    


text_to_search("A circle is located next to a square. A triangle is to the left of both of them.")