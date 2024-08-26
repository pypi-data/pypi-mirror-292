from setuptools import setup


with open("README.md", "r") as file:
    readme = file.read()


with open("LICENSE", "r") as file:
    license = file.read()


setup(
    name="yt-dls",
    version="0.0.2",
    description="Download videos from YouTube",
    install_requires=[
        "colorlog",
        "yt-dlp",
    ],
    entry_points={
        "console_scripts": [
            "yt-dls = yt_dls:videoDownloader",
        ],
    },
    long_description=readme,
    long_description_content_type="text/markdown",
    license=license,
)
