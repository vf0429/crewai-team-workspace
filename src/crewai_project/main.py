import os
import sys

# Add current dir to path so we can import crew
sys.path.insert(0, os.path.dirname(__file__))

from crew import my_crew

def run():
    print("Kicking off the CrewAI process...")
    result = my_crew.kickoff()
    
    print("\n\n######################")
    print("FINAL RESULT:")
    print("######################\n")
    print(result)

if __name__ == "__main__":
    run()
