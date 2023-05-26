"""Natural Language Interface"""
import json
import sys

import openai


def completion(messages):
    """completion"""
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    return chat_completion.choices[0].message.content


def get_output_type(arg):
    messages = [
        {
            "role": "system",
            "content": "A user will input a task/question. You must classify this request by providing the type of output that would best fit. Options: 'text', 'graph', 'spreadsheet', 'form', 'cron', 'empty'",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "spreadsheet"},
        {"role": "user", "content": arg},
    ]
    return completion(messages)


def create_plan(arg, output_type):
    # TODO: JSON PLAN
    messages = [
        {
            "role": "system",
            "content": "A user will input a task/question. You must classify this request by providing the type of output that would best fit. Options: 'text', 'graph', 'spreadsheet', 'form', 'cron', 'empty'",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "spreadsheet"},
        {"role": "user", "content": arg},
    ]
    return json.loads(completion(messages))


def get_required_data_sources(plan):
    return True


def get_existing_data_sources():
    return True


def prompt_user_for_data_sources():
    return True


def verify_plan(plan):
    return True


def execute_plan(plan):
    return True


def save_result(result):
    return True


def prompt(arg):
    """prompt"""

    output_type = get_output_type(arg)
    print(f"output_type {output_type}")

    # plan = create_plan(arg, output_type)
    # required_data_sources = get_required_data_sources(plan)
    # existing_data_sources = get_existing_data_sources()
    # needed_data_sources = required_data_sources.difference(existing_data_sources)
    # prompt_user_for_data_sources(needed_data_sources)
    # existing_data_sources = get_existing_data_sources()
    # verify_plan(plan)
    # result = execute_plan(plan)
    # save_result(result)
    # return result


# 2. Classification: What is the output type?
# 3. Planning: Create a multi-step plan to complete this task
#   - Include as context existing external and internal data sources
#   - Include as context unconfigured potential external data sources
#   - Ensure each step has a defined input and output (file, function return, etc.)
#   - Steps can prompt additional input from the user
#   - Specifically ensure that the final task has the proper desired output
# 4. Classification: Given the plan, determine if an external data source needs to be configured
#   - Prompt the user if necessary using external data source instructions
# 5. Classification: Verify the plan looks correct
# 6. Execution: Step by step, execute the plan:
#   - Always provide context as to the larger plan
#   - Always provide context on how to use data sources
#       - Eventually give better context using embeddings / vector db
#   - After each step, validate the output is correct
# 7. Completion
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
