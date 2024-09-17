from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='open-weather_LW',
    version='0.0',
    description='Openweather API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fuquyoma/Program5/tree/main/ЛР№3",
    packages=['open-weather_LW'], 
    author='Artem Gnevnov',
    author_email='gnevnov1996@mail.ru',
    zip_safe=False
)
