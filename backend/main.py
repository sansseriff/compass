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

from pydantic import BaseModel


from openai import OpenAI
import instructor

from dotenv import load_dotenv  # Import load_dotenv
# Load environment variables from .env file
import openai

from backend.models import Circle, Polygon, Rect


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



client = instructor.from_openai(OpenAI())


class SearchTerms(BaseModel):
    search_terms: list[str]


# class Scene(BaseModel):
#     scene: list[BaseModel]

class Message(BaseModel):
    message: str

@app.post("/scene")
def text_to_search(msg: Message):

    text = msg.message
    prompt = f"""make a list of search terms that might label the nodes in the following text, if 
    the text was expressed as a knowledge graph. Include both nouns and nouns with modifiers.

    Examples:
    INPUT: A triangle sits on top of a long and thing blue rectangle. Hovering above the triangle is a small red circle.
    OUTPUT: "triangle", "long blue rectangle", "rectangle", "small red circle", "circle"

    INPUT: "Below a square is a large green circle. To the right of the circle is a small yellow triangle."
    OUTPUT: "square", "large green circle", "circle", "small yellow triangle", "triangle"

    INPUT: {text}
    OUTPUT: """
    # logger.info("starting openai call: %s", prompt)

    completion = SearchTerms(search_terms=[])

    try:
        completion: SearchTerms = client.chat.completions.create(
            # model="gpt-4-turbo",
            model="gpt-4o-mini",
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
        logger.error("%s", e)

    models = search_search(completion)
    return matches_to_scene(models, text)

        


def search_search(s: SearchTerms):
    models_module = importlib.import_module("backend.models")
    print("search terms: ", s.search_terms)
    matched_classes: list[BaseModel] = []

    for name, obj in inspect.getmembers(models_module, inspect.isclass):
        # Ensure the class is defined in the models_module
        if inspect.getmodule(obj) != models_module:
            continue

        # Check if the class has a 'name' attribute and it is a Literal
        hints = get_type_hints(obj)
        if 'name' not in hints or get_origin(hints['name']) != Literal:
            continue

        # Extract the possible values from the Literal type hint for 'name'
        synonyms = hints['name'].__args__
        logger.info("synonyms: %s", synonyms)

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

        logger.info("expanded search terms: %s", search_terms_lower)

        synonyms_lower = [syn.lower() for syn in synonyms]
        synonyms_plural_lower = [f"{syn}s" for syn in synonyms_lower]
        synonyms_lower.extend(synonyms_plural_lower)

        # Check if any of the search terms match the class name or any of the synonyms
        if any(term in name.lower() or term in synonyms_lower for term in search_terms_lower):
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




def matches_to_scene(matched: list[BaseModel], text: str):

    print("matched: ", matched)
    GenericObject = Annotated[Union[*matched], Field(discriminator='t')] # type: ignore

    class ReturnType(BaseModel):
        scene: list[GenericObject]

    # completion = ReturnType(scene=[Circle(name="circle", size=30, fill="green", position=Vector(x=0, y=0))])

    prompt = f"Build a scene description that matches the following text. {text}"

    try:
        completion: ReturnType = client.chat.completions.create(
            # model="gpt-4-turbo",
            model="gpt-4o-mini",
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

    return completion

    


# text_to_search("A circle is located next to a square. A triangle is to the left of both of them.")
# text_to_search("A blue circle and a square are on opposite sides of a vertical long and thin rectangle that's colored grey. By the way, the square is yellow.")