from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

DOCUMENTATION_TEXT = (HERE / "DOCUMENTATION.md").read_text()

setup(
    name="cooputils",
    version="0.1.3",
    descriptions="Simple helpers",
    long_description=DOCUMENTATION_TEXT,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "modal",
        "openai",
        "python-dotenv",
        "pydantic",
        "instructor",
        "requests",
    ],
)
