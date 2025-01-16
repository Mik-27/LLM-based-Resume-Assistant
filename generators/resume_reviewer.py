import sys
import os
import json

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_agent.agent import LLMAgent


class ResumeReviewer:
    """Class to generate relevancy score between resume and job description"""

    def __init__(self, resume, job_description):
        self.llm_agent = LLMAgent()
        self.resume = resume
        self.job_description = job_description


    def generate_relevancy_score(self):
        """Generate relevancy score between resume and job description"""
        try:
            with open("../prompts/relevancy_score.txt", mode='r') as f:
                prompt = f.read().strip()
            response = self.llm_agent.generate_json_response(prompt, self.resume, self.job_description)
            response = json.loads(response.text)
            return response
        except Exception as e:
            print(e)

    
    def _generate_sw(self) -> dict:
        """Generate strengths and weaknesses of resume based on job description"""
        try:
            with open("../prompts/strengths_weaknesses.txt", mode='r') as f:
                prompt = f.read().strip()
            response = self.llm_agent.generate_json_response(prompt, self.resume, self.job_description)
            response = json.loads(response.text)

            assert type(response) == dict
            assert 'strengths' in response and 'weaknesses' in response
            
            return response
        
        except Exception as e:
            print(e)


    def get_strengths(self) -> list:
        """Get strengths from the generated response"""
        response = self._generate_sw()
        return response['strengths']


    def get_weaknesses(self) -> list:
        """Get weaknesses from the generated response"""
        response = self._generate_sw()
        return response['weaknesses']
    
    
    def extract_keywords(self, source:str) -> dict:
        """Extract keywords from job description"""
        try:
            if source == "resume":
                with open("../prompts/extract_keywords.txt", mode='r') as f:
                    prompt = f.read().strip()
                response = self.llm_agent.generate_json_response(prompt, self.resume)
            else:
                with open("../prompts/extract_keywords.txt", mode='r') as f:
                    prompt = f.read().strip()
                response = self.llm_agent.generate_json_response(prompt, self.job_description)
            response = json.loads(response.text)
            return response
        except Exception as e:
            print(e)



    
if __name__ == "__main__":
    resume = "I am a software engineer with 5 years of experience"
    job_description = "We are looking for a software engineer with 5 years of experience"
    resume_reviewer = ResumeReviewer(resume, job_description)
    print(resume_reviewer._generate_sw())