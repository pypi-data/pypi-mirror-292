from pathlib import Path
from setuptools import setup, find_packages
import sys

sys.path.insert(0, '.')

from icpv import __version__

VERSION = __version__
DESCRIPTION = 'Integrated Circuit Physical Verification'

here = Path(__file__).resolve().parent
with open(here / 'README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='icpv',
    version=VERSION,
    author='YEUNGCHIE',
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yeungchie/icpv',
    packages=['icpv'],
    python_requires='>=3.7',
    install_requires=[
        'typing_extensions',
        'PyYAML',
        'numpy',
        'gdstk',
    ],
    keywords=[
        'icpv',
        'verification',
        'virtuoso',
        'calibre',
        'python',
        'linux',
        'yeungchie',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: Unix',
    ],
)
