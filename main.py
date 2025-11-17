from PyPDF2 import PdfReader
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk
import re
import numpy as np
from math import log
from nltk.stem import PorterStemmer
import string

nltk.download('punkt')
nltk.download('stopwords')

class AnalisadorArtigo:
    def __init__(self):
        self.stop_words = set(stopwords.words('english')).union(stopwords.words('portuguese'))
        self.stop_words = self.stop_words.union(string.punctuation)
        self.stemmer = PorterStemmer()

    def extract_text_lowercase(self, file_path):
        all_text = ""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                try:
                    text = page.extract_text()
                except Exception:
                    text = None
                if text:
                    all_text += text + "\n"

        all_text = all_text.replace('\r\n', '\n').replace('\r', '\n')

        all_text = re.sub(r'\n\s*\n+', '\n\n', all_text)

        all_text = all_text.strip().lower()
        return all_text

    def split_paragraphs(self, text):
        if not text:
            return []

        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'\n\s*\n+', '\n\n', text)

        raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        cleaned = []
        for p in raw_paragraphs:
            p2 = re.sub(r'\n+', ' ', p).strip()
            if len(p2) >= 40:  # evita lixo muito curto
                cleaned.append(p2)

        if len(cleaned) > 1:
            return cleaned

        sentences = sent_tokenize(text) #fallback
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if not sentences:
            return cleaned  

        N = 5  
        pseudo = []
        for i in range(0, len(sentences), N):
            group = " ".join(sentences[i:i+N])
            if len(group) >= 40:
                pseudo.append(group)

        if len(pseudo) == 1:
            longp = pseudo[0]
            if len(longp) > 2000:
                mid = len(longp) // 2
                cut = longp.rfind('.', 0, mid)
                if cut == -1:
                    cut = mid
                a = longp[:cut+1].strip()
                b = longp[cut+1:].strip()
                pseudo = [p for p in [a, b] if len(p) > 40]

        return pseudo if pseudo else cleaned

    def get_top_10_terms(self, all_text):
        token_words = word_tokenize(all_text)
        token_texts = [
            token for token in token_words
            if token.isalpha() and token not in self.stop_words
        ]

        frequency = {}
        for token in token_texts:
            frequency[token] = frequency.get(token, 0) + 1

        return sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def extract_reference(self, all_text): 
        pos = all_text.lower().find("references") 
        if pos == -1: 
            return [] 
        
        ref_text = all_text[pos:] 
        matches = list(re.finditer(r"\[(\d+)\]", ref_text)) 
        referencias = [] 
        for i, m in enumerate(matches): 

            start = m.start() 
            if i + 1 < len(matches): 
                end = matches[i + 1].start() 
            else: end = len(ref_text) 

            bloco = ref_text[start:end].strip() 
            if any(k in bloco for k in ["doi", ".com", ".org", "20", "19"]): 
                referencias.append(bloco) 
        
        return referencias


    def relevant_paragraphs(self, all_text, top_k_each=3):
        paragraphs = self.split_paragraphs(all_text)

        TAGS = {
            "objetivo": ["objective", "aim", "purpose", "goal", "objetivo", "propósito", "we aim", "the objective"],
            "palavras-chaves": ["keywords", "palavras-chave", "key words", "index terms"],
            "problema": ["problem", "issue", "challenge", "problema", "we address", "we tackle"],
            "contribuição": ["contribution", "novelty", "innovation", "contribuição", "we propose", "we present"]
        }

        results = {tag: [] for tag in TAGS}

        for p in paragraphs:
            p_clean = p.lower()

            for tag, keywords in TAGS.items():
                matches = 0
                for kw in keywords:
                    if re.search(rf"\b{re.escape(kw)}\b", p_clean):
                        matches += 1

                density = matches / (len(p_clean.split()) + 1)

                if matches >= 2 or (matches == 1 and density > 0.002):
                    score = matches + density
                    results[tag].append((score, p))

        for tag in results:
            results[tag] = sorted(results[tag], key=lambda x: -x[0])[:top_k_each]

        return results

    def generate_summary(self, text, num_sentences=6):
        sentences = sent_tokenize(text)

        clean_sentences = []
        for s in sentences:
            if len(s.split()) < 8:
                continue
            if re.search(r'\d{2,}', s):
                continue
            if '@' in s:
                continue
            if 'table' in s.lower() or 'figure' in s.lower():
                continue

            clean_sentences.append(s)

        if len(clean_sentences) <= num_sentences:
            return " ".join(clean_sentences)

        sentence_tokens = [
            [w for w in word_tokenize(s.lower()) if w.isalpha() and w not in self.stop_words]
            for s in clean_sentences
        ]

        n = len(clean_sentences)
        sim_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue

                words_i = set(sentence_tokens[i])
                words_j = set(sentence_tokens[j])

                if len(words_i) == 0 or len(words_j) == 0:
                    continue

                sim_matrix[i][j] = len(words_i.intersection(words_j)) / (
                    log(len(words_i) + 1) + log(len(words_j) + 1)
                )

        scores = np.ones(n)
        damping = 0.85

        for _ in range(50):
            for i in range(n):
                scores[i] = (1 - damping) + damping * sum(
                    sim_matrix[j][i] * scores[j] / (sim_matrix[j].sum() + 1e-6)
                    for j in range(n)
                )

        ranked = np.argsort(scores)[-num_sentences:]
        ranked = sorted(ranked)

        return " ".join(clean_sentences[i] for i in ranked)

def main():
    analisador = AnalisadorArtigo()
    file_path = 'Fingerprint Matching Using Pores Extracted with Machine Learning.pdf'
    all_text = analisador.extract_text_lowercase(file_path)

    def format_paragraph(text):
        palavras = text.split()
        linhas = []
        linha = []

        for palavra in palavras:
            linha.append(palavra)
            if len(" ".join(linha)) > 90: 
                linhas.append(" ".join(linha))
                linha = []
        if linha:
            linhas.append(" ".join(linha))

        return "\n".join("  " + l for l in linhas)


    print("\n=================== TOP 10 TERMOS ===================\n")
    for term, count in analisador.get_top_10_terms(all_text):
        print(f"{term:<20} {count}")


    print("\n=================== REFERÊNCIAS ===================\n")
    references = analisador.extract_reference(all_text)

    if not references:
        print("Nenhuma referência encontrada.")
    else:
        for i, ref in enumerate(references, 1):
            ref_cleaned = ref.replace('\n', ' ') 
            print(format_paragraph(ref_cleaned).strip())
            print() 

    print("\n=================== PARÁGRAFOS RELEVANTES ===================")

    relevantes = analisador.relevant_paragraphs(all_text)

    for categoria, lista in relevantes.items():
        print(f"\n--- {categoria.upper()} ---")

        if not lista:
            print("  Nenhum parágrafo encontrado.\n")
            continue

        for score, par in lista:
            print(f"\n  [score={score:.3f}]")
            print(format_paragraph(par))
            print()

    print("\n=================== RESUMO DO ARTIGO ===================\n")
    summary = analisador.generate_summary(all_text)
    print(format_paragraph(summary))


if __name__ == "__main__":
    main()