from .parse import build_docs
if __name__ == "__main__":
    p = build_docs()
    print("Docs written to", p)
