import sys
import os
import json
import pathlib
import asyncio
import logging

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_agent.agent import LLMAgent
from config.logger_config import setup_logger

logger = setup_logger(__name__, level=logging.DEBUG)

# TODO: Implement Logger
# BUG: Layout does not change for first button press

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
            return response.get('relevancy_score')
        
        except Exception as e:
            logger.error(f"Error generating relevancy score: {e}")
            return -1
    

    # TODO: Update SW prompt to make it precise and reduce nesting
    # TODO: Make strengths and weaknesses a bit brief
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
        
        except AssertionError as e:
            logger.error(f"Error generating strengths and weaknesses: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error generating strengths and weaknesses: {e}")
            return {}


    async def get_strengths(self) -> list:
        """Get strengths from the generated response"""
        try:
            response = await self._generate_sw()
            return response['strengths']
        except Exception as e:
            logger.error(f"Error getting strengths: {e}")
            return {}


    async def get_weaknesses(self) -> list:
        """Get weaknesses from the generated response"""
        try:
            response = await self._generate_sw()
            return response['weaknesses']
        except Exception as e:
            logger.error(f"Error getting weaknesses: {e}")
            return {}
        

    # TODO: update keyword extraction
    # TODO: Handle keyword matching using LLM itself
    async def extract_keywords(self, source:str) -> dict:
        """Extract keywords from job description"""
        try:
            response = r"{'matching_keywords': [], 'non_matching_keywords': []}"
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
            
            elif source == "match":
                prompt_filepath = pathlib.Path(__file__).parent.parent / "prompts" / "extract_keywords.txt"
                with open(prompt_filepath, mode='r') as f:
                    prompt = f.read().strip()
                response = await self.llm_agent.generate_json_response(prompt, contents=[self.resume, self.job_description])
                response = response.text
            
            response = json.loads(response)
            return response
        
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return {}


# Main function to run the class and functions on test inputs
async def main():
    resume = pathlib.Path(__file__).parent.parent / "sample_data" / "resumes" / "resume.txt"
    job_description = pathlib.Path(__file__).parent.parent / "sample_data" / "job_desc" / "jd.txt"
    
    with open(resume, mode='r') as f:
        resume = f.read()
    with open(job_description, mode='r') as f:
        job_description = f.read()
    resume_reviewer = ResumeReviewer(resume, job_description)
    res = await resume_reviewer.extract_keywords(source="match")
    logger.debug(f"Relevancy Score: {res}")

    
if __name__ == "__main__":
    asyncio.run(main())