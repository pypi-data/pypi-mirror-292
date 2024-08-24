from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='python-gsmmodem_weabox',
    version='1.0.5',
    author='PT Thanh',
    description='Control an attached GSM modem: send/receive SMS messages, handle calls, etc',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.3',
    long_description=description,
    long_description_content_type="text/markdown",
)