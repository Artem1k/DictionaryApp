from setuptools import setup


setup(
    name="Dictaker",
    version="0.01",
    packages=["dictaker"],
    entry_points={
        "console_scripts": [
            "dictaker = dictaker.__main__:main",
        ],
    },
    install_requires=[
        "spacy",
        "contractions",
        "pandas",
        "deep_translator",
        "openpyxl",
    ],
    python_requires=">=3.9,<4.0",
)
