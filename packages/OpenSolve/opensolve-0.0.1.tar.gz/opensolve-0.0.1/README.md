# OpenSolve Python Client

A simple programmatic solution for interacting with the [OpenSolve](https://open-solve.com) linear optimization service. [Read the complete, official docs here](https://open-solve.com/docs).

## Use a virtual environment

For every new project, create a new virtual environment. Read about them [here](https://docs.python.org/3/library/venv.html).

```
$ mkdir myProject && cd myProject
$ python3 -m venv myenv
```

Once you've created the virtual environment, activate it before beginning work.

```
$ cd path/to/myProject
$ source myenv/bin/activate
```

Once activated, you'll want to install all necessary packages (like the OpenSolve client) for your project.

## Install

Install the python client with 

```
(myenv) $ python3 -m pip install OpenSolve
```

The OpenSolve client only requires the [requests](https://requests.readthedocs.io/en/latest/) package. The minimum required version of Python is 3.7 (but the latest version of Python is always recommended).

## Using It

After [setting up your OpenSolve account](https://open-solve.com/docs), you'll be able to do a few cool things. 

### Submit jobs

```

from OpenSolve import Client
import time
import os  


# create a client object with your authentication details
c = Client.client('your_username', 'your_password')  


# submit a simple job (default options, no warmstart solution)
response = c.submit_job('path/to/your/problemfile.lp')  

```

### Check on a job

```
status = c.check_job()
```

### Pull the results of a completed job

``` 
results = c.pull_results()
```

### List current and past jobs

```
jobs = c.ls_jobs()
```


Get more details at the official [docs](https://open-solve.com/docs).