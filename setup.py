#!/usr/bin/env python3


from setuptools import setup

if __name__ == '__main__':
    with open('README.md') as file:
        long_description = file.read()
    setup(
        name='upup',
        packages=[
            'upup',
        ],
        entry_points={
            'console_scripts': [
                'upup = upup.main:main',
                'za = upup.main:main'
            ]
        },
        version='2.0',
        description='A terminal tool to upload files to servers based on SSH.',
        long_description_content_type='text/markdown',
        long_description=long_description,
        license='MIT License ',
        author='xi',
        author_email='gylv@mail.ustc.edu.cn',
        url='https://github.com/XoriieInpottn/upup',
        platforms='any',
        classifiers=[
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
        include_package_data=True,
        zip_safe=True,
        install_requires=[
            'paramiko'
        ]
    )
