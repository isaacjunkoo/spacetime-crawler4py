import sys
import builtins
import re as regex


def tokenize(TextFilePath):
    stop_words = set()
    stopWordsFile = open("stop_words.txt", "r", encoding="utf-8")
    for line in stopWordsFile:
        stop_words.add(line)
    stopWordsFile.close()
    # O(nm), where n is the amount of lines in a text
    # and m is the amount of terms (delimited by ' ') in each line

    allWords = []  # for constant time incrementation/detection of words, use hashmap
    try:
        # open in utf8 to avoid character discrepancies, remove errors
        file = open(TextFilePath, "r", errors='replace', encoding='utf-8')
        for i in file:  # each line in file
            alphaNumOnly = i.lower()
            # replace all non-alphanum characters with ''
            alphaNumOnly = regex.sub('[^A-Za-z0-9\s]', '', alphaNumOnly)
            # remove consecutive whitespaces for split
            alphaNumOnly = regex.sub(' +', ' ', alphaNumOnly)
            alphaNumOnly = alphaNumOnly.strip()  # remove the newline and trailing spaces
            alphaNumOnlyList = alphaNumOnly.split(" ")

            # builtins.print("LINE: " + alphaNumOnly)
            if len(alphaNumOnlyList) == 1 and '' in alphaNumOnlyList:
                # split(" "), on empty strings, yields '' so remove it.
                alphaNumOnlyList.remove('')
            for j in alphaNumOnlyList:
                # place in map for O(1) lookup and placement
                allWords.append(j)
        file.close()
        return allWords
    except FileNotFoundError:
        builtins.print("Invalid file path.")
        return []  # in case file dne
    except UnicodeDecodeError:
        builtins.print("Bad character detected")
        return []
        # should never be possible with errors='replace'


def computeWordFrequencies(listOfTokens):
    # O(n) where n is the amount of tokens in the text
    # sometimes smaller than the actual amount of words in a text because many things can be filtered out
    wordCounts = dict()
    for i in listOfTokens:  # loop through all tokens
        if i in wordCounts:
            wordCounts[i] += 1  # add to word in hashmap
        else:
            wordCounts[i] = 1  # initialize word in hashmap
    return wordCounts  # dict


def print(frequencies):
    # O(n) where n is the amount of words in the text.
    # Worst case, all words are unique resulting in the size being the amount of words in the text.
    # The time improves when words are not unique
    # x:(-x[1], x[0]) creates a key-value
    sortedDescending = sorted(frequencies.items(), key=lambda x: (-x[1], x[0]))
    # tuple that sorts by giving priority to most frequent words x[1] and orders alphabetically x[0] which is a 2nd priorityy
    for word, count in sortedDescending:
        builtins.print(word, count)


if __name__ == "__main__":
    try:
        tokens = tokenize(sys.argv[1])
        frequencies = computeWordFrequencies(tokens)
        print(frequencies)
    except IndexError:
        builtins.print("File path not specified.")
