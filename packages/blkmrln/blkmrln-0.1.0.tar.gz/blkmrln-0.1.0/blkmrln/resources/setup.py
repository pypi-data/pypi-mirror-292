from setuptools import setup,find_packages

def parse_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="",
    version="0.1.0",
    description="",
    author="",
    author_email="",
    packages=find_packages(where="example.*"),
    install_requires=parse_requirements("dep/common/requirements.txt"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)