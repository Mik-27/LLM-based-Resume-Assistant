import sys
import os
import pathlib
import asyncio
import datetime
import logging
import json

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import defaultdict
from llm_agent.agent import LLMAgent
from config.logger_config import setup_logger
from util.helpers import get_current_date

logger = setup_logger(__name__, level=logging.DEBUG)


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

    # TODO: pass parameters, personal information, strengths and weakeness.]
    async def generate_cover_letter(self, addl_info: dict = {}) -> str:
        """Generate cover letter based on personal information and job description"""
        try:
            metadata = defaultdict(str)
            metadata['date_today'] = self._get_current_date()
            prompt_filepath = pathlib.Path(__file__).parent.parent / "prompts" / "cover_letter.txt"
            with open(prompt_filepath, mode='r', encoding='utf-8') as f:
                prompt = f.read().strip()

            response = await self.llm_agent.generate_text_response(prompt, self.resume, self.job_description, metadata=json.dumps(metadata))
            return response
        
        except Exception as e:
            print("Error generating cover letter.",e)


async def main():
    resume = pathlib.Path(__file__).parent.parent / "sample_data" / "resumes" / "resume.txt"
    job_description = pathlib.Path(__file__).parent.parent / "sample_data" / "job_desc" / "jd.txt"
    
    with open(resume, mode='r') as f:
        resume = f.read()
    with open(job_description, mode='r') as f:
        job_description = f.read()
    cover_letter_generator = CoverLetterGenerator(resume, job_description)
    res = await cover_letter_generator.generate_cover_letter()
    logger.debug(f"Cover Letter:\n {res}")

    

if __name__ == "__main__":
    asyncio.run(main())
