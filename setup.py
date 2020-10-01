import sys
import os

from setuptools import dist
dist.Distribution().fetch_build_eggs(['Cython', 'numpy'])

import numpy.distutils.misc_util as np_misc
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython import Tempita as tempita

import versioneer

compile_args = np_misc.get_info('npymath')
compile_args['include_dirs'].append('crick/klib')

if '--debug' in sys.argv:
    sys.argv.remove('--debug')
    compile_args['undef_macros'] = ["NDEBUG"]
    compile_args['extra_compile_args'] = ['-O0']


def generate_code(templates):
    """Generate code from template files"""
    for template in templates:
        # template extention must be .in
        assert template.endswith('.in')
        outfile = template[:-3]

        if (os.path.exists(outfile) and
                (not os.path.exists(template) or
                 os.stat(template).st_mtime < os.stat(outfile).st_mtime)):
            # If output is present but template isn't, or if template is not
            # updated no need to generate
            continue

        with open(template, "r") as f:
            tmpl = f.read()
        output = tempita.sub(tmpl)

        with open(outfile, "w") as f:
            f.write(output)


templates = ['crick/space_saving_stubs.c.in']

generate_code(templates)

extensions = [Extension("crick.tdigest",
                        ['crick/tdigest.pyx'],
                        **compile_args),
              Extension("crick.space_saving",
                        ['crick/space_saving.pyx'],
                        **compile_args),
              Extension("crick.stats",
                        ['crick/stats.pyx'],
                        **compile_args)
              ]

setup(name='crick',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='High performance approximate and streaming algorithms',
      long_description=(open('README.rst').read()
                        if os.path.exists('README.rst') else ''),
      keywords='streaming approximate algorithms',
      url='https://github.com/jcrist/crick',
      maintainer='Jim Crist',
      maintainer_email='crist042@umn.edu',
      license='BSD',
      packages=['crick', 'crick.tests'],
      ext_modules=cythonize(extensions),
      setup_requires=['numpy', 'Cython'],
      zip_safe=False)
