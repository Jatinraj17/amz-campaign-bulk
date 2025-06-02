from setuptools import setup, find_packages

setup(
    name="amazon_bulk_generator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "amazon_bulk_generator": ["templates/*.csv"],
    },
    include_package_data=True,
    install_requires=[
        "streamlit>=1.31.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.5",
        "streamlit-aggrid==0.3.5",
        "python-decouple>=3.8",
    ],
    python_requires=">=3.8",
)
