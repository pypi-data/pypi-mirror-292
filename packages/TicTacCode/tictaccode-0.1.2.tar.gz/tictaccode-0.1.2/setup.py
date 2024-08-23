from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="TicTacCode",
    version="0.1.2",
    author="Amos Xiao",
    author_email="AmosXiao1000020@proton.me",
    description="Python Tic-Tac-Toe Library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3.10',
)
