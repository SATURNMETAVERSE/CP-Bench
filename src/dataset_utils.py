import re
from pathlib import Path

from dataset_classes import DatasetInstance
from enums import InstanceCategory


def parse_single_file(file_path: Path, instance_id: int) -> DatasetInstance:
    # read the file, with encoding utf-8
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # extract metadata: all non-empty lines until the first multi-line comment
    metadata = []
    i = 0
    while i < len(lines) and not lines[i].startswith('"""'):
        metadata.append(lines[i].strip())
        i += 1

    # extract problem description: In the first multi-line comment.
    # Use regex to find the first multi-line comment
    multi_line_comment_pattern = re.compile(r'"""(.*?)\s*"""|\'\'\'(.*?)\s*\'\'\'', re.DOTALL)
    match = multi_line_comment_pattern.search("".join(lines))

    if match:
        # Extract the comment content
        problem_description = match.group(0).strip('"""').strip("'''").strip()
    else:
        raise ValueError("Problem description not found in the script content")

    # Input Data: between # Data and # End of data
    # Use regex to find the input data
    input_data_pattern = re.compile(r'# Data(.*?)# End of data', re.DOTALL)
    match = input_data_pattern.search("".join(lines))

    if match:
        # Extract the input data
        input_data = match.group(1).strip()
    else:
        input_data = ""

    # full content: the entire file
    full_content = "".join(lines)

    # category: based on the parent directory of the file
    parent_dir = Path(file_path).parent
    if parent_dir.name == "aplai_course":
        category = InstanceCategory.APLAI
    elif parent_dir.name == "complex_or":
        category = InstanceCategory.COMPLEX_OR
    elif parent_dir.name == "cpmpy_examples":
        category = InstanceCategory.CPMPY_EXAMPLES
    elif parent_dir.name == "csplib":
        category = InstanceCategory.CSPLIB
    elif parent_dir.name == "hakan_examples":
        category = InstanceCategory.HAKANK_EXAMPLES
    else:
        raise ValueError(f"Unknown category for {file_path}. Check the parent directory name.")

    return DatasetInstance(file_path=file_path, category=category, id=instance_id, metadata=metadata,
                           problem_description=problem_description, input_data=input_data, full_content=full_content)


def load_dataset(dataset_path: str = "dataset") -> [DatasetInstance]:
    dataset = []
    for idx, file in enumerate(Path(dataset_path).rglob("*.py")):
        try:
            instance = parse_single_file(file, idx)
            dataset.append(instance)
        except Exception as e:
            print(f"Error processing {file}: {e}")
    print(f"Loaded {len(dataset)} instances.")
    return dataset
