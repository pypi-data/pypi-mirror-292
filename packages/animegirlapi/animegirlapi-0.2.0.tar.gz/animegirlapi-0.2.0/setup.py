from setuptools import setup, find_packages

setup(
    name='animegirlapi',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
    ],
    description='A api that can output anime girls, and is 100% manually verified',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Alleexx',
    author_email='Alleexx129@example.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
