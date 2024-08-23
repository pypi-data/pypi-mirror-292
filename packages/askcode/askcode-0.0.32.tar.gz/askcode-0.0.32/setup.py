from setuptools import setup, find_packages

setup(
    name='askcode',
    version='0.0.32',
    packages=find_packages(),
    description='eUR Ask Code',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'ollama',
        'numpy',
        'gitpython',
        'requests',
        'pytest-shutil',
        "tqdm"
],
    author='eUR',
    author_email='aiml@embedur.com',
    license='MIT',
    entry_points={
        "console_scripts": [
            "askcode = askcode.__main__:main"
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
