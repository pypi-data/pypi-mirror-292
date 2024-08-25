from setuptools import setup, find_packages

setup(
    name='prestream',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prestream=prestream.prestream:main',
        ],
    },
    install_requires=[
        'yt-dlp',
        'ffmpeg-python',
    ],
    author='Avinion Group',
    author_email='shizofrin@gmail.com',
    url='https://x.com/Lanaev0li',
    description='Interactive script for streaming with yt-dlp and ffmpeg.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
