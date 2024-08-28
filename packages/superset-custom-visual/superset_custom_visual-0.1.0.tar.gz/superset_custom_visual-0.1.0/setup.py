from setuptools import setup, find_packages

setup(
    name='superset_custom_visual',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Custom visualization plugin for Apache Superset',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-github-repo',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.js', '*.json', '*.css', '*.html', '*.txt', '*.tsx', '*.ts', '*.jsx'],
        'esm': ['*'],
        'lib': ['*'],
        'src': ['*'],
        'types': ['*']
    },
    install_requires=[
        'apache-superset>=1.0.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='superset plugin visualization',
    zip_safe=False,
    entry_points={
        'superset.plugins': [
            'custom_visual = superset_custom_visual.plugin:CustomVisualPlugin'
        ],
    }
)
