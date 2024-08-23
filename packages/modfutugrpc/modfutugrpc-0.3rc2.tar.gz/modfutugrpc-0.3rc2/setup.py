from setuptools import setup, find_packages

exclude_pkgs = [
  'build',
  'grpcio-tools',
  'protobuf',
  'pytest',
  'setuptools',
  'twine',
]
# with open('./requirements.txt') as f:
#   requirements = f.read().splitlines()
# requirements = [x for x in requirements if not any([y for y in exclude_pkgs if y in x])]
setup(
  name='modfutugrpc',
  version='0.3-preview2',
  packages=find_packages('src', exclude=exclude_pkgs),
  package_dir={'': 'src'},
  # install_requires=requirements,
)