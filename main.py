from PyPDF2 import PdfReader
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

stop_words = [
    "a", "an", "and", "the", "but", "or", "because", "as", "until", "while", 
    "of", "at", "by", "for", "with", "about", "against", "between", "into", 
    "through", "during", "before", "after", "above", "below", "to", "from", 
    "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", 
    "then", "once", "here", "there", "when", "where", "why", "how", "all", 
    "any", "both", "each", "few", "more", "most", "other", "some", "such", 
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", 
    "s", "t", "can", "will", "just", "don", "should", "now",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", 
    "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", 
    "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", 
    "their", "theirs", "themselves", "what", "which", "who", "whom", "this", 
    "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", 
    "being", "have", "has", "had", "having", "do", "does", "did", "doing"
]

def extract_text_lowercase():
    all_text = ""
    with open('sample-local-pdf.pdf', 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text += text.lower() + " "
    return all_text


all_text = extract_text_lowercase()
token_words = word_tokenize(all_text)

token_texts = []
for token in token_words:
    token_lower = token.lower()
    if token_lower not in stop_words and token_lower.isalpha():
        token_texts.append(token_lower)

frequency = {}
for token in token_texts:
    if token in frequency:
        frequency[token] += 1
    else:
        frequency[token] = 1

ordened_list = sorted(frequency.items(), key=lambda x: x[1], reverse=True)

print(ordened_list)