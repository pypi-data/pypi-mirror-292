from setuptools import setup, find_packages

setup(
    name="creao",
    version="0.2.32",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "scikit-learn==1.5.1",
        "haystack-ai==2.3.1",
        "openai==1.40.6",
        "datasets==2.21.0",
        "gradio==4.41.0",
        "ragas==0.1.14"
        # List your project dependencies here
    ],
    include_package_data=True,
    description="A description of your project",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://creao@dev.azure.com/creao/creao/_git/creao",
    author="creaoai",
    author_email="dev@creao.ai",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
