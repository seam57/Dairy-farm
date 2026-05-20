"""
Livestock Pro — RAG Setup
Terminal এ run করুন: python setup_rag.py
"""
import os, sys, json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from vet_knowledge import VETERINARY_KNOWLEDGE

RAG_DB_PATH = os.path.join(BASE_DIR, 'vet_rag_db.json')

def setup_rag():
    print("\n Livestock Pro RAG Setup")
    print("=" * 40)
    db = []
    for item in VETERINARY_KNOWLEDGE:
        full_text = " ".join([
            item['title'], item['animal'], item['category'],
            item['symptoms'], item['treatment'], item['prevention'],
            item['vaccine'], item['keywords']
        ]).lower()
        db.append({**item, "full_text": full_text})

    with open(RAG_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(db)} entries saved to {RAG_DB_PATH}")

    # Test
    results = search_rag("গরুর দুধ কমে গেছে", n=2)
    print(f"[Test] 'গরুর দুধ কমে গেছে' -> {[r['title'] for r in results]}")
    print("=" * 40)

def search_rag(query: str, animal_filter: str = None, n: int = 3) -> list:
    if not os.path.exists(RAG_DB_PATH):
        return []
    with open(RAG_DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    query_lower = query.lower()
    query_words = set(query_lower.split())
    scored = []
    for doc in db:
        score = 0
        text = doc['full_text']
        animal_map = {'cow':'গরু','goat':'ছাগল','hen':'মুরগি','duck':'হাঁস'}
        if animal_filter:
            bn = animal_map.get(animal_filter, animal_filter)
            if bn in text or animal_filter in text:
                score += 5
        for word in query_words:
            if len(word) > 1 and word in text:
                score += 2
        if query_lower in text:
            score += 10
        for kw in ['জ্বর','কাশি','ডায়রিয়া','দুধ','ফোলা','ঘা','রক্ত','দুর্বল','খাচ্ছে','ভ্যাকসিন','fever','cough','milk','weak','blood']:
            if kw in query_lower and kw in text:
                score += 3
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda x: -x[0])
    return [doc for _, doc in scored[:n]]

if __name__ == '__main__':
    setup_rag()