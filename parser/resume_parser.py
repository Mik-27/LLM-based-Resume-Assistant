import sys
import os
import json
import pathlib

from google import genai

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.connection import DatabaseConnection
from llm_agent.agent import LLMAgent


class ResumeParser:
    """Parse resume to extract relevant information"""
    def __init__(self):
        self.agent = LLMAgent()
        self.dbClient = DatabaseConnection()

    def extract_information(self, filename:str, loc='local') -> dict:
        """Extract information from resume"""

        # Read resume file
        filepath = pathlib.Path(__file__).parent.parent / "sample_data" / "resumes" / filename
        # filepath = "../sample_data/resumes/Mihir_Thakur_Resume_CITI_Python.pdf"
        try:
            path = pathlib.Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"File not found at path: {path}")
            # print(path)
            file = self.agent.client.files.upload(path=path)
            # print(type(file))
        except Exception as e:
            print(e)
        
        if loc == 'local':
            try:
                prompt_filepath = pathlib.Path(__file__).parent.parent / "prompts" / "resume_parser.txt"
                with open(prompt_filepath, mode='r') as f:
                    prompt = f.read().strip()
                response = self.agent.generate_response_using_file(prompt, file)
                response = json.loads(response.text)
                return response
            except Exception as e:
                print(e)

        elif loc == 'cloud':
            pass
        

    def initialise_db(self):
        """Initialise database connection"""
        try:
            self.dbClient.connect()
            self.dbClient.create_database("resume_db")
            self.dbClient.create_collection(self.dbClient.database, "resume_collection")
        except Exception as e:
            print(e)


    def save_resume_to_db(self, filename:str):
        """Save resume information into database"""
        try:
            print("Initializing Database Connection...")
            self.initialise_db()
            resume_data = self.extract_information(filename)[0]
            # Insert JSON document into database
            self.dbClient.insert_document(resume_data)
        except Exception as e:
            print(e)
        finally:
            self.dbClient.disconnect()


if __name__ == "__main__":
    parser = ResumeParser()
    parser.save_resume_to_db("Mihir_Thakur_Resume_CITI_Python.pdf")