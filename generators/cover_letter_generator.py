import sys
import os
import json
import datetime

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_agent.agent import LLMAgent


class CoverLetterGenerator:
    """Class to generate cover letter based on personal information and job description"""

    def __init__(self, resume, job_description):
        self.llm_agent = LLMAgent()
        self.resume = resume
        self.job_description = job_description

    def _get_current_date(self):
        """Get current date"""
        return datetime.datetime.now().strftime("%B %d, %Y")

    def _get_company_name(self):
        pass

    def _get_personal_information(self):
        pass

    def generate_cover_letter(self):
        """Generate cover letter based on personal information and job description"""
        try:
            with open("../prompts/cover_letter.txt", mode='r') as f:
                prompt = f.read().strip()
            response = self.llm_agent.generate_text_response(prompt, self.resume, self.job_description)
            return response
        
        except Exception as e:
            print(e)

