from CodeRus.commands import CodeRusTranslator

def main():
    translator = CodeRusTranslator()
    print("Введите код на русском:")
    code = '\n'.join(iter(input, ''))  # Ввод многострочного текста
    translated_code = translator.translate(code)
    print("\nПереведенный код:")
    print(translated_code)
