import os
import shutil

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CATEGORY_DIRS = {
    "Billing": "billing_docs",
    "Technical": "technical_docs",
    "Security": "security_docs",
    "General": "general_docs",
}

def ingest_file(src_path: str, category: str):
    """Copy a file into the right category folder."""
    if category not in CATEGORY_DIRS:
        raise ValueError(f"Invalid category: {category}")
    dest_dir = os.path.join(DATA_DIR, CATEGORY_DIRS[category])
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, os.path.basename(src_path))
    shutil.copy(src_path, dest_path)
    print(f"Ingested {src_path} → {dest_path}")

def ingest_demo():
    """Demo: create a few mock docs."""
    for category, folder in CATEGORY_DIRS.items():
        path = os.path.join(DATA_DIR, folder)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, f"{category.lower()}_example.txt"), "w", encoding="utf-8") as f:
            f.write(f"This is a {category} example document for retrieval.")

if __name__ == "__main__":
    ingest_demo()
    print("✅ Demo ingestion complete. Check data/ folders.")
