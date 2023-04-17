"""
* This script is used to convert the .env file to a string
* Place the script in the same directory as the .env file
"""


def skip_empty_or_hashtag_lines(line):
    if "#" in line:
        return True
    if len(line) < 4:
        return True
    return False


def env_file_to_string():
    file = open(".env", "r")
    lines_of_file = file.readlines()
    env_var_as_string = ""
    for line in lines_of_file:
        if skip_empty_or_hashtag_lines(line):
            pass
        else:
            env_var_as_string += f"{line.rstrip()},"

    return env_var_as_string[:-1]


if "__main__" == __name__:
    print(env_file_to_string())
