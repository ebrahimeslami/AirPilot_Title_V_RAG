from .index import build_index
if __name__ == "__main__":
    print("Building index...")
    p = build_index()
    print("Index at", p)
