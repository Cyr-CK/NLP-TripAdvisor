import re

def clean_text(text: str) -> str:
    txt = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    txt = txt.replace('  ', ' ')
    return txt.strip()

def extract_by_regex(text: str, regex: str) -> str:
    pattern = re.compile(regex)
    match = pattern.search(text)
    if match:
        # Check if there are any groups and return the first group if it exists
        if match.groups():
            return match.group(1) + " " + match.group(2) if len(match.groups()) > 1 else match.group(1)
        else:
            return match.group(0)  # Return the entire match if no groups are defined
    return ""

def filter_by_regex(text, pattern):
    """Extract data using a regular expression."""
    match = re.sub(pattern, '', text)
    return match if match else None