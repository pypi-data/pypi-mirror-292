from setuptools import setup, find_packages

setup(
    name='gstfkl',
    version='1.0.0',
    description='Generic Scanner Tool for Kali Linux',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='ruben',
    author_email='ruben.s@skiff.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'dnspython',
        'python-nmap',
        'termcolor',
        # Add any other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'gstfkl=gstfkl:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

