from setuptools import setup, find_packages

setup(
    name="gpt-4o-cli",
    version="0.1.0",
    packages=find_packages(), 
    install_requires=[
        "openai",
        "httpx",  
    ],
    entry_points={
        "console_scripts": [
            "gpt=gpt_cli.cli:main",  
        ],
    },
    author="Dipendra Kumar Shah",
    author_email="dipendrashah0789878@gmail.com",
    description="A CLI application to interact with OpenAI's GPT models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/invinciblerd/gpt_cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
