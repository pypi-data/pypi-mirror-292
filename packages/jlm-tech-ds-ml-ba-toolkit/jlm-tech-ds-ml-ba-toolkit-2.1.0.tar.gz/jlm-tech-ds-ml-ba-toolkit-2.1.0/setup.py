"""
    Setup file for jlm-tech-ds-ml-ba-toolkit.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.5.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup

if __name__ == "__main__":
    try:
        setup(
            name='jlm-tech-ds-ml-ba-toolkit',
            version='2.1.0',
            author='JLM-Tech LLC',
            author_email='jlmtechconsultingsvc@gmail.com',
            description='data science toolkit',
            long_description='wraps and provides tools for data science',
            license='MIT'
            # url='https://github.com/your-username/your-package-name',
            # packages=['your_package'],
            # python_requires='>=3.6',
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise