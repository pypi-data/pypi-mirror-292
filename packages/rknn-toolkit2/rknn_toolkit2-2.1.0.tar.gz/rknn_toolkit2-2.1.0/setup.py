import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rknn-toolkit2",
    version="2.1.0",
    author="ai@rock-chips.com",
    url='https://github.com/airockchip/rknn-toolkit2',
    author_email="ai@rock-chips.com",
    description="RKNN-TOOLKIT2  ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
