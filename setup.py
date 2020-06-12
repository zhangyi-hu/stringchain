from setuptools import setup

setup(
  name='stringchain',
  version='0.8',
  python_requires='>=3.7',
  packages=['stringchain'],
  url='https://github.com/zhangyi-hu/stringchain',
  license='BSD',
  author='Zhangyi Hu',
  author_email='hu.zhangyi@gmail.com',
  description=('Grammartize a given set of delimited string chains. '
               'Eliminate typo or invalid combinations when preparing such values.'),
  entry_points={"console_scripts": ["stringchain = stringchain.generator:generate"]}
)
