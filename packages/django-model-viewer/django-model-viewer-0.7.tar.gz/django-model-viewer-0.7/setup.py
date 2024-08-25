from setuptools import setup, find_packages

setup(
    name='django-model-viewer',
    version='0.7',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='',
    #long_description=open('README.md').read(),
    long_description='',
    long_description_content_type='text/markdown',
    url='https://github.com/twoj-github/myapp',
    author='Mikołaj Łysakowski',
    author_email='mikolaj.lysakowski01@gmail.com',
    install_requires=[
        'Django==4.2.14',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
