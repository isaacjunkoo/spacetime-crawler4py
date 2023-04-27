
from simhash import Simhash

# JEF FOCUS ON THIS ONE


def compare_fingerprints(sim1, sim2):
    hamming_distance = sim1.distance(sim2)
    # Normalize to a similarity score between 0 and 1
    similarity_score = 1 - (hamming_distance / 64)
    print(
        f"Similarity between '{sim1}' and '{sim2}': {similarity_score}")


# Assuming you have assigned fingerprints to two texts

# Compare the texts using their fingerprint values
if __name__ == "__main__":
    text1 = "testing to see if this is great"
    text2 = "testing to see if this is great"
    simhash_value1 = Simhash(text1)
    simhash_value2 = Simhash(text2)
    print(simhash_value1, simhash_value2)
    compare_fingerprints(simhash_value1, simhash_value2)
