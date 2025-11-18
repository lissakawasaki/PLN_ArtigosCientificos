from PyPDF2 import PdfReader
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk
import re
import string

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

nltk.download('punkt')
nltk.download('stopwords')

FILE_PATHS = [
    'articles/3D Medical Imaging by using Point Cloud Generation.pdf',
    'articles/A Gated Review Attention Framework for Topics in Graph-Based Recommenders.pdf',
    'articles/A Zero-Shot Prompting Approach for Automated Feedback Generation on ENEM Essays.pdf',
    'articles/ClearFace Facial Acne Detection and Classification System Using YOLOv11 and EfficientNet-B0.pdf',
    'articles/Multi-Pathology Segmentation of the Lumbar Spine.pdf',
    'articles/Socially Responsible and Explainable Automated Fact-Checking and Hate Speech Detection.pdf',
    'articles/Superpixel Segmentation Effect on Hierarchical GNN applied to Image Classification.pdf',
    'articles/Symmetry Shape Analysis.pdf',
    'articles/The Flow of Creation A Tour of Flow Matching for Visuals.pdf',
    'articles/When Art meets Computer Science a systematic review about technologies and user interaction in adaptive digital museums and archives.pdf'
]

class AnalisadorArtigo:
    def __init__(self):
        self.stop_words = set(stopwords.words('english')).union(stopwords.words('portuguese'))
        self.stop_words = self.stop_words.union(set(string.punctuation))
        

        self.stop_markers = [
            "appendix", "apêndice", "acknowledgements", "agradecimentos", 
            "a tables of the top", "a.1 letterboxd rating top 10" 
        ]

    def extract_text_lowercase(self, file_path):
        all_text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado: {file_path}")
            return ""

        all_text = all_text.replace('\r\n', '\n').replace('\r', '\n')
        all_text = re.sub(r'\n\s*\n+', '\n\n', all_text)
        return all_text.strip().lower()

    def split_paragraphs(self, text):
        if not text:
            return []
        
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        cleaned = []
        for p in raw_paragraphs:
            p2 = re.sub(r'\n+', ' ', p).strip()
            if len(p2) >= 40: # evita lixo muito curto
                cleaned.append(p2)
        return cleaned

    def get_top_10_terms(self, all_text):
        raw_tokens = re.split(r'[^a-z]+', all_text.lower())
        
        token_texts = [
            token for token in raw_tokens
            if token and token.isalpha() and token not in self.stop_words
        ]

        frequency = {}
        for token in token_texts:
            frequency[token] = frequency.get(token, 0) + 1

        return sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def extract_reference(self, all_text): 
        pos = all_text.lower().find("references") 
        if pos == -1: 
            return [] 
        
        ref_text = all_text[pos + len("references"):].strip() 
        matches = list(re.finditer(r"\[(\d+)\]", ref_text)) 
        referencias = [] 
        
        for i, m in enumerate(matches): 
            start = m.start() 
            if i + 1 < len(matches): 
                end = matches[i + 1].start() 
            else: 
                end = len(ref_text) 

            bloco = ref_text[start:end].strip() 
            if bloco: 
                referencias.append(bloco) 
        
        return referencias

    def relevant_paragraphs(self, all_text, top_k_each=1):
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
        if not text: return ""

        try:
            parser = PlaintextParser.from_string(text, Tokenizer("english")) 
            summarizer = TextRankSummarizer()
            summary_sentences = summarizer(parser.document, num_sentences)
            summary_text = " ".join([str(s) for s in summary_sentences])
            return summary_text
        except Exception:
            sentences = sent_tokenize(text)
            return " ".join(sentences[:num_sentences])


def format_paragraph(text, width=90, indent="    "):
    """Formata o texto para quebras de linha em uma largura específica e adiciona indentação."""
    palavras = text.split()
    linhas = []
    linha = []
    
    for palavra in palavras:
        # Verifica se adicionar a próxima palavra excede a largura
        if len(" ".join(linha + [palavra])) > width and linha:
            linhas.append(" ".join(linha))
            linha = [palavra]
        else:
            linha.append(palavra)
            
    if linha:
        linhas.append(" ".join(linha))

    return "\n".join(indent + l for l in linhas)


def analyze_articles(file_paths):
    analyzer = AnalisadorArtigo()
    analysis_results = []
    
    for path in file_paths:
        print(f"Analisando: {path}")
        all_text = analyzer.extract_text_lowercase(path)
        
        if not all_text:
            analysis_results.append({'Article': path, 'Error': 'File not processed'})
            continue

        top_terms = analyzer.get_top_10_terms(all_text)
        references = analyzer.extract_reference(all_text)
        relevant_paras = analyzer.relevant_paragraphs(all_text)
        summary = analyzer.generate_summary(all_text, num_sentences=6)
        
        analysis_results.append({
            'Article': path,
            'Top10_Terms': top_terms,
            'References_Extracted_Count': len(references),
            'References': references, 
            'Relevant_Paragraphs': relevant_paras,
            'Summary': summary
        })
        
    return analysis_results

def export_results_to_txt(results, filename="analise_resultados.txt"):
    """Salva os resultados obtidos em um arquivo de texto, mostrando todas as referências e formatando o resumo."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("========================================================\n")
        f.write("      ANÁLISE AUTOMÁTICA DE ARTIGOS CIENTÍFICOS\n")
        f.write("========================================================\n\n")
        
        for result in results:
            if 'Error' in result:
                f.write(f"--- ARTIGO: {result['Article']} ---\n")
                f.write(f"ERRO: {result['Error']}\n")
                f.write("\n" + "="*50 + "\n\n")
                continue

            f.write(f"--- ARTIGO: {result['Article']} ---\n\n")
            
            # 1. Top 10 Termos
            f.write("1. TOP 10 TERMOS:\n")
            for term, count in result['Top10_Terms']:
                f.write(f"    - {term:<15}: {count}\n")
            f.write("\n")
            

            f.write(f"2. REFERÊNCIAS EXTRAÍDAS ({result['References_Extracted_Count']} total):\n")
            if not result['References']:
                 f.write("    Nenhuma referência encontrada ou padrão não detectado.\n")
            else:
                for i, ref in enumerate(result['References'], 1):
                    f.write(f"    [{i}] {format_paragraph(ref, indent='')}\n")
            f.write("\n")
            
            f.write("3. PARÁGRAFOS RELEVANTES (TOP-1):\n")
            for tag, paras in result['Relevant_Paragraphs'].items():
                f.write(f"  > {tag.upper()}:\n")
                if paras:
                    score, para_text = paras[0]
                    formatted_text = format_paragraph(para_text, width=130, indent="        ")
                    f.write(f"    Score: {score:.3f}\n{formatted_text}\n")
                else:
                    f.write("    Não encontrado.\n")
            f.write("\n")

            f.write("4. RESUMO GERAL:\n")
            f.write(format_paragraph(result['Summary'], width=80, indent="    ") + "\n")
            f.write("\n" + "="*50 + "\n\n")
    
    print(f"\nResultados salvos em '{filename}'")


def main():

    results = analyze_articles(FILE_PATHS)
    export_results_to_txt(results)
    
if __name__ == "__main__":
    main()