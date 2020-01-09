import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twolalign",
    version="0.0.7",
    author="Kimmo Koskenniemi",
    author_email="koskenni@gmail.com",
    description="Aligning words in the two-level framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/koskenni/alignment",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent"
    ],
    entry_points={
        "console_scripts": [
            "twol-aligner = twolalign.aligner:main",
            "twol-multialign = twolalign.multialign:main",
            "twol-table2words = twolalign.table2words:step1",
            "twol-words2zerofilled = twolalign.words2zerofilled:main",
            "twol-zerofilled2raw = twolalign.zerofilled2raw:main",
            "twol-raw2named = twolalign.raw2named:main",
        ]
    },
    python_requires='>=3.6',
)
