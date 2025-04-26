def remove_text_after(text, keyword):
    if keyword in text:
        return text.split(keyword)[0].strip()
    return text