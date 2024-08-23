from setuptools import setup, find_packages

setup(
    name='kidsafeinternet',
    version='0.0.1',
    author='Zander Lewis',
    author_email='zander@zanderlewis.dev',
    description='A library for detecting safe images using AI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kidsafeinternet/library',
    packages=find_packages(),
    install_requires=[
        'fastai>=2.0.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)