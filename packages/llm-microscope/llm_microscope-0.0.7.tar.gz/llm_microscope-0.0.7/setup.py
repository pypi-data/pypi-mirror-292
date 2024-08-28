import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

requirements = [
	"torch>=2.1.0",
	"matplotlib"
]

setuptools.setup(
	name="llm_microscope",
	version="0.0.7",
	author="Matvey Mikhalchuk",
	author_email="mikhalchuk@airi.net",
	description="Official implementation of the LLM-Microscope package functions for the paper",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/AIRI-Institute/LLM-Microscope",
	packages=setuptools.find_packages(),
	install_requires=requirements,
	classifiers=[
		"Programming Language :: Python :: 3.10",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.10',
	include_package_data=True
)

