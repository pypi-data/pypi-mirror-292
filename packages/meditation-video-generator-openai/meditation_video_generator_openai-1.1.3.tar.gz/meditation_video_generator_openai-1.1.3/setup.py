from setuptools import setup, find_packages

setup(
    name='meditation-video-generator-openai',
    version='1.1.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pedalboard', 'pydub', 'openai','requests', 'moviepy', 'pillow'
    ],
    author='Alexis Kirke',
    author_email='alexiskirke2@gmail.com',
    description='A tool to create guided meditations (like those found on YouTube) using OpenAI.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
