import setuptools

PACKAGE_NAME = "whataspp-message-inforu-local"
# Since all PACAKGE_NAMEs are with an underscore, we don't need this. Why do we need it?
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.48',  # update only the minor version each time # https://pypi.org/project/whataspp-message-inforu-local/
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles whataspp_inforu_local Python",
    long_description="This is a package for sharing common whataspp_inforu_local function used in different repositories",
    long_description_content_type='text/markdown',
    url="https://github.com/circles-zone/whatsapp-message-inforu-local-python-package",
    # packages=setuptools.find_packages(),
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests>=2.31.0',
        'logger-local>=0.0.135',
        'message-local>=0.0.122',
        'python-sdk-remote>=0.0.93'
    ],
)
