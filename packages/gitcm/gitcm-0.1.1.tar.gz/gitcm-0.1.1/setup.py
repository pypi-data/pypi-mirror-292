from setuptools import setup, find_packages

setup(
    name='gitcm',
    version='0.1.1',
    description='A custom git commit command with AI-generated commit messages.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gauravreddy008/gitcm',  # Replace with your GitHub repo
    author='Gaurav Tadkapally',
    author_email='gauravreddy008@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'gitcm=gitcm.main:git_commit',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)