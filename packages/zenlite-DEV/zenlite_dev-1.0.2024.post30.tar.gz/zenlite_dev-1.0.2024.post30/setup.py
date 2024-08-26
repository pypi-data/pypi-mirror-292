from setuptools import setup, find_packages

setup(
    name='zenlite_DEV',
    version='1.0.2024-30',
    description='the python voxel engine',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Izaiyah Stokes',
    author_email='zeroth.bat@gmail.com',
    url='https://github.com/stozak/zenlite',
    packages=find_packages(),
    package_data={"zenlite": ['assets/*', 'assets/shaders/*', 'assets/textures/*']},
    install_requires=[
        "ipdb",
        "GLFW",
        "Numba",
        "Numpy",
        "PyGLM",
        "ModernGL",
        "objgraph",
        "memory_profiler"
    ],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)