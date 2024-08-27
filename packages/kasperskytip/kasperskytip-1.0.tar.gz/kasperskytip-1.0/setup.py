from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="kasperskytip",
    version="1.0",

    description="Kaspersky TIP unofficial API for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="api kaspersky antivirus malware scan",

    url="https://github.com/clienthold/kaspersky-tip",
    author="Dmitry Kondrashov",

    packages=["kasperskytip"],
    python_requires=">=3.7, <4",
    install_requires=["requests", "datetime", "validators"]
)
