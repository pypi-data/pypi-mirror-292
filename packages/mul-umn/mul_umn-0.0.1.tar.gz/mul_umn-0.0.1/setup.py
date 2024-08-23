import setuptools

with open('README.md',"r") as fh:
    long_description = fh.read()

setuptools.setup(
                name="mul_umn",
                version="0.0.1",
                author="Umeshn7Codes",
                description="This is for testing the python package umn",
                long_description= long_description, #open(r"C:\1_ESI_INDIA\Work\2_SYSTEMS_AND_TOOLS\1_PYTHON_UMN\my_package_umn\README.md").read(),
                long_description_content_type="text/markdown",
                python_requires='>=3.6',

)
