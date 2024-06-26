import uvicorn
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server_logging import get_logger
logger = get_logger(__name__)

from pydantic import BaseModel


from openai import OpenAI
import instructor

from dotenv import load_dotenv  # Import load_dotenv
# Load environment variables from .env file
import openai
load_dotenv()

app = FastAPI()
# Patch the OpenAI client
client = instructor.from_openai(OpenAI())


class SearchTerms(BaseModel):
    search_terms: list[str]


@app.post("/text_to_search")
def text_to_search(text: str):

    prompt = f"make a list of search terms that might label the nodes in the following text, if the text was expressed as a knowledge graph: {text}"
    logger.info("starting openai call: %s", prompt)

    try:
        completion: SearchTerms = client.chat.completions.create(
            model="gpt-4-turbo",
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

        logger.info("result: %s", completion)
    except openai.RateLimitError as e:
        # request limit exceeded or something.
        logger.warning("%s", e)

    except Exception as e:
        # general exception handling
        logger.error("%s", e)


text_to_search("While I like coffee and appreciate it, I prefer bitter tea")