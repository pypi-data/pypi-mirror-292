# `ictasks`

This is a set of utilities to support running groups of small tasks as part of a single HPC batch submission at ICHEC.

The repo includes:

1) the `ictasks` package with tooling building blocks
2) Example `applications`, including snapshots of the ICHEC [Taskfarm](https://www.ichec.ie/academic/national-hpc/documentation/tutorials/task-farming) tool available on our HPC systems.

# Installing #

The package can be installed from PyPI:

``` shell
pip install ictasks
```

# Example Use #


``` shell
ictasks taskfarm --tasklist $PATH_TO_TASKLIST
```

# License #

This package is Coypright of the Irish Centre for High End Computing. It can be used under the terms of the GNU Public License (GPL). See the included `LICENSE.txt` file for details.





