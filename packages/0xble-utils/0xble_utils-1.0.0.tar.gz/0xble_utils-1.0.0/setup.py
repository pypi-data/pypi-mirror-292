from setuptools import setup, find_packages

setup(
    name="0xble-utils",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "pyfzf",
        "termcolor",
        "rich",
        "pytz",
        "dateparser",
        "tenacity",
        "notion-client",
    ],
)
