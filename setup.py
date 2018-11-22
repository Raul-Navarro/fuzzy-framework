from setuptools import setup, find_packages

setup(name='FuzzySystem',
      version='0.2',
      description='FIS Framework',
      url='',
      author='Raul Navarro-Almanza',
      author_email='rnavarro@uabc.edu.mx',
      license='MIT',
      packages= find_packages(),
      install_requires=[
          'numpy',
          'matplotlib',
      ],
      zip_safe=False) 
