# simple-app-with-pycalrissian
Create a simple python app to submit a job using `pycalrissian`. The app will only print a very basic hello world.



To create mamba environment please execute this command:
```
mamba create -n hello_world_pycalrissian -c conda-forge python=3.8 twine
mamba activate hello_world_pycalrissian
```

## How to install the module:
To create a module using pyproject.toml with `PIP` dependencies please execute the code below:
```
pip install .    # this will create build folder
```

> Note: To create a module using pyproject.toml with `conda` dependencies in a particular channel please execute the code below:
>```
>unidep install .    # this will create build folder
>```





## How to create PYPI package(Optional):
You need to install some packages to create `dist/*` directory including `.whl` and `.tar.gz` files:

- Check the python and pip version by environment
```
## 
which python
which pip
```
- Update pip and install `dist` folder using the python specific version and `build` library:
EX:
```
/home/t2/micromamba/envs/hello_world_pycalrissian/bin/python -m pip install --upgrade pip
/home/t2/micromamba/envs/hello_world_pycalrissian/bin/pip install twine build
```
- Create API token on PYPI account and configure it under `$HOME/.pypirc` file as below:
```
[pypi]
  username = __token__
  password = pypi-...

``` 

- Create `dist` folder:
```
/home/t2/micromamba/envs/hello_world_pycalrissian/bin/python -m build
```

Now you need to publish your application packages on `PYPI`:
```
twine upload dist/*
```


## How to use the package in an isolated environment:
```
pip install hello-world-pycalrissian
hello-world-pycalrissian
```

<!-- ## How to use pycalrissian to submit a job:
sudo snap install microk8s --classic
sudo usermod -a -G microk8s t2
sudo chown -R t2 ~/.kube
newgrp microk8s
microk8s status --wait-ready


microk8s enable dashboard
microk8s enable dns
microk8s enable registry
microk8s enable istio -->