from PyPDF2 import PdfReader
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import re
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

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
    with open('Behind the Stars Uncovering Hidden Adjustments in Letterboxd Film Ratings.pdf', 'rb') as file:
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

print("\n=== ORNEDED TOKENS ===\n")
print(ordened_list)

reference_index = all_text.find('references')
if reference_index == -1:
    print("Section was not found.")
    exit()

references_text = all_text[reference_index:]
references_lines = references_text.split("\n")

references = []
current_ref = ""

pattern = re.compile(r"^\[\d+\]")  

lines_without_ref = 0
MAX_EMPTY = 10  

for line in references_lines:
    line = line.strip()

    if pattern.match(line):
        lines_without_ref = 0 
        if current_ref:
            references.append(current_ref.strip())
        current_ref = line

    else:
        if current_ref:
            current_ref += " " + line

        lines_without_ref += 1
        if lines_without_ref >= MAX_EMPTY:
            break

if current_ref:
    references.append(current_ref.strip())

print("\n=== REFERENCES ===\n")
for ref in references:
    print(ref, "\n")


def split_paragraphs(text):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs

topics = {
    "objetivo": ["abstract", "goal", "aim", "purpose", "objective", "we propose", "this paper proposes"],
    "palavras-chave": ["keywords", "key words", "index terms"],
    "problema": ["problem", "challenge", "issue", "limitations", "gap"],
    "contribuição": ["contribution", "novel", "we present", "we introduce", "main contribution"]
}

paragraphs = split_paragraphs(all_text)

def find_relevant_paragraphs(paragraphs, topics):
    results = {k: [] for k in topics}

    for p in paragraphs:
        p_lower = p.lower()
        for topic, keywords in topics.items():
            for kw in keywords:
                if kw in p_lower:
                    results[topic].append(p)
                    break

    return results

relevant_paragraphs = find_relevant_paragraphs(paragraphs, topics)

def summarize_text(text, max_tokens=1000):
    text = text[:4000] 
    summary = summarizer(text, max_length=200, min_length=80, do_sample=False)
    return summary[0]['summary_text']

print("\n=== RELEVANT PARAGRAPHS ===\n")
for topic, paras in relevant.items():
    print(f"\n--- {topic.upper()} ---\n")
    for p in paras:
        print(p)
        print()

print("\n=== SUMARY ===\n")
print(summarize_text(all_text))
