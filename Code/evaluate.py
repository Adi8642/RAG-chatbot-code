import time
import csv
import re
from rag_engine import RAG_Engine

# -----------------------------
# Helpers: normalization + matching
# -----------------------------

def normalize(text: str) -> str:
    """Lowercase, remove punctuation, collapse whitespace."""
    if text is None:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Patterns indicating the model thinks it can't answer
ABSTAIN_PATTERNS = [
    r"\bdo not have information\b",
    r"\bi do not have information\b",
    r"\bnot available\b",
    r"\bnot provided\b",
    r"\bnot in (the|this) (document|context)\b",
    r"\bno information\b",
    r"\bcan t find\b",
    r"\bcannot find\b",
    r"\bnot found\b",
    r"\bunknown\b",
    r"\bno mention\b",
]

def looks_like_abstain(response: str) -> bool:
    resp = normalize(response)
    for pat in ABSTAIN_PATTERNS:
        if re.search(pat, resp):
            return True
    return False

def contains_all_terms(response: str, terms: list[str]) -> bool:
    resp = normalize(response)
    return all(normalize(t) in resp for t in terms)

def contains_any_group(response: str, groups: list[list[str]]) -> bool:
    return any(contains_all_terms(response, g) for g in groups)

# -----------------------------
# Test Cases (Total ~25)
# behavior: "ANSWER" (Positive) or "ABSTAIN" (Negative)
# -----------------------------

test_cases = [
    # --- Section: Basic Info (Positive) ---
    {"type": "Positive", "question": "Who is the project lead?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["evelyn reed"], ["dr reed"]]},
    {"type": "Positive", "question": "What is the project start date?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["august 1 2025"]]},
    {"type": "Positive", "question": "What is the go-live target date?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["december 1 2025"]]},
    {"type": "Positive", "question": "What is the backend codename?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["orion"]]},
    
    # --- Section: Team (Positive) ---
    {"type": "Positive", "question": "Who is the DevOps engineer?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["marcus thorne"], ["thorne"]]},
    {"type": "Positive", "question": "Who is the Chief Designer?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["sarah jenkins"], ["jenkins"]]},
    {"type": "Positive", "question": "Who is the lead for Orion?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["david chen"], ["chen"]]},

    # --- Section: Technology (Positive) ---
    {"type": "Positive", "question": "What database is used?", "behavior": "ANSWER", "match_mode": "ALL", "keywords": ["postgresql"]},
    {"type": "Positive", "question": "What frontend framework is used?", "behavior": "ANSWER", "match_mode": "ALL", "keywords": ["react"]},
    {"type": "Positive", "question": "What cloud provider is used?", "behavior": "ANSWER", "match_mode": "ALL", "keywords": ["aws"]},
    
    # --- Section: Budget & Risks (Positive) ---
    {"type": "Positive", "question": "What is the total budget?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["1.2 million"], ["$1.2m"]]},
    {"type": "Positive", "question": "How much is allocated for development?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["800000"], ["$800k"], ["$800,000"], ["800,000"]]},
    {"type": "Positive", "question": "What is the mitigation for scaling risks?", "behavior": "ANSWER", "match_mode": "ALL", "keywords": ["auto", "scaling"]},
    {"type": "Positive", "question": "What handles API rate limits?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["redis"], ["cache"]]},

    # --- Section: New Content (Security, Vendors, Comms) (Positive) ---
    {"type": "Positive", "question": "What encryption standard is required?", "behavior": "ANSWER", "match_mode": "ALL", "keywords": ["aes", "256"]},
    {"type": "Positive", "question": "How long must audit logs be retained?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["7 years"], ["seven years"]]},
    {"type": "Positive", "question": "Who is the security auditing firm?", "behavior": "ANSWER", "match_mode": "ALL", "keywords": ["cyberguard"]},
    {"type": "Positive", "question": "When is the daily standup?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["9:30 am"], ["930 am"]]},
    {"type": "Positive", "question": "Who is the emergency contact?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["marcus thorne"], ["thorne"]]},

    # --- Newly Added Positive Questions (Previously Negative) ---
    {"type": "Positive", "question": "What is the CEO's name?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["eleanor vance"], ["vance"]]},
    {"type": "Positive", "question": "Who is the HR manager?", "behavior": "ANSWER", "match_mode": "ANY_GROUP", "acceptable": [["sarah miller"], ["miller"]]},

    # --- Negative / Unanswerable Questions (Negative) ---
    {"type": "Negative", "question": "Is the project ahead of schedule?", "behavior": "ABSTAIN"},
    {"type": "Negative", "question": "What is the price of the stock?", "behavior": "ABSTAIN"},
    {"type": "Negative", "question": "What is the color of the new logo?", "behavior": "ABSTAIN"},
    {"type": "Negative", "question": "What is the lunch menu for Friday?", "behavior": "ABSTAIN"},
]

def score_answer_case(response: str, test: dict) -> tuple[bool, str]:
    if looks_like_abstain(response):
        return False, "Model abstained (False Negative)"
    
    mode = test.get("match_mode", "ALL")
    if mode == "ALL":
        keywords = test.get("keywords", [])
        ok = contains_all_terms(response, keywords)
        return (ok, "Found all keywords" if ok else "Missing keywords")
    elif mode == "ANY_GROUP":
        acceptable = test.get("acceptable", [])
        ok = contains_any_group(response, acceptable)
        return (ok, "Found match" if ok else "No match found")
    return False, "Unknown mode"

def score_abstain_case(response: str) -> tuple[bool, str]:
    if looks_like_abstain(response):
        return True, "Correctly abstained"
    return False, "Failed to abstain (Hallucination Risk)"

def run_evaluation():
    print("--- Starting Extended Chatbot Evaluation (25 Questions) ---")

    try:
        engine = RAG_Engine("project_nova_brief.pdf")
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return

    results = []
    correct_count = 0
    
    # Counters for Positive vs Negative data
    pos_total = 0
    pos_correct = 0
    neg_total = 0
    neg_correct = 0

    print(f"\nRunning {len(test_cases)} test cases...\n")

    for i, test in enumerate(test_cases):
        q = test["question"]
        behavior = test.get("behavior", "ANSWER")
        data_type = test["type"]

        print(f"[{i+1}/{len(test_cases)}] ({data_type}) Q: {q}")
        
        start = time.time()
        response = engine.query(q)
        duration = time.time() - start
        
        if behavior == "ABSTAIN":
            is_correct, reason = score_abstain_case(response)
        else:
            is_correct, reason = score_answer_case(response, test)
        
        if is_correct:
            correct_count += 1
            if data_type == "Positive":
                pos_correct += 1
            else:
                neg_correct += 1
        
        if data_type == "Positive":
            pos_total += 1
        else:
            neg_total += 1

        print(f"  -> {'✅ PASS' if is_correct else '❌ FAIL'}: {reason} | {duration:.2f}s")

        results.append({
            "ID": i + 1,
            "Data Type": data_type,
            "Question": q,
            "Expected": behavior,
            "Actual Response": response.strip(),
            "Result": "PASS" if is_correct else "FAIL",
            "Time": f"{duration:.2f}s"
        })

    qrs = (correct_count / len(test_cases)) * 100
    
    print("\n" + "="*40)
    print("EVALUATION SUMMARY")
    print("="*40)
    print(f"Total Questions: {len(test_cases)}")
    print(f"Accuracy Metric: {correct_count/len(test_cases)*100:.1f}% ({correct_count}/{len(test_cases)})")
    print(f"Query Resolution Score (QRS): {qrs:.1f}%")
    
    if pos_total > 0:
        print(f"Positive Data Accuracy: {pos_correct/pos_total*100:.1f}% ({pos_correct}/{pos_total})")
    if neg_total > 0:
        print(f"Negative Data Accuracy: {neg_correct/neg_total*100:.1f}% ({neg_correct}/{neg_total})")
    
    # CSV Export
    with open("evaluation_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print("\nResults saved to evaluation_results.csv")

if __name__ == "__main__":
    run_evaluation()
