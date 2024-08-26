from setuptools import find_packages, setup

VERSION = '0.0.3'

with open('README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='PyGaLiTool',
    version=VERSION,
    author='xuranyang',
    author_email='xuranyang96@gmail.com',
    description='Common Tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/xuranyang/PyGaLiTool',
    keywords='tool',
    packages=find_packages(),
    install_requires=[
        'pytz >= 2021.1'
    ],
    python_requires='>=3.8',
    # license='MIT',
    license='Apache',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    package_data={'': ['*.csv', '*.txt', '.toml']},
    include_package_data=True,
)
