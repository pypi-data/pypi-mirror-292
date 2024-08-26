from setuptools import setup, find_packages
def readme():
  with open('README.md', 'r') as f:
    return f.read()
setup(name = "supMath",
    version = "0.1.6",
    description = "Provides large amount of unique mathematical functions and operators",
    long_description = readme(),
    author = "landee",
    author_email = "ivankurd2007@gmail.com",
    packages = find_packages(),
    classifiers = [
    'Programming Language :: Python :: 3.12',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'])