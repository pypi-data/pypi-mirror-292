from setuptools import setup, find_packages

setup(
    name='CodeRus',  # Имя вашей библиотеки
    version='0.1',
    packages=find_packages(),  # Находит все пакеты в проекте
    install_requires=[
        # Список зависимостей, если есть
    ],
    entry_points={
        'console_scripts': [
            'code-rus=CodeRus.main:main',  # 'code-rus' — это команда, 'CodeRus.main:main' — это путь к функции
        ],
    },
)
