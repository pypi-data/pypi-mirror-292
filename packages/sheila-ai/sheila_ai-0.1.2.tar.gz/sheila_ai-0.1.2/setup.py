from setuptools import setup, find_packages

setup(
    name='sheila_ai',
    version='0.1.2',
    author='jackfhession',
    author_email='',  # Replace with your email
    description='Toolkit for building Pytorch Classifiers.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Lill-E-Software/SheilAI',
    packages=find_packages(),
    install_requires=[
        'torch',
        'numpy',
        'nltk',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
)
