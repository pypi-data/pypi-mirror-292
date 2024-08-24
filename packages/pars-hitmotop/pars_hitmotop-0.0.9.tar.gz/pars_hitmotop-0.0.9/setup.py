from setuptools import setup

version='0.0.9'
with open('README.md', encoding='utf-8') as f:
    long_description=f.read()

setup(
    name='pars_hitmotop',
    version=version,

    author='Joy_079',
    author_email='Prufu@yandex.ru',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PY079/pars_hitmotop',
    download_url=f'https://github.com/PY079/pars_hitmotop/arhive/v{version}.zip',
    install_requires=['bs4','colorama','fake-useragent','requests','lxml'],
    # license=...,
    packages=['pars_hitmotop'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)