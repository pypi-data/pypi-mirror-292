from setuptools import setup, find_packages

setup(
    name='ensemble_seg',
    version='0.3.0',
    description='Agnostic ensemble algorithm for instance segmentation tasks',
    author='Jack Mead',
    author_email='jackmead515@gmail.com',
    url='https://github.com/ainascan/ensemble_seg',
    packages=find_packages(),
    install_requires=[
        "numpy",
        "numba",
        "opencv-python",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)