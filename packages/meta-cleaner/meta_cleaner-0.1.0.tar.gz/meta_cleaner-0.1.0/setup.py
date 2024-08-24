from setuptools import setup, find_packages

setup(
    name='meta_cleaner',
    version='0.1.0',
    description='A Python package to clean text from META tags using a BERT NER model.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tim Isbister',
    author_email='tim.isbister@pirr.me',
    url='https://github.com/pirr-me/meta_cleaner',
    packages=find_packages(),
    install_requires=[
        'torch',
        'transformers',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
