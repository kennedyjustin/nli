"""Natural Language Interface"""

import json
import uuid
import sys

import openai


def completion(name, messages, verification, max_attempts):
    count = 0
    while True:
        count += 1
        print(f"Attempting completion for {name} (attempt {count})")
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        result = chat_completion.choices[0].message.content
        if verification(result):
            return result
        if count >= max_attempts:
            raise Exception(f"Max attempts ({max_attempts}) reached for {name}")


def create_title(prompt):
    messages = [
        {
            "role": "system",
            "content": "Create a short title for the following question/task",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "Earning's Report"},
        {"role": "user", "content": prompt},
    ]
    return completion("create_title", messages, lambda x: None, 1)


def get_output_type(prompt):
    output_types = ["text", "graph", "spreadsheet", "form", "cron", "empty"]
    messages = [
        {
            "role": "system",
            "content": f"A user will input a task/question. You must classify this request by providing the type of output that would best fit. Options: {output_types}",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "spreadsheet"},
        {"role": "user", "content": prompt},
    ]
    return completion("get_output_type", messages, lambda x: x in output_types, 3)


def verify_step(step, previous_output_type):
    if step.input_type != previous_output_type:
        return False
    messages = [
        {
            "role": "system",
            "content": "",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "True"},
        {
            "role": "user",
            "content": "",
        },
    ]

    result = completion(
        "verify_step",
        messages,
        lambda x: x in ["True", "False"],
        1,
    )
    return True if result == "True" else False


def verify_plan(prompt, steps, output_type):
    has_correct_shape = isinstance(steps, list) and all(
        verify_step_shape(step) for step in steps
    )
    if not has_correct_shape:
        return False

    previous_output_type = ""
    for step in steps:
        previous_output_type = step.output_type
        if not verify_step(step, previous_output_type):
            return False

    messages = [
        {
            "role": "system",
            "content": "",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "True"},
        {
            "role": "user",
            "content": f"prompt: {prompt}, steps: {steps}, output_type: {output_type}",
        },
    ]

    result = completion(
        "verify_plan",
        messages,
        lambda x: x in ["True", "False"],
        3,
    )
    return True if result == "True" else False


def verify_step_shape(step):
    step_types = []
    return all(
        hasattr(step, "text"),
        isinstance(step.text, str),
        hasattr(step, "input"),
        step.input in step_types,
        hasattr(step, "output"),
        step.output in step_types,
    )


def create_plan(prompt):
    output_type = get_output_type(prompt)
    print(f"output_type {output_type}")

    messages = [
        {
            "role": "system",
            "content": "",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "spreadsheet"},
        {"role": "user", "content": prompt},
    ]

    steps = json.loads(
        completion(
            "create_plan",
            messages,
            lambda x: verify_plan(prompt, steps, output_type),
            3,
        )
    )

    return {"steps": steps, "output_type": output_type}


def verify_step_result(step, result):
    messages = [
        {
            "role": "system",
            "content": "",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "spreadsheet"},
        {"role": "user", "content": f"step: {step}, result: {result}"},
    ]

    return completion(
        "verify_step_result",
        messages,
        lambda x: None,
        1,
    )


def execute_step_code(code, input, memory):
    # TODO Run code
    return True


def execute_step(step, input, memory):
    messages = [
        {
            "role": "system",
            "content": "",
        },
        {"role": "user", "content": "Give me a report of last week's earnings"},
        {"role": "user", "content": "spreadsheet"},
        {"role": "user", "content": f"memory: ${memory}, text: {step.text}"},
    ]

    # Note do stuff depending on step type (if code, verify code generated, if not, verify output type, etc.)
    result = completion(
        "execute_step",
        messages,
        lambda x: verify_step_result(step, x),
        3,
    )

    if step.type == "code":
        result = execute_step_code(result, input, memory)

    # Check output type is correct

    return result


def execute_plan(plan):
    outputs = []
    memory = []
    for step in plan.steps:
        result = execute_step(step, outputs[-1], memory)
        outputs.append(memory.output)
        memory.append(result.memory)

    return outputs[-1]


def save_result(title, prompt, plan, result):
    filename = f"${uuid.uuid4()}.json"
    f = open(filename, "w")
    f.write(
        json.dumps({"title": title, "prompt": prompt, "plan": plan, "result": result})
    )
    f.close()


def handle(prompt):
    title = create_title(prompt)
    print(f"title {title}")

    plan = create_plan(prompt)
    print(f"plan {plan}")

    # figure out data sources

    result = execute_plan(plan)
    print(f"result {result}")

    filename = save_result(title, prompt, plan, result)
    print(f"filename {filename}")


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
    if len(sys.argv) != 2:
        sys.exit("Takes exactly one argument.")
    handle(sys.argv[1])


if __name__ == "__main__":
    main()
