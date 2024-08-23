import os
import json
def dict_to_json(dict,title,directory="C:/Users/lukas/Desktop/bachelor/data"):
      os.chdir(directory)
      with open(title+".json", "w", encoding="utf-8") as outfile:
            json_file=json.dumps(dict,ensure_ascii=False)
            outfile.write(json_file)
            print(f"{title} changed")



def dict_to_json_newline(data, filename,directory):
    """
    Creates a JSON file from a dictionary where each key-value pair is on a new line.

    :param data: Dictionary to be converted to JSON.
    :param filename: Name of the JSON file to be created.
    """
    os.chdir(directory)
    with open(filename, "w", encoding="utf-8") as json_file:
        for key, value in data.items():
            json_line = json.dumps({key: value})
            json_file.write(json_line + '\n')