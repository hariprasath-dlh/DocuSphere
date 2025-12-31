import re

def detect_output_mode(query: str) -> str:
    """
    Detects if the query requires structured extraction (URL, Email, Phone) or strict listing.
    Returns: 'EXTRACT_URL' | 'EXTRACT_EMAIL' | 'EXTRACT_PHONE' | 'LIST_ONLY' | 'EXPLAIN' | 'GENERAL'
    """
    q = query.lower()
    
    # 1. URL / Link Extraction
    if any(k in q for k in ["link", "url", "website", "linkedin", "github", "portfolio"]):
        return "EXTRACT_URL"
        
    # 2. Email Extraction
    if any(k in q for k in ["email", "mail", "gmail", "contact"]):
        return "EXTRACT_EMAIL"
        
    # 3. Phone Extraction
    if any(k in q for k in ["phone", "mobile", "number", "call", "contact number"]):
        return "EXTRACT_PHONE"
    
    return "GENERAL"

def extract_urls(chunks: list[dict], query: str) -> str:
    """
    Extracts URLs from chunks using Regex. 
    """
    q = query.lower()
    found_urls = []
    
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    
    for chunk in chunks:
        text = chunk["text"]
        matches = re.finditer(url_pattern, text)
        for match in matches:
            url = match.group(0)
            url = url.rstrip('.,;:)')
            found_urls.append(url)
            
    if not found_urls:
        return "Not found in document."
        
    if "linkedin" in q:
        linkedin_urls = [u for u in found_urls if "linkedin.com" in u.lower()]
        if linkedin_urls: return linkedin_urls[0]
            
    if "github" in q:
        github_urls = [u for u in found_urls if "github.com" in u.lower()]
        if github_urls: return github_urls[0]
            
    if "linkedin" in q or "github" in q:
         return "Not found in document."

    return found_urls[0]

def extract_emails(chunks: list[dict]) -> str:
    """
    Extracts Emails using Regex.
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found_emails = set()
    
    for chunk in chunks:
        text = chunk["text"]
        matches = re.findall(email_pattern, text)
        for email in matches:
            found_emails.add(email)
            
    if not found_emails:
        return "Not found in document."
        
    return list(found_emails)[0]

def extract_phone(chunks: list[dict]) -> str:
    """
    Extracts Phone numbers using Regex.
    Supports common international and local formats.
    """
    # Captures phone numbers with optional +code, spaces, dashes (10-15 digits total)
    phone_pattern = r'\+?[\d\s\-\.\(\)]{10,20}'
    found_phones = set()
    
    for chunk in chunks:
        text = chunk["text"]
        # Use findall but filter for strings that look like valid long number sequences
        matches = re.findall(phone_pattern, text)
        for phone in matches:
            # Clean up and check digit count
            digits = re.sub(r'\D', '', phone)
            if 10 <= len(digits) <= 15:
                # Ensure it doesn't just return a fragment of a longer number
                # by checking if it's surrounded by non-digits
                found_phones.add(phone.strip())
                
    if not found_phones:
        return "Not found in document."
        
    return list(found_phones)[0]
