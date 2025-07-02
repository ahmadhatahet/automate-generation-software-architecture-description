import io
import base64
from PIL import Image


SYSTEM_PROMPT = [
    {
        "role": "system",
        "content": """<Role>
You are an expert software engineer.
</Role>
<Goal>
Generate a state machine diagram for the c++ code in plantuml format.
</Goal>

<Solution Plan>
1. Understand the source code
2. Extract the candidate states
3. Provide small and summarized description of each state
4. Extract the transition from one state to another
5. What is the trigger that triggered the transition
6. Review the examples and how their corresponding state diagram
7. Construct the state diagram for the passed code
8. Review the order of the states based on normal logic and using the examples
</Solution Plan>""",
    }
]


def user_message(cpp_files):
    """Create user prompt for the target cpp by providing a list of Paths to the cpp files."""

    cpp_text = ""
    for f in cpp_files:
        cpp_text += f"<File {f.name}>:\n```\n{f.read_text()}\n```\n</File {f.name}>\n"

    message = [
        {
            "role": "user",
            "content": f"# Generate a state machine  for the following code:\n{cpp_text}",
        }
    ]

    return message


def example_message(cpp_files, image_file):
    """Create User-Assistant simulated interaction to pass the general Examples."""

    if not image_file.is_file() or len(cpp_files) == 0:
        raise ValueError("Image file and cpp files must be provided.")

    cpp_text = ""
    for f in cpp_files:
        cpp_text += f"<File {f.name}>:\n```\n{f.read_text()}\n```\n</File {f.name}>\n"

    # Save to an in-memory buffer
    buffered = io.BytesIO()
    # Convert the resized image to bytes and then to Base64
    scale_image_to_fit(image_file, 800).save(buffered, format="PNG")
    img_byte_array = buffered.getvalue()
    image_data = base64.b64encode(img_byte_array).decode("utf-8")
    buffered.close()


    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"<Example>\n# Here is the a C++ code file(s):\n{cpp_text}"
                    + "# Here is the state machine as an image\n",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}",
                    },
                },
            ],
        }
    ]


def scale_image_to_fit(image_path: str, max_width: int = None):
    """
    Scales an image down to fit either a maximum width,
    without losing the aspect ratio.

    Args:
        image_path (str): The path to the input image file.
        max_width (int, optional): The maximum desired width for the image.
                                    If the original width is larger, it will be scaled down.
    """
    if max_width is None and max_height is None:
        raise ValueError("At least one of max_width or max_height must be provided.")

    # Open the image
    img = Image.open(image_path)
    original_width, original_height = img.size

    scaling_ratio = 1.0

    if max_width is not None and original_width > max_width:
        scaling_ratio = max_width / original_width

    # If no scaling is needed, keep the original size.
    if scaling_ratio >= 1.0:
        return img

    # Calculate new dimensions
    new_width = int(original_width * scaling_ratio)
    new_height = int(original_height * scaling_ratio)

    # Resize the image using LANCZOS filter for high-quality downscaling
    scaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return scaled_img



def feedback_message(solution, cpp_files):

    cpp_text = ""
    for f in cpp_files:
        cpp_text += f"<File {f.name}>:\n```\n{f.read_text()}\n```\n</File {f.name}>\n"

    # feedback messages
    messages_feedback = [
        {
            "role": "system",
            "content": (
                "<Role>You are an expert software engineer specializing in constructing state diagrams from source code and reviewing them.</Role>"
                + "<Goal>You are responsible to review a state diagram served to you in plantuml format and c++ source code of the represented diagram to fix any state name, transition event, or assess the availability of parallel state</Goal>"
            ),
        },
        {
            "role": "user",
            "content": (
                f"# Here the is state diagram:\n<State Diagram>\n```\n{solution}\n```\n</State Diagram>\n\n"
                + f"# Here is the source code:```\n{cpp_text}\n```"
            ),
        },
    ]

    return messages_feedback