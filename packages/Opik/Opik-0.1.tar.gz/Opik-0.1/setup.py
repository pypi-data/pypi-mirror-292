import setuptools

with open('DESCRIPTION.md', 'r') as readme:
  long_description = readme.read()

with open('requirements.txt', 'r') as requirements_file:
  requirements_text = requirements_file.read()

requirements = requirements_text.split()

setuptools.setup(
      name='Opik',
      version='0.1',
      description='Opik - Open Source LLM Evaluation',
      url='',
      author='Gideon Mendels',
      author_email='gideon@comet.com',
      license='Apache 2',
      packages=setuptools.find_packages(),
      zip_safe=False,
      long_description_content_type="text/markdown",
      long_description="Congrats on cracking the riddle!",
      install_requires=requirements
)