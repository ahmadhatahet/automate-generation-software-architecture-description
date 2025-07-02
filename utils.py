import subprocess
import json
from PIL import Image


def save_solution_puml(
    solution,
    state_diagram_path,
    target_component,
    model,
    date_postfix,
):
    """
    Save the PlantUML solution to a file and render it to a PNG image.
    """
    solution_file = solution_path / f"{model}_{date_postfix}.puml"

    solution_file.parent.mkdir(parents=True, exist_ok=True)

    solution_file.write_text(solution)
    puml_to_png_output = subprocess.run(
        f"plantuml -tpng {str(solution_file)}", shell=True
    )


def save_chat_json(
    messages,
    solution,
    response,
    chat_path_component,
    filename,
    date_postfix,
):
    """Save chat messages to a JSON file."""
    messages_path = chat_path_component / f"{filename}_{date_postfix}.json"
    messages_path.touch()

    json.dump(
        {"solution": solution, "usage": response.usage.to_dict(), "messages": messages},
        messages_path.open("w"),
        indent=4,
    )


def save_chat_feedback_json(
    messages,
    messages_feedback,
    solution,
    solution_feedback,
    response,
    response_feedback,
    chat_path_component,
    filename,
    date_postfix,
):
    """Save chat messages to a JSON file."""

    messages_path = chat_path_component / f"{filename}_{date_postfix}_feedback.json"
    messages_path.touch()

    json.dump(
        {
            "solution": solution,
            "solution_feedback": solution_feedback,
            "solution_messages": {
                "usage": response.usage.to_dict(),
                "messages": messages,
            },
            "feedback_messages": {
                "usage": response_feedback.usage.to_dict(),
                "messages": messages_feedback,
            },
        },
        messages_path.open("w"),
        indent=4,
    )


def save_chat_text(
    messages,
    chat_path_component,
    filename,
    date_postfix,
    is_feedback=False,
):
    """Save chat messages to a Text file."""

    if is_feedback:
        messages_path = chat_path_component / f"{filename}_{date_postfix}_feedback.txt"
    else:
        messages_path = chat_path_component / f"{filename}_{date_postfix}.txt"

    messages_path.touch()

    text = ""

    for m in messages:
        text += m["role"]
        text += "\n"
        text += "--" * 30
        text += "\n"
        text += "\n"
        if isinstance(m["content"], list):
            for i in m["content"]:
                if i.get("text") is not None:
                    text += i["text"]
        else:
            text += m["content"]
        text += "\n\n\n" + "##" * 50 + "\n\n\n"

    messages_path.write_text(text)
