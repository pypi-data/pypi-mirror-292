from setuptools import setup, find_packages

setup(
    name='kmon_file_streamer',
    version='0.1.4',
    author='Tanvir Ahmed',
    author_email='tanvir.ahmed@kmon.net',
    description='This is used to stream JSON from tar.gz file',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)