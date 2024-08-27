from distutils.core import setup
setup(
  name = 'IR3',
  packages = ['IR3'], 
  version = '3.0.0',
  license='MIT',
  description = 'Finding the activity value and designing enzyme for input substrate',
  author = 'Xinxin Yu',
  author_email = 'xn255368@dal.ca',
  url = 'https://github.com/XinxinTree/IR3',
  download_url = 'https://github.com/XinxinTree/IR3/archive/refs/tags/v_05.tar.gz',
  keywords = ['IR3', 'dnazyme', 'substrate'],
  install_requires=[
          'pandas',
          'numpy',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
