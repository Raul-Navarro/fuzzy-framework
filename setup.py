from setuptools import setup, find_packages

setup(name='FuzzySystem',
      version='0.242',
      description='FIS Framework',
      url='https://github.com/Raul-Navarro/fuzzy-framework',
      author='Raul Navarro-Almanza',
      author_email='rnavarro@uabc.edu.mx',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'numpy',
          'matplotlib',
          'pandas',
      ],
      zip_safe=False) 
