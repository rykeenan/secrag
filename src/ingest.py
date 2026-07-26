from pathlib import Path    # modern file-path handling
from pypdf import PdfReader # PDF text extraction
from bs4 import BeautifulSoup # HTML parsing
import re # regular expression, for whitespace cleanup

def clean_text(text):
    """Normalize whitespace: collapse space runs and blank-line runs."""
    text = re.sub(r"[ \t]+", " ", text)  #runs of spaces/tabs -> one spcae 
    text = re.sub(r"\n\s*\n", "\n\n", text) # runs of blank lines -> one blank line
    return text.strip()

def extract_pdf(path):
    """Read a PDF and return all its text as one string."""
    reader = PdfReader(path)    # open the PDF file
    pages = []                  # will hold each page's text
    for page in reader.pages:   # loop over every page
        text = page.extract_text() # pull the text off this page
        if text:                   # some pages are images/blank -> None
            pages.append(text)
    return clean_text("\n".join(pages))        # glue pages into one string

def extract_html(path):
    """ Read an HTML file and return its visible text, minus site chrome."""
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["nav", "header", "footer", "script", "style"]):
        tag.decompose()     # delete this tag + everything inside it

    main = soup.find("main")    # many sites wrap real content in <main>
    target = main if main else soup  # use <main> if it exists, else whole page 

    return clean_text(target.get_text(separator="\n"))


def ingest(folder="data/raw"):
    """Read every PDF/HTML in the folder -> list of document dicts."""
    docs = []                                         # collector
    for path in sorted(Path(folder).iterdir()):       # every file, alphabetical
        print(f"Processing: {path.name}")
        if path.suffix == ".pdf":
            text = extract_pdf(path)
        elif path.suffix == ".html":
            text = extract_html(path)
        else:
            continue                                 # skip anything else
        docs.append({
            "source": path.stem,                     # filename minus extension
            "format": path.suffix[1:],               # ".pdf" -> "pdf"
            "text": text,
        })
    return docs

if __name__ == "__main__":                        # runs only via: python src\ingest.py
    docs = ingest()
    print(f"Ingested {len(docs)} documents\n")
    
    for d in docs:   # Job 1: the summary table
        print(f"{d['source']:40} {d['format']:5} {len(d['text']):>8} chars")

    for d in docs:
        if d["source"] == "mitre_t1566":
            print("\n--- First 300 chars of mitre_t1566 ---")
            print(d["text"][:300])