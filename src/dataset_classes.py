from dataclasses import dataclass
from pathlib import Path

from enums import InstanceCategory, ErrorType
import re


@dataclass
class DatasetInstance:
    # metadata
    file_path: Path
    category: InstanceCategory
    id: int

    # file contents
    metadata: [str]  # list of lines that contain metadata (start of the file)
    problem_description: str  # the problem description in natural language
    input_data: str  # optional, the input data (between # Data and # End of data)
    full_content: str  # the CP model

    def get_prompt(self):
        prompt = self.problem_description
        if self.input_data:
            prompt += f"\n### Input data: \n{self.input_data}\n### End of input data\n"
        return prompt

    def get_content_after_description(self, wrapped=True):
        # Find the first occurrence of the multi-line comment
        multi_line_comment_pattern = re.compile(r'"""(.*?)\s*"""|\'\'\'(.*?)\s*\'\'\'', re.DOTALL)
        match = multi_line_comment_pattern.search(self.full_content)

        if match:
            # Extract the comment content
            content_after_description = self.full_content[match.end():].strip()
        else:
            raise ValueError("Content after description not found in the script content")

        if wrapped:
            return f'```python\n{content_after_description}\n```\n'
        return content_after_description



@dataclass
class SelfDebugStep:
    messages: []
    output: str
    error_type: ErrorType
    prompt_tokens: int
    completion_tokens: int

    def __init__(self):
        self.messages = []
        self.output = ""
        self.error_type = None
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def to_dict(self):
        return {
            "messages": self.messages,
            "output": self.output,
            "error_type": self.error_type.name if self.error_type else None,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens
        }


@dataclass
class LogInstance:
    instance: DatasetInstance
    answer: str
    error_type: ErrorType
    initial_messages: []
    samples: []
    self_debug_history: [SelfDebugStep]
    total_prompt_tokens: int
    total_completion_tokens: int

    # add constructor
    def __init__(self, instance: DatasetInstance):
        self.instance = instance
        self.answer = ""
        self.initial_messages = []
        self.samples = []
        self.self_debug_history = []
        self.error_type = None
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
