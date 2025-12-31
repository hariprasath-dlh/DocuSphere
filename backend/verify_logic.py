from output_mode import extract_urls, extract_emails, extract_phone
from intent_normalizer import normalize_intent
from llm import validate_and_clean_output
from query_normalizer import normalize_query
from retrieval import filter_chunks_by_target

def test_final_upgrade():
    print("Testing DocuSphere Final Upgrade Accuracy...")
    
    # 1. Query Normalization
    assert normalize_query("list soft skil") == "list soft skill"
    assert normalize_query("tell me abt intern ship") == "explain about intern ship"
    print("  ✅ Query Normalization Passed")

    # 2. Intent Detection
    res1 = normalize_intent("list soft skil")
    assert res1["intent"] == "LIST_ONLY"
    assert res1["target"] == "soft_skills"
    
    res2 = normalize_intent("linkedin link")
    assert res2["intent"] == "EXTRACT"
    assert res2["target"] == "links"
    print("  ✅ Intent Detection (LIST_ONLY, EXTRACT) Passed")

    # 3. Targeted Retrieval Filtering
    mock_chunks = [
        {"text": "Python and React are my technical tools."},
        {"text": "I am a good team leader and communicator (soft skills)."}
    ]
    filtered = filter_chunks_by_target(mock_chunks, "soft_skills", "LIST_ONLY")
    assert len(filtered) == 1
    assert "soft skills" in filtered[0]["text"]
    print("  ✅ Target-Aware Filtering (retrieval.py) Passed")

    # 4. LLM Strict Rules (4-word limit)
    # 5 words should fail
    fail_5 = "I am a team leader (Page 1)"
    assert validate_and_clean_output(fail_5, "LIST_ONLY") == "Not found in document."
    
    # 4 words should pass
    pass_4 = "Excellent Team Leader (Page 1)"
    res_pass = validate_and_clean_output(pass_4, "LIST_ONLY")
    assert "Team Leader" in res_pass
    
    # Forbidden word check
    forbidden = "Developed a system (Page 2)"
    assert validate_and_clean_output(forbidden, "LIST_ONLY") == "Not found in document."
    print("  ✅ LLM Strict Rules (4 words, forbidden terms) Passed")

if __name__ == "__main__":
    try:
        test_final_upgrade()
        print("\n🎉 ALL FINAL CORE UPGRADES VERIFIED")
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
