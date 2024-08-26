from setuptools import setup, find_packages

setup(
    name='ErrorLogger',
    version='0.0.4',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'collect_logs=errorlogger.logger:ErrorLogger.collect_logs',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A standalone library for collecting and logging errors from external applications.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/errorlogger',  # Update with your repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

