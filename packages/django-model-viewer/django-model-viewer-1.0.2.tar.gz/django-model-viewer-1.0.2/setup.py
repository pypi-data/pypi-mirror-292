from setuptools import setup, find_packages

setup(
    name='django-model-viewer',
    version='1.0.2',
    packages=find_packages(),
    include_package_data=True,
    license='This software may be used, modified, and distributed freely for personal, educational, or research purposes. Commercial use, including but not limited to selling or offering the software as part of a product or service, is prohibited without prior written permission from the author.',
    description='A useful tool for viewing Django models and their relationships.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lysykot/django-model-viewer/tree/main/django_model_viewer',
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
