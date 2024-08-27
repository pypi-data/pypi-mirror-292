from setuptools import setup, find_namespace_packages

# Đọc nội dung của requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="zinley-cli",
    version="0.0.10",
    packages=find_namespace_packages(include=['zinley', 'zinley.*']),
    include_package_data=True,
    install_requires=required,
    entry_points={
        'console_scripts': [
            'zinley = zinley.__main__:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)