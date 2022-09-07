import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'pyside6 == 6.3.1',
    'PyQt6 == 6.3.1',
    'IceSpringPySideStubs-PyQt6 == 1.3.1',
    'wikipedia == 1.4.0',
    'nltk',
    'keybert',
    'bing-image-downloader',
    'opencv-python',
    'pyttsx3',
]

DEV_REQUIREMENTS = [
    'black == 22.*',
    'build == 0.7.*',
    'coveralls == 3.*',
    'flake8 == 4.*',
    'isort == 5.*',
    'mypy == 0.942',
    'pytest == 7.*',
    'pytest-cov == 3.*',
    'twine == 4.*',
]

setuptools.setup(
    name='video_name_generator',
    version='0.1.0',
    description='Generation of a Automatic Video',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/pedrojlazevedo/python-video-generator',
    author='pedrojlazevedo',
    license='MIT',
    packages=setuptools.find_packages(
        exclude=[
            'examples',
            'test',
        ]
    ),
    package_data={
        'python-video-generator': [
            'py.typed',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'PROJECT_NAME_URL=python_video_generator.my_module:main',
        ]
    },
    python_requires='>=3.7, <3.9',
)
