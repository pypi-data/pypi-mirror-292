from setuptools import setup, find_packages

extras_require = {
    "posix": ["uvloop"],
    "win32": ["winloop"],
}

setup(
    name="winuvloop",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    extras_require=extras_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
    ],
)
