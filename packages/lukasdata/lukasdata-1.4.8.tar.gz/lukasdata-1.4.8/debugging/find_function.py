

import os
def find_function_usage_in_file(file_path, function_name):
    """
    Searches for the usage of a function in a single file.
    
    :param file_path: Path to the Python file.
    :param function_name: Name of the function to search for.
    :return: A list of lines where the function is used.
    """
    usages = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line_number, line in enumerate(lines, start=1):
            if function_name in line and not line.strip().startswith("#"):  # Ignore commented lines
                usages.append((line_number, line.strip()))
    return usages

def find_function_usage_in_folder(folder_path, function_name):
    """
    Searches for the usage of a function in all Python files within a folder.
    
    :param folder_path: Path to the folder containing Python modules.
    :param function_name: Name of the function to search for.
    :return: A dictionary where the keys are file paths and values are lists of lines where the function is used.
    """
    function_usages = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                usages = find_function_usage_in_file(file_path, function_name)
                if usages:
                    function_usages[file_path] = usages

    if function_usages:
        for file, lines in function_usages.items():
            print(f'Function "{function_name}" is used in {file}:')
            for line_number, line in lines:
                print(f'  Line {line_number}: {line}')
    else:
        print(f'Function "{function_name}" is not used in any files within the folder.')
    return function_usages


bachelor_path=r"C:\Users\lukas\Documents\GitHub\bachelor"

usages = find_function_usage_in_folder(bachelor_path,"iterate_list")
usages = find_function_usage_in_folder(bachelor_path,"array_generator")

