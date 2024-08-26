from setuptools import setup, find_packages

def read_long_description(file_path):
    """Read the long description from the specified file."""
    with open(file_path, encoding='utf-8') as f:
        return f.read()

setup(
    name="TkEasyGo",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        'ttkbootstrap>=1.0.0',  # Bootstrap themes for ttk widgets
        'Pillow>=8.0.0'         # Python Imaging Library, used for handling images
    ],
    description="A simple cross-platform GUI generator.",
    long_description=read_long_description('README.md'),  # Ensure you have a README.md file for this
    long_description_content_type='text/markdown',
    author="TkEasyGo",  # Replace with your name
    author_email="tkeasygo@gmail.com",  # Replace with your email address
    url="https://github.com/TkEasyGo/TkEasyGo",  # Replace with your GitHub username
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ],
    python_requires='>=3.7',
)
