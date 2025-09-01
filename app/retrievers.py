import os

BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data")

def _load_docs_from_folder(folder: str):
    docs = []
    folder_path = os.path.abspath(os.path.join(BASE_PATH, folder))
    if not os.path.exists(folder_path):
        return docs
    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)
        if os.path.isfile(fpath) and fname.endswith(".txt"):
            with open(fpath, "r", encoding="utf-8") as f:
                docs.append(f.read())
    return docs

def get_billing_docs():
    return _load_docs_from_folder("billing_docs")

def get_technical_docs():
    return _load_docs_from_folder("technical_docs")

def get_security_docs():
    return _load_docs_from_folder("security_docs")

def get_general_docs():
    return _load_docs_from_folder("general_docs")

CATEGORY_TO_RETRIEVER = {
    "Billing": get_billing_docs,
    "Technical": get_technical_docs,
    "Security": get_security_docs,
    "General": get_general_docs,
}
