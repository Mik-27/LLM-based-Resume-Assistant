from google import genai
from google.genai import Client, types
import os
from dotenv import load_dotenv

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

    def generate_json_response(self, prompt: str, resume_data:str, job_description_data:str):
        """Generate JSON response from LLM model"""
        config = types.GenerateContentConfig(**self.model_config, response_mime_type="application/json")
        return self.client.models.generate_content(model=self.model, contents=[prompt, resume_data, job_description_data], config=config)
    
    def generate_text_response(self, prompt:str, resume_data:str, job_description_data:str):
        """Generate text response from LLM model"""
        config = types.GenerateContentConfig(**self.model_config, response_mime_type="text/plain")
        return self.client.models.generate_content(model=self.model, contents=[prompt, resume_data, job_description_data], config=config).text

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


if __name__ == "__main__":
    load_dotenv()
    agent = LLMAgent()
    print(agent.response_test("What is the capital of India?"))