from setuptools import setup

setup(name='xts',
      version='0.1',
      description='xts with setup.py',
      url='https://github.com/symphonyfintech/xts-pythonclient-api-sdk',
      author='someone',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['XTConnect'],
      data_files=[('XTConnect', ['XTConnect/config.ini'])],
      zip_safe=False)
