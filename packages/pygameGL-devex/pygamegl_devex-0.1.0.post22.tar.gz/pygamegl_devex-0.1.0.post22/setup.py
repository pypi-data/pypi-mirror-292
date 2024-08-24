from setuptools import setup, find_packages

setup(
    name='pygameGL-devex',
    version='0.1.0-22',
    description='A packaged version of the pygameGL devex repository branch containing developmental and experimental features.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Izaiyah Stokes',
    author_email='zeroth.bat@gmail.com',
    url='https://github.com/stozak/pygameGL',
    packages=find_packages(),
    package_data={"pygameGL": ['assets/*', 'ext/SoGL/*']},
    install_requires=[
        "ipdb",
        "GLFW",
        "Numba",
        "Numpy",
        "PyGLM",
        "PyOpenGL",
        "ModernGL",
        "objgraph",
        "Swarm-ECS",
        "memory_profiler"
    ],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

# setup(
#     name='pygameGL',
#     version='0.1.0',
#     description='',
#     long_description=open('README.md').read(),
#     long_description_content_type='text/markdown',
#     author='Izaiyah Stokes',
#     author_email='zeroth.bat@gmail.com',
#     url='https://github.com/stozak/pygameGL',
#     packages=find_packages(),
#     package_data={"pygameGL": ['assets/*']},
#     install_requires=[
#         "ipdb",
#         "GLFW",
#         "Numba",
#         "Numpy",
#         "PyGLM",
#         "PyOpenGL",
#         "ModernGL",
#         "objgraph",
#         "Swarm-ECS",
#         "memory_profiler"
#     ],
#     classifiers=[
#         'Programming Language :: Python :: 3.12',
#         'License :: OSI Approved :: MIT License',
#         'Operating System :: OS Independent',
#     ],
# )

