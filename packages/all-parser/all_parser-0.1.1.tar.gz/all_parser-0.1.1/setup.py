from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='all-parser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'click',
        'python-docx',
        'PyPDF2',
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'all-parser=all_parser.cmd:parse',
        ],
    },
)
