from fuzzywuzzy import fuzz


def compare_fingerprints(fingerprint1, fingerprint2):
    similarity_ratio = fuzz.ratio(fingerprint1, fingerprint2)
    print(f"Similarity ratio between fingerprints: {similarity_ratio}%")


# Assuming you have assigned fingerprints to two texts


# Compare the texts using their fingerprint values
if __name__ == "__main__":
    text1 = "testing to see if this is good"
    text2 = "testing to see if this is great"
    fingerprint1 = fuzz.FuzzyWuzzy().fuzz(text1)
    fingerprint2 = fuzz.FuzzyWuzzy().fuzz(text2)
    compare_fingerprints(fingerprint1, fingerprint2)
