from setuptools import setup, find_packages

setup(
    name='django-model-viewer',
    version='1.0.3',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'django_model_viewer': ['templates/*.html'],
    },
    license='This software may be used, modified, and distributed freely for personal, educational, or research purposes. Commercial use, including but not limited to selling or offering the software as part of a product or service, is prohibited without prior written permission from the author.',
    description='A useful tool for viewing Django models, their relationships and functions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lysykot/django-model-viewer',
    author='Mikołaj Łysakowski',
    author_email='mikolaj.lysakowski01@gmail.com',
    install_requires=[
        'Django',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
)
