import os
import sys
import asyncio

from google import genai
from google.genai import Client, types
from dotenv import load_dotenv

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.helpers import get_current_date

class LLMAgent:
    """Agent for sending prompt to LLM model and getting response"""
    def __init__(self):
        load_dotenv()
        self.client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.0-flash-exp"
        self.model_config = {"max_output_tokens": 8192,
                             "temperature": 0.75,
                             "top_p": 0.95,
                             "top_k": 40}

    async def generate_json_response(self, prompt: str, contents: list):
        """Generate JSON response from LLM model"""
        config = types.GenerateContentConfig(**self.model_config, response_mime_type="application/json")
        return await self.client.aio.models.generate_content(model=self.model, contents=[prompt]+contents, config=config)
    
    # Update function as per above one
    async def generate_text_response(self, prompt:str, resume_data:str, job_description_data:str, metadata:str=None):
        """Generate text response from LLM model"""
        config = types.GenerateContentConfig(**self.model_config, response_mime_type="text/plain")
        res = await self.client.aio.models.generate_content(model=self.model, contents=[prompt, resume_data, job_description_data, metadata], config=config)
        return res.text
    

    def generate_response_using_file(self, prompt:str, file:genai.types.File):
        """Generate response using file"""
        config = types.GenerateContentConfig(**self.model_config, response_mime_type="application/json")
        return self.client.models.generate_content(
            model=self.model, 
            contents=[prompt, 
                      types.Content(
                          role="user",
                          parts=[
                              types.Part.from_uri(
                                  file_uri=file.uri,
                                  mime_type=file.mime_type),
                                ])
                      ], 
            config=config)

    def response_test(self, query:str):
        return self.client.models.generate_content(model=self.model, contents=query, config=self.model_config)


async def main():
    load_dotenv()
    agent = LLMAgent()
    resume = "I am a software engineer with 5 years of experience."
    description = "We are looking for a software engineer with 5 years of experience."
    res = await agent.generate_text_response("What are your strengths and weaknesses?", resume, description)
    print(res, type(res))


if __name__ == "__main__":
    asyncio.run(main())