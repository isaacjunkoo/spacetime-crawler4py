from collections import defaultdict
import re
import sys
def tokenize(textfile) -> list:
    tokens, token = [], ""
    try:
        with open(textfile, encoding='utf-8', errors="ignore") as file:
            while True:
                character = file.read(1).lower()  # read byte by byte to avoid using RAM
                if not re.match("[a-zA-Z0-9]", character) or character in [" ", "\n"]:
                    if token:
                        tokens.append(token)
                    token = ""

                if re.match("[a-zA-Z0-9]", character) and character != " ":
                    token += character

                if not character:  # end of file
                    if token:
                        tokens.append(token)
                    break

            return tokens

    except FileExistsError:
        print(f"{textfile} doesn't exist. Try another one.")
        sys.exit()

    except FileNotFoundError:
        print(f"{textfile} not found. Try another one.")
        sys.exit()

    except UnicodeDecodeError:
        print(f"Cannot open {textfile} because this is a non-text file.")
        sys.exit()


def compute_word_frequencies(tokens: list) -> dict:
    frequencies = defaultdict(int)
    try:
        for token in tokens:
            frequencies[token] += 1
        return frequencies
    except TypeError:
        print("Error: empty list of tokens")


def print_res(frequencies: dict):
    try:
        res = sorted([pair for pair in sorted([x for x in frequencies.items()], key=lambda x: x[0])], key=lambda x: x[1], reverse=True)
        for k, v in res:
            print(f'{k} = {v}')
    except AttributeError:
        print("Error: dictionary doesn't exist")


if __name__ == '__main__':
    pass