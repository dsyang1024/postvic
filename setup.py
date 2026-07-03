from pathlib import Path

from setuptools import setup


BASE_DIR = Path(__file__).resolve().parent
LIB_DIR = BASE_DIR / "lib"


def read_readme() -> str:
    return (BASE_DIR / "README.md").read_text(encoding="utf-8")


def list_modules() -> list[str]:
    return sorted(
        path.stem
        for path in LIB_DIR.glob("*.py")
        if path.name != "__init__.py"
    )


scripts = []



setup(
    name="postvic", 
    version="0.1.0",
    author = 'DK Yang',
    author_email = 'yang2309@purdue.edu',
    url='https://github.com/dsyang1024/postvic.git',
    description="Analysis tools for VIC simulation outputs",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    license="GPL-3.0-only",
    package_dir={"": "lib"},
    py_modules=list_modules(),
    scripts=scripts,
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "geopandas",
    ],
    include_package_data=True,
    python_requires=">=3.11",
)