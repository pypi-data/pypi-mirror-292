from googletrans import Translator

def translate_text(text: str, to_lan="en", from_lan="en"):
    """
        This is for Translate text to any language

        Args:
            text (str)
            to_lan (str): To Language. Defaults to "en".
            from_lan (str, optional): From Language. Defaults to "en".

        Returns:
            str: Translated Text
    """
    translator = Translator()
    return translator.translate(text, src=from_lan, dest=to_lan).text