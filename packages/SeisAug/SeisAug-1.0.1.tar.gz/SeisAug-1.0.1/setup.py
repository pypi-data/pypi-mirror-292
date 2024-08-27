from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='SeisAug',
    version='1.0.1',
    packages=find_packages(),
    keywords=['Seismology', 'Earthquakes', 'Deep Learning', 'Data Augmentation'],
    install_requires=['obspy', 'matplotlib', 'scipy~=1.10.0', 'jupyter', 'ipywidgets', 'numpy'],
    author='ISR-AIML',
    author_email='isr3aiml@gmail.com',
    description='A Comprehensive Data Augmentation Python Toolkit for Deep Learning.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ISR-AIML/SeisAug',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

