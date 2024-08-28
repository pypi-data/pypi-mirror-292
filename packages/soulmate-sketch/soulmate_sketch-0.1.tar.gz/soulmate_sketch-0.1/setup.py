from setuptools import setup, find_packages

setup(
    name='soulmate_sketch',
    version='0.1',
    packages=find_packages(),
    description='Discover Your True Love with a Psychic Soulmate Sketch',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Luna',
    author_email='thesoulmatesketcher@gmail.com',
    url='https://www.thesoulmatesketcher.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

