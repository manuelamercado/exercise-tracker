from setuptools import find_packages, setup

setup(
    name="Exercise Tracker",
    version="0.1.0",
    author="Manuela Mercado",
    description="An Exercise Tracker app",
    keywords="Flask example",
    url=("https://github.com/manuelamercado/exercise-tracker"),
    python_requires='~=3.8',
    package_dir={'': 'flaskr'},
    packages=find_packages(where='flaskr'),
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "psycopg2",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
