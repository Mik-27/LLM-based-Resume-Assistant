import sys
import os
import json
import pathlib
import asyncio

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_agent.agent import LLMAgent

# TODO: Implement Logger

class ResumeReviewer:
    """Class to generate relevancy score between resume and job description"""

    def __init__(self, resume, job_description):
        self.llm_agent = LLMAgent()
        self.resume = resume
        self.job_description = job_description


    async def generate_relevancy_score(self):
        """Generate relevancy score between resume and job description"""
        try:
            prompt_filepath = pathlib.Path(__file__).parent.parent / "prompts" / "relevancy_score.txt"
            with open(prompt_filepath, mode='r') as f:
                prompt = f.read().strip()

            contents = [self.resume, self.job_description]
            response = await self.llm_agent.generate_json_response(prompt, contents=contents)
            response = json.loads(response.text)
            # print(response)
            # print(self.resume, self.job_description)
            return response.get('relevancy_score')
        except Exception as e:
            print("score",e)

    
    # TODO: Update SW prompt to make it precise and reduce nesting
    async def _generate_sw(self) -> dict:
        """Generate strengths and weaknesses of resume based on job description"""
        try:
            prompt_filepath = pathlib.Path(__file__).parent.parent / "prompts" / "strengths_weaknesses.txt"
            with open(prompt_filepath, mode='r') as f:
                prompt = f.read().strip()
            response = await self.llm_agent.generate_json_response(prompt, contents=[self.resume, self.job_description])
            response = json.loads(response.text)

            assert type(response) == dict
            assert 'strengths' in response and 'weaknesses' in response
            
            return response
        
        except Exception as e:
            print(e)


    async def get_strengths(self) -> list:
        """Get strengths from the generated response"""
        response = await self._generate_sw()
        return response['strengths']


    async def get_weaknesses(self) -> list:
        """Get weaknesses from the generated response"""
        response = await self._generate_sw()
        return response['weaknesses']
    

    # TODO: update keyword extraction
    # TODO: Handle keyword matching using LLM itself
    async def extract_keywords(self, source:str) -> dict:
        """Extract keywords from job description"""
        try:
            if source == "resume":
                prompt_filepath = pathlib.Path(__file__).parent.parent / "prompts" / "extract_keywords_resume.txt"
                with open(prompt_filepath, mode='r') as f:
                    prompt = f.read().strip()
                response = await self.llm_agent.generate_json_response(prompt, contents=[self.resume])
            elif source == "job":
                prompt_filepath = pathlib.Path(__file__).parent.parent / "prompts" / "extract_keywords_jd.txt"
                with open(prompt_filepath, mode='r') as f:
                    prompt = f.read().strip()
                response = await self.llm_agent.generate_json_response(prompt, contents=[self.job_description])

            response = json.loads(response.text)
            return response
        
        except Exception as e:
            print(e)


# Main function to run the class and functions on test inputs
async def main():
    resume = "I am a software engineer with 5 years of experience"
    job_description = "We are looking for a software engineer with 5 years of experience"
    resume_reviewer = ResumeReviewer(resume, job_description)
    res = await resume_reviewer.generate_relevancy_score()

    
if __name__ == "__main__":
    asyncio.run(main())