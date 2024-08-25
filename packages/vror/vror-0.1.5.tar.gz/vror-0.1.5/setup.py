from setuptools import setup, find_packages

setup(
    name='vror',  # Your package name
    version='0.1.5',  # Initial version
    packages=find_packages(),  # Automatically find packages in the project
    install_requires=[
        'networkx',
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
    ],  # External dependencies
    author='Ragu and Team',
    author_email='https.ragu@gmail.com',
    description='A package for solving various optimization problems. Developed by Ramanujan Computing Centre, Anna University.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ragu8/vror',  # URL to your project repository
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
