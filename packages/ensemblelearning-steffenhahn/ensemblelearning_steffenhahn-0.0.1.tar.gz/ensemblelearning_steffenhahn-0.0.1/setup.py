from setuptools import setup, find_packages

setup(
    name="ensemblelearning_steffenhahn",  # Package name
    version="0.0.1",
    description="A package for EnsembleLearning for Software Entwicklung Course 2",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Steffen Hahn",
    author_email="2310837609@stud.fh-kufstein.ac.at",
    url="https://gitlab.web.fh-kufstein.ac.at/hahnsteffen/oftwareentwicklung2_steffenhahn",  # Placeholder URL
    packages=find_packages(where='src'),  # Assuming source files are in the src directory
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
