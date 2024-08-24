from setuptools import setup, find_packages
import os


packageVersion = os.getenv("PyLibVersion", "0.0.1")
print ("Setting up package version: {}".format(packageVersion))

description = ""
with open("README.md", "r") as rdf:
    description = rdf.read()

print ("Possible packages: {}".format(find_packages()))

setup (
    name="unitypredict-engines",
    version=packageVersion,
    packages=find_packages(),
    install_requires=[
        # Currently no dependencies
    ],
    entry_points = {          # this here is the magic that binds your function into a callable script
        'console_scripts': 
        [
            'unitypredict-engines=unitypredict_engines.scripts:main'
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown"
)
