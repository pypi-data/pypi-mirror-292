from setuptools import setup


class Variables:
    ProjectName = "yts-dl" 


with open("README.md", "r") as file:
    readme = file.read()


with open("LICENSE", "r") as file:
    license = file.read()


setup(
    name=Variables.ProjectName,
    version="0.0.1",
    description="Download from YouTube & Spotify",
    install_requires=[
        "colorlog",
        "yt-dlp",
        "spotdl"
    ],
    entry_points={
        "console_scripts": [
            f"{Variables.ProjectName} = {Variables.ProjectName.replace("-", "_")}:downloader",
        ],
    },
    long_description=readme,
    long_description_content_type="text/markdown",
    license=license,
)
