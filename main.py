from PyPDF2 import PdfReader #Biblioteca para manipulação de arquivos PDF
import nltk #Biblioteca para "tokentização"
nltk.download('punkt')

def extract_text_lowercase(pdf_path):
    all_text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text += text.lower()
    return all_text

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

tokens_words = word_tokenize(all_text)