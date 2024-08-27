# simple-app-with-pycalrissian

To create mamba environment please execute this command:
```
mamba create -n hello_world_pycalrissian -c conda-forge python=3.8 tomli unidep
mamba activate hello_world_pycalrissian
```
To create a module using pyproject.toml please execute the code below:
```
unidep install .
```

Create a simple python app to submit a job using `pycalrissian`. The app will only print a very basic hello world.



sudo snap install microk8s --classic
sudo usermod -a -G microk8s t2
sudo chown -R t2 ~/.kube
newgrp microk8s
microk8s status --wait-ready


microk8s enable dashboard
microk8s enable dns
microk8s enable registry
microk8s enable istio
