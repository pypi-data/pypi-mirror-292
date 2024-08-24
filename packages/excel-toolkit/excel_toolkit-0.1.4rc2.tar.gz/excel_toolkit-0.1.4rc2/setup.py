from setuptools import setup, find_packages

setup(
    author= "Dear Norathee",
    description="package to help you automate Excel files' tasks",
    name="excel_toolkit",
    version="0.1.4rc2",
    packages=find_packages(),
    license="MIT",
    install_requires=["xlwings","openpyxl","pyxlsb","pandas","py_string_tool>=0.1.4", "python_wizard", "os_toolkit", ],
    

)