from setuptools import setup,find_packages

def parse_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="blkmrln",
    version="0.1.0",
    description="A python build tool optimized to setup for projects of any scale using modern python packaging, robust repository standards, and black formatting.",
    author="Nicholas Fulton",
    author_email="nicholasfulton14@gmail.com",
    packages=find_packages(),
    install_requires=parse_requirements("dep/common/requirements.txt"),
    url="https://github.com/nickornator9000/blkmrln",
    icense="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'blkmrln=blkmrln.cli:main',
        ],
    },
    include_package_data=True
)