#!/usr/bin/env python
import sys
import warnings

from .crew import Maffb

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    
    try:
        print("🚀 Starting Maffb crew for blog content processing...")
        result = Maffb().crew().kickoff()
        print("✅ Crew execution completed successfully!")
        print(f"📊 Crew result type: {type(result)}")
        return result
    except Exception as e:
        print(f"❌ An error occurred while running the crew: {e}")
        import traceback
        traceback.print_exc()
        raise


def train():
    """
    Train the crew for a given number of iterations.
    """
    try:
        Maffb().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2])

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Maffb().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    try:
        Maffb().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2])

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    # Default to running the crew
    run()
