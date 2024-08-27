from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

    setup(
        name="crack-pdf",
        version="0.1.1",
        author="Richard Szilagyi",
        author_email="szprichard@proton.me",
        description="A tool to crack password-protected PDFs",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/szpatrichard/crack-pdf",
        packages=find_packages(),
        install_requires=[
            "PyPDF2",
        ],
        entry_points={
            "console_scripts": [
                "crack-pdf=crack_pdf.core:main",
            ],
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires=">=3.6",
    )
