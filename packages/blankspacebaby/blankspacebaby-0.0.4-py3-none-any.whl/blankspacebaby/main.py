from .char import Char, en_zh_punctuation, zh_en_punctuation

def typeset(text, language="zh", fix_punctuation=True):
    """
    Typesets Chinese and English text.
    
    :param text: str, the input text to typeset
    :param language: str, default "zh". Determines the main language of the text (affected by punctuation).
    :param fix_punctuation: bool, default True. Whether to fix punctuation based on the main language.
    :return: str, the typeset text
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string.")
    if language not in ["zh", "en"]:
        raise ValueError("Language must be 'zh' or 'en'.")

    chars = [Char(character) for character in text]
    output = []

    for i, char in enumerate(chars):
        if i == 0:
            output.append(char.character)
        if i == (len(chars) - 1):
            continue
        next_char = chars[i + 1]
        if char.language == "English" and next_char.language == "Non-English":
            output.append(" ")
        elif char.language == "Non-English" and next_char.language == "English":
            output.append(" ")

        if fix_punctuation:
            if language == "zh" and next_char.language == "English Punctuation":
                next_char.character = en_zh_punctuation.get(next_char.character, next_char.character)
            elif language == "en" and next_char.language == "Chinese Punctuation":
                next_char.character = zh_en_punctuation.get(next_char.character, next_char.character)

        output.append(next_char.character)
    
    return "".join(output)