from PyPDF2 import PdfReader
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import re

nltk.download('punkt')
nltk.download('stopwords')

class AnalisadorArtigo:
    def __init__(self):
        self.stop_words = set(stopwords.words('english')).union(stopwords.words('portuguese'))
       
    def extract_text_lowercase(self, file_path):
        all_text = ""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text += text.lower() + "\n"
        return all_text
    
    def get_top_10_terms(self, all_text):
        token_words = word_tokenize(all_text)
        token_texts = []
        for token in token_words:
            if token not in self.stop_words and token.isalpha():
                token_texts.append(token)
        
        frequency = {}
        for token in token_texts:
            if token in frequency:
                frequency[token] += 1
            else:
                frequency[token] = 1
        
        return sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def extract_reference(self, all_text):
        pos = all_text.lower().find("references")
        if pos == -1:
            return []

        ref_text = all_text[pos:]

        # encontrar todas as ocorrências de [n]
        matches = list(re.finditer(r"\[(\d+)\]", ref_text))

        referencias = []

        for i, m in enumerate(matches):
            start = m.start()

            # pega o texto até o próximo [n]
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(ref_text)

            bloco = ref_text[start:end].strip()

            if any(keyword in bloco for keyword in ["doi", "20", "19", ".com", ".org"]):
                referencias.append(bloco)

        return referencias




def main():
    analisador = AnalisadorArtigo()
    all_text = analisador.extract_text_lowercase(
        'Behind the Stars Uncovering Hidden Adjustments in Letterboxd Film Ratings.pdf')

    print("\n===== TOP 10 TERMOS =====")
    for term, count in analisador.get_top_10_terms(all_text):
        print(f"{term}: {count}")

    print("\n===== REFERÊNCIAS EXTRAÍDAS =====")
    referencias = analisador.extract_reference(all_text)
    for i, ref in enumerate(referencias, 1):
        print(f"{i}. {ref}\n")


if __name__ == "__main__":
    main()
