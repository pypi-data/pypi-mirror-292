from .char import Char, en_zh_punctuation, zh_en_punctuation

class BlankSpaceBaby:
    """
    The BlankSpaceBaby class is used to typeset Chinese and English text.
    language: str, default "zh". Determines the main language of the text (affected by punctuation).
    """
    def __init__(self, text, language="zh", fix_punctuation=True):
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")
        if language not in ["zh", "en"]:
            raise ValueError("Language must be 'zh' or 'en'.")
        
        self.text = text
        self.chars = [Char(character) for character in text]
        self.language = language
        self.fix_punctuation = fix_punctuation

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text

    def typeset(self): 
        output = []
        for i, char in enumerate(self.chars):
            if i == 0:
                output.append(char.character)
            if i == (len(self.chars) - 1):
                continue
            
            next_char = self.chars[i + 1]
            
            if char.language == "English":
                if next_char.language == "Non-English":
                    output.append(" ")
            
            if char.language == "Non-English":
                if next_char.language == "English":
                    output.append(" ")
            
            if self.fix_punctuation and self.language == "zh" and next_char.language == "English Punctuation":
                if next_char.character in en_zh_punctuation:
                    next_char.character = en_zh_punctuation[next_char.character]
                    
            if self.fix_punctuation and self.language == "en" and next_char.language == "Chinese Punctuation":
                if next_char.character in zh_en_punctuation:
                    next_char.character = zh_en_punctuation[next_char.character]
                    
            output.append(next_char.character)
            
        return "".join(output)