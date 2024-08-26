from setuptools import setup, find_packages

setup(
    name='lescolors',
    version='0.1.0',
    description='Color Manipulation and Analysis Utilities',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Anish Panda',
    author_email='anip1776@gmail.com',
    url='https://github.com/Anish177/lescolors',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests',
        'colorsys',
        'colorthief',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
