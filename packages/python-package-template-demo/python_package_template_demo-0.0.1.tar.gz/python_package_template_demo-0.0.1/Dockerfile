FROM continuumio/miniconda3:latest

COPY . /package
WORKDIR /package

# install conda env
RUN conda env create -f environment.yml

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "python_package_template_demo", "python_package_template_demo"]