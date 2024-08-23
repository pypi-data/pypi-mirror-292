import subprocess
from setuptools import setup, find_packages


def get_version():
    return "0.1.0"


setup(
    name="ryw-textcompare",
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4==4.10.0",
        "nltk==3.6.6",
        "odfpy==1.4.1",
        "tabulate==0.8.9",
        "tqdm==4.66.3",
        "pdfminer.six==20200517",
    ],
    extras_require={
        "lint": ["pylint==3.0.2", "mypy==1.7.1", "flake8==6.1.0", "black==24.3.0", "types-tabulate"],
        "dev": ["pytest", "pre-commit"],
    },
    author="yiwei.ru",
    author_email="ruyiwei.cas@gmail.com",
    description="good job.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "ryw-textcompare=scripts.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "scripts": ["template.html"],
    },
)
