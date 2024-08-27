FROM ubuntu:latest
ARG DEBIAN_FRONTEND=noninteractive
ENV APP_ENV=hello_world_pycalrissian

SHELL ["/bin/bash", "-c"]
RUN apt-get update -yq                                                                                                      && \
    apt-get install -y ca-certificates file wget bash bzip2 sudo                                                 && \
    apt-get clean autoremove --yes                                                                                     && \
    rm -rf /var/lib/{apt,dpkg,cache,log}


ARG USERNAME=linus
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# # Create the user
# RUN groupadd --gid $USER_GID $USERNAME                                                                                      && \
#     useradd --uid $USER_UID --gid $USER_GID -m $USERNAME                                                                    && \
#     echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME                                                     && \
#     chmod 0440 /etc/sudoers.d/$USERNAME                             

ENV BASH_ENV=~/.bashrc \
    MAMBA_ROOT_PREFIX=/home/$USERNAME/conda \
    PYTHON_VERSION=3.8 \
    PATH=$PATH:/home/$USERNAME/conda/envs/$APP_ENV/bin:/home/$USERNAME/conda/envs/$APP_ENV/snap/bin

COPY --from=docker.io/mambaorg/micromamba:alpine /bin/micromamba /bin/micromamba
RUN micromamba shell init -s bash -p ~/micromamba
COPY --chown=$USERNAME:$USER_GID . /tmp

# Create the environment and install dependencies
RUN micromamba create -n ${APP_ENV} -c conda-forge -c terradue python=${PYTHON_VERSION} tomli unidep && \
    micromamba run -n ${APP_ENV} unidep install /tmp && \
    micromamba clean --all --yes                                                                                                    

# Activate environment
ENV CONDA_DEFAULT_ENV=$APP_ENV \
    ENV_NAME=$APP_ENV \
    CONDA_PROMPT_MODIFIER=($APP_ENV)