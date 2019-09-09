import setuptools

setuptools.setup(
    name="nazgul",
    version="1.0",
    tests_require=["pytest"],
    include_package_data=True,
    zip_safe=False,
    packages=setuptools.find_packages(),
)
