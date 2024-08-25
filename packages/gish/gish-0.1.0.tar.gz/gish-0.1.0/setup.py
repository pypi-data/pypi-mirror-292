from setuptools import setup, find_packages

setup(
    name='gish',
    version='0.1.0',
    description='A CLI tool for managing GitHub profiles using SSH.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Helder Perez',
    author_email='helder.perez@avynta.com',
    url='https://github.com/helder-avynta/gish',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'gish=gish.cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
)
