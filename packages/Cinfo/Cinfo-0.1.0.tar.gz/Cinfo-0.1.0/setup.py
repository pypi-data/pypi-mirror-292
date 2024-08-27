from setuptools import setup, find_packages

setup(
    name="Cinfo",
    
    py_modules=['cli', 'code_lines', 'all_lines', 'empty_lines', 'comment_lines', 'file_info'],
    
    author_email='coding.game82@gmail.com',
    
    version='0.1.0',
        
    description="a CLI program to know about your written code for Unix ( linux / macOS ).",
    
    long_description=open('README.md').read(),
    
    long_description_content_type='text/markdown',
    
    url='https://github.com/codinggmae/Cinfo',
    
    packages=find_packages(),
    
    install_requires=[
        "click>=8.1.7",
        "tabulate>=0.9.0",
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    
    python_requires='>=3.11',
    
    entry_points={
        'console_scripts': [
            'cinfo=cli:readFile',
        ],
    },
    
    license="MIT"
)
