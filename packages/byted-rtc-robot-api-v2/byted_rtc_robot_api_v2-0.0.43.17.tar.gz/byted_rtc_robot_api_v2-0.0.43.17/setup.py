from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.43.17'
DESCRIPTION = 'Collect byted metrics to evaluate'
LONG_DESCRIPTION = 'Collect byted metrics to better orchestrate running directories and containers'

# Setting up
setup(
    name="byted_rtc_robot_api_v2",
    version=VERSION,
    author="<serverinspector>",
    author_email="<serverinspector@wearehackerone.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=[]
   )
