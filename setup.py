import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mpris_client_asyncio",
    version="1.1",
    author="Yash Bhosale",
    author_email="bhosaley5@gmail.com",
    description="Client library for MPRIS that uses asyncio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yashBhosale/mpris-client-asyncio",
    project_urls={
        "Bug Tracker": "https://github.com/yashBhosale/mpris-client-asyncio/issues",
    },
    classifiers=[       
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Framework :: AsyncIO",
    ],
    python_requires='>=3.6',

    packages=["mpris_client_asyncio"]
)
