from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geekros",
    version="0.0.1",
    author="MakerYang",
    author_email="admin@wileho.com",
    description="Python development framework for geekros.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geekros/geekros",
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.9.0",
    license="Apache-2.0",
    project_urls={
        "Documentation": "https://www.geekros.com/docs",
        "Website": "https://lgeekros.com",
        "Source": "https://github.com/geekros/geekros",
    },
    keywords=["webrtc", "realtime", "audio", "video", "geekros", "ros", "ros2", "ubuntu"],
)
