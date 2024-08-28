from setuptools import setup, find_packages

setup(
    name='visagepy',
    version='0.1.0',  # Update this with the correct version
    packages=find_packages(),
    install_requires=[
        'pyyaml'  # Add any other dependencies here
    ],
    author='Nazaryan Artem Karapetovich',
    author_email='spanishiwasc2@gmail.com',
    description='A Python library for building declarative web GUIs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/sl1dee36/visagepy',  # Update with your repository URL
    license='MIT',  # Choose a suitable license
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, this
        # project should only work on Python 3 or Python 2.7 and above
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',

        # Operating systems
        'Operating System :: OS Independent',

        # Environment
        'Environment :: Web Environment',

        # Framework
        'Framework :: Flask',  # If applicable
        'Framework :: Django',  # If applicable

        # Other classifiers as needed
    ],
    python_requires='>=3.6',
)