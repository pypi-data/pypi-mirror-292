class CodeRusTranslator:
    def __init__(self):
        self.translation_map = {
            'печать': 'print',
            'если': 'if',
            'для': 'for',
            'пока': 'while',
            'определение': 'def',
            'добавить': 'append',
            'ввод_данных': 'input',
            'истина': 'True',
            'ложь': 'False',
            'ничего': 'None',
            'класс': 'class',
            'импортировать': 'import',
            'из': 'from',
            'как': 'as',
            'вернуть': 'return',
            'попытаться': 'try',
            'кроме': 'except',
            'возбуждать': 'raise',
            'с': 'with',
            'прервать': 'break',
            'продолжить': 'continue',
            'ничего_не_делать': 'pass',
            'глобальный': 'global',
            'не_локальный': 'nonlocal',
            'лямбда': 'lambda',
            'удалить': 'del',
            'утверждать': 'assert',
            'отдавать': 'yield',
            'асинхронный': 'async',
            'ожидать': 'await',
            'выполнить': 'exec',
            'оценить': 'eval',
            'открыть': 'open',
            'закрыть': 'close',
            'читать': 'read',
            'писать': 'write',
            'обрезать': 'strip',
            'разделить': 'split',
            'соединить': 'join',
            'форматировать': 'format',
            'получить': 'get',
            'установить': 'set',
            'словарь': 'dict',
            'список': 'list',
            'кортеж': 'tuple',
            'целое': 'int',
            'дробное': 'float',
            'строка': 'str'
        }

    def translate(self, code):
        translated_code = []
        for line in code.split('\n'):
            words = line.split()
            translated_line = ' '.join(self.translation_map.get(word, word) for word in words)
            translated_code.append(translated_line)
        return '\n'.join(translated_code)
