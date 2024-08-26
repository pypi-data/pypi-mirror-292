import json

from setuptools import find_packages, setup

manifest = json.load(open("vspacker/manifest.json", "r"))
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name=manifest["name"],
    version=manifest["version"],
    author=manifest["author"],
    description=manifest["description"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=manifest["url"],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": [
            "manifest.json",
        ]
    },
    install_requires=[],
    python_requires=">=3.7",
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ],
)
