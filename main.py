"""Natural Language Interface"""
import sys

import openai


def completion(messages):
    """completion"""
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    return chat_completion.choices[0].message.content


def prompt(arg):
    """prompt"""
    print(arg)
    # system, user, or assistant
    messages = [{"role": "user", "content": arg}]

    print(completion(messages))


# 1. Classification: Is prompt ephemeral or persistent (store it forever?)
# 2. Classification: What is the output type?
# 3. Classification: Is this a simple task/question, or will a larger plan be needed?
# 4. Planning: Create a multi-step plan to complete this task
#   - Include as context existing external and internal data sources
#   - Include as context unconfigured potential external data sources
#   - Ensure each step has a defined input and output (file, function return, etc.)
#   - Steps can prompt additional input from the user
#   - Specifically ensure that the final task has the proper desired output
# 5. Classification: Given the plan, determine if an external data source needs to be configured
#   - Prompt the user if necessary using external data source instructions
# 6. Classification: Verify the plan looks correct
# 7. Execution: Step by step, execute the plan:
#   - Always provide context as to the larger plan
#   - Always provide context on how to use data sources
#       - Eventually give better context using embeddings / vector db
#   - After each step, validate the output is correct
# 8. Completion
#   - If output is ephemeral, simply return information back to the frontend
#   - If output is persistent, save to a file if not already depending on output type
#   - Record information in layout.json
#   - Return stuff to frontend


def main():
    """main"""
    if len(sys.argv) != 2:
        sys.exit("Takes exactly one argument.")
    prompt(sys.argv[1])


if __name__ == "__main__":
    main()
