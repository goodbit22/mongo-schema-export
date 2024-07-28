from setuptools import setup

setup(
    name='MongoSchemaImportExport',
    version='0.2.5',
    long_description_content_type="text/markdown",
    packages=['mongo_import_export_schema'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Import and export metadata about mongodb databases and collections',
    classifiers=[
        "Programming Language :: Python",
    ],
    author="Jonathan Mackenzie & goodbit22",
    url="https://github.com/jonnoftw/mongo_import_export_schema",
    keywords=["pymongo mongodb schema import export"],
    long_description=open('README.md').read(),
    install_requires=['pymongo'],
    extras_require={
        "dev": ["twine"],
    },
    scripts=['mongo_import_export_schema/mongo-schema-export.py',
             'mongo_import_export_schema/mongo-schema-import.py'],
    python_requires=">=3.9"
)
