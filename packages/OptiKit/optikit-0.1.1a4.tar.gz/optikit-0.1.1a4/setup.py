from setuptools import setup, find_packages

setup(
   name='OptiKit',
   version='0.1.1a4',
   description='A basic optics module',
   author='Armando Martinez',
   author_email='ar.martinez.hdz@hotmail.com',
   url= 'https://github.com/ARMANDOMTZ05/pyOptics',
   packages= find_packages(),
   install_requires=['matplotlib', 'numpy', 'scipy', 'pillow'],
   keywords= 'numpy, optics, holography, slm, python3, wavefront shaping',
   classifiers= ['Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.10'],
   python_requires='>=3.10',
   license = 'MIT License' 
)