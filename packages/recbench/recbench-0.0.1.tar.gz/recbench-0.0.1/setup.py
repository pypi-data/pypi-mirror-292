from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf8')

setup(
    name='recbench',
    version='0.0.1',
    keywords=['recommendation', 'benchmark'],
    description='Benchmarking Recabilities for Large Language Models',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT Licence',
    url='https://github.com/Jyonn/RecBench',
    author='Jyonn Liu',
    author_email='i@6-79.cn',
    platforms='any',
    packages=find_packages(),
    install_requires=[
    ],
    entry_points={
    }
)
