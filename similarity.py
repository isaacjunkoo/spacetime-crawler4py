from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import nltk


def calculate_similarity(text1, text2):
    # Tokenize the texts
    tokens1 = word_tokenize(text1)
    tokens2 = word_tokenize(text2)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens1 = [
        word for word in tokens1 if word.lower() not in stop_words]
    filtered_tokens2 = [
        word for word in tokens2 if word.lower() not in stop_words]

    # Calculate frequency of words
    freq_dist1 = nltk.FreqDist(filtered_tokens1)
    freq_dist2 = nltk.FreqDist(filtered_tokens2)

    # Create vectors for the frequency distribution of words
    vector1 = []
    vector2 = []
    all_words = set(filtered_tokens1 + filtered_tokens2)

    for word in all_words:
        vector1.append(freq_dist1[word])
        vector2.append(freq_dist2[word])

    # Calculate the cosine similarity between the vectors
    similarity = cosine_similarity([vector1], [vector2])[0][0]
    return similarity


# Example usage
text1 = "Hello, how are you doing today?"
text2 = "Hola, how are you doing?"
similarity_score = calculate_similarity(text1, text2)
print(f"The similarity score is: {similarity_score}")
