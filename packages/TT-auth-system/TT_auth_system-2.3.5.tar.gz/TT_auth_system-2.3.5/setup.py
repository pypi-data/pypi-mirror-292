from setuptools import setup, find_packages

setup(
    name="TT_auth_system",
    version="2.3.5",
    author="Jarod Johnson",
    author_email="jarodjohnson1001@gmail.com",
    description="An authentication system with one-time login links, templated email sending, and SQLite database support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jarod-johnson-23/TT24_otc_generator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'python-dotenv',
        'jinja2',
        'cryptography',
        'sqlalchemy', 
    ],
)