from setuptools import setup, find_packages

keywords = [
    'tire',
    'codes',
    'automotive',
    'validation',
    'parser',
]

setup(
    name='tire_codes',
    version='0.1.0', 
    packages=find_packages(),
    include_package_data=True,
    description='A lightweight, dependency-free Python tool to parse and validate tire codes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown', 
    author='Michael Pearce',
    author_email='firstflush@protonmail.com', 
    url='https://github.com/firstflush/tire_codes',
    keywords='tire, codes, automotive, validation, parser, size',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'tire-codes=tire_codes.main:main',
        ],
    },
    license='MIT',
    install_requires=[],
)