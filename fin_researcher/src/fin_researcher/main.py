#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from fin_researcher.crew import FinResearcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the financeial researcher crew.
    """
    inputs = {
        'company': 'Tesla'
    }
    result= FinResearcher().crew().kickoff(inputs=inputs)
    print(result.raw) 

if __name__=="__main__":
    run()
    
    