from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
install_requires = ["click>=7.0", "requests", "pyyaml", "m3u8"]
extras_require = {"test": ["tox"]}

setup(
    name="pitchbase",
    version="0.13.0",
    description="Command Line utility for pitchbase.",
    long_description=open(os.path.join(here, "README.md")).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="pitchbase tool aws",
    author="Hiroshi Toyama",
    author_email="toyama0919@gmail.com",
    url="https://github.dena.jp/AI/pitchbase",
    license="MIT",
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require["test"],
    entry_points={"console_scripts": ["pitchbase=pitchbase.commands:main"]},
)
