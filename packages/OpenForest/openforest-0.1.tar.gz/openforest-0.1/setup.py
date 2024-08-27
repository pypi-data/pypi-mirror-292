from setuptools import setup, find_packages

setup(
    name='OpenForest',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here, if any
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of the OpenForest library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/OpenForest',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
