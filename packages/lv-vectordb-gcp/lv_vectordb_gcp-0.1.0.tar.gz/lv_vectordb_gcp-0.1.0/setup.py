from setuptools import setup, find_packages

setup(
    name='lv_vectordb_gcp',
    version='0.1.0',
    description='A package for GCP, LangChain, and BigQuery Vector store integration',
    author='Navaneethan S',
    author_email='navaneethan.s@latentview.com',
    url='https://github.com/lvnavaneethan123/lv_vectordb_gcp',
    packages=find_packages(where="/Users/navaneethans/PycharmProjects/lv_vectordb_gcp/lv_vectordb_gcp/"),
    install_requires=[
        'google-cloud-bigquery',
        'google-cloud-aiplatform',
        'google-auth',
        'langchain',
        'langchain-google-vertexai',
        'langchain-google-community[featurestore]',
        'jsonpatch',
        'tabulate'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
