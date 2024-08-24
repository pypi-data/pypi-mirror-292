from setuptools import setup, find_packages
from pathlib import Path

setup(
  name='pro-video-ferraments',
  version=1.0,
  description='pacote que irá forneceer ferramentas para processamento de video',
  long_description=Path('README.md').read_text(),
  author="Bruno",
  author_email='test@email.com',
  keywords=['camera','video', 'processamento'],
  packages=find_packages()
)