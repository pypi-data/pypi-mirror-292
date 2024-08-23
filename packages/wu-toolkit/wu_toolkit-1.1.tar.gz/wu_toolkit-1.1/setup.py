from setuptools import setup, find_packages
from wu_toolkit.__version__ import __title__, __version__

with open("requirements.txt") as f:
    requirements = f.readlines()

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="wu_toolkit",
    version=__version__,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    license="GPLv3",
    description="个人用的命令包",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Feifeng Wu",
    author_email="wufeifeng_hust@163.com",
    keywords=["python", "toolkit", "modeling"],
    python_requires=">=3.7",
    install_requires=requirements,
    packages=find_packages(),
    # 把script加进去
    package_data={"wu_toolkit": ["script/*"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "wtk=wu_toolkit.command:main",
        ]
    },
)
