from setuptools import setup, find_packages

# Read the README file for the long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='webp-imagefield',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'Django>=3.0',
        'Pillow>=8.0.0'
    ],
    include_package_data=True,
    description='A custom Django ImageField that automatically converts images to WebP format.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Mehdi Shoqeyb',
    author_email='mehdi.shoqeyb@gmail.com',
    url='https://github.com/mehdi-shoqeyb/webp-image-field',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',  # Update as your project matures
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
    python_requires='>=3.6',
)
