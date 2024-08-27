from setuptools import setup, find_packages

# Read the contents of the requirements.txt file
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="pysystelbot",
    version="1.0",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "monitor-bot=monitor:main",
        ],
    },
    author="Dan \"Daniel\" Lappisto",
    author_email="lapitzlullaby@gmail.com",
    description="A Telegram bot that monitors system performance and sends updates.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PSYGNEX/systel-bot.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
