from setuptools import setup
from io import open
from blitz_sphinx_theme import __version__

setup(
    name="blitz_sphinx_theme",
    version=__version__,
    author="Etched",
    author_email="colin_x@etched.com",
    url="https://github.com/etched-ai/blitz_sphinx_theme",
    docs_url="https://github.com/etched-ai/blitz_sphinx_theme",
    description="Blitz Sphinx Theme",
    py_modules=["blitz_sphinx_theme"],
    packages=["blitz_sphinx_theme"],
    include_package_data=True,
    zip_safe=False,
    package_data={
        "blitz_sphinx_theme": [
            "theme.conf",
            "*.html",
            "static/css/*.css",
            "static/js/*.js",
            "static/js/vendor/*.js",
            "static/fonts/*.*",
            "static/images/*.*",
            "theme_variables.jinja",
        ]
    },
    entry_points={
        "sphinx.html_themes": [
            "blitz_sphinx_theme = blitz_sphinx_theme",
        ]
    },
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Documentation",
    ],
    install_requires=[
        "sphinx==6.0.0",
        "myst-nb==1.1.0",
    ],
)
