# Installation

The latest release of *NiBabies* is {{ release }}.

To view all available releases, refer to the [NiBabies PyPI page](https://pypi.org/project/nibabies/#history).

## Container Installation

Given its extensive dependencies, the easiest way to get up and running with *NiBabies* is by using a container service, such as [Docker](https://www.docker.com/get-started) or [Singularity](https://sylabs.io/singularity/).

### Working with Docker

Images are hosted on our [Docker Hub](https://hub.docker.com/r/nipreps/nibabies).
To pull an image, the specific version tag must be specified in order to pull the images.

:::{admonition} Example Docker build
:class: seealso

$ {{ dockerbuild }}
:::

There are also a few keyword tags, `latest` and `unstable`, that serve as special pointers.
`latest` points to the latest release (excluding any betas or release candidates).
`unstable` points to the most recent developmental change, and should only be used to test new features or fixes.

### Working with Singularity

The easiest way to create a Singularity image is to build from the [Docker](#working-with-docker) images hosted online.

:::{admonition} Example Singularity build
:class: seealso

$ {{ singbuild }}
:::

## Installing the nibabies-wrapper

The `nibabies-wrapper` is a lightweight Python tool to facilitate running `nibabies` within a container service.
To install or upgrade to the current release:
```
$ pip install --update nibabies-wrapper
```

For further details, see [](usage.md#using-the-nibabies-wrapper).

## Bare-metal Installation

If you would prefer to install this tool natively, you can refer the [Dockerfile](https://github.com/nipreps/nibabies/blob/master/Dockerfile) as a guide for all the dependencies.
