from setuptools import setup, find_packages

setup(
    name='fs_nsfw_checker',
    version='0.2.0',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'Pillow',
        'requests',
    ],
    author='FitSnap',
    author_email='noreply@fitsnap.io',
    description='A package to check NSFW content in virtual try-on using the free FitSnap API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/parksoftware/fs-nsfw-checker',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)