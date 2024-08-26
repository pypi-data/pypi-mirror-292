from setuptools import setup, find_packages

setup(
    name='django-model-viewer',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    homepage='None',
    description='Will be usefull',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    author='Mikołaj Łysakowski',
    author_email='mikolaj.lysakowski01@gmail.com',
    install_requires=[
        'Django',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
