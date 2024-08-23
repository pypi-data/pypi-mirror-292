from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="altrumai",
    version="1.1.2",
    packages=find_packages(),
    install_requires=[
        "httpx==0.26.0",
        "pydantic==2.6.2",
        "tenacity==8.4.1",
    ],
    author="Yashwanth S",
    author_email="yashwanth@aligne.ai",
    description="A python client for interacting with AltrumAI APIs.",
    long_description=README,
    long_description_content_type='text/markdown',
    license="Apache-v2",
    keywords="altrumai api client aligne",
)
