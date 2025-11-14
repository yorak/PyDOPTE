# PyDOPTE

**Python Design of Parameter Tuning Experiments**

## ⚠️ IMPORTANT NOTICE ⚠️

**This project has not been actively maintained since 2018.** The included configurator tool versions (SMAC, ParamILS, IRace, etc.) are seriously outdated. While the framework itself may still be useful for understanding automatic algorithm configuration concepts or for educational purposes, users should be aware that:

- Python 2.x is no longer supported (EOL January 2020)
- External configurator tools have had major updates and improvements since 2018
- Modern alternatives and updated versions of these tools are available elsewhere
- Dependencies and external tools may no longer work as expected on modern systems

**For production use, please consider modern alternatives such as:**
- [SMAC3](https://github.com/automl/SMAC3) - Latest version of SMAC
- [irace](https://cran.r-project.org/web/packages/irace/) - Updated IRace package
- [Optuna](https://optuna.org/) - Modern hyperparameter optimization framework
- [HpBandSter](https://github.com/automl/HpBandSter) - Hyperparameter optimization with Bayesian approaches

---

## About

PyDOPTE is a Python library and framework for **automatic algorithm configuration** (also known as **parameter tuning** or **hyperparameter optimization**). It provides a unified interface for multiple state-of-the-art configuration methods and supports both internal (Python-based) and external (executable-based) algorithms.

**For Evolutionary Computing Researchers:** PyDOPTE offers a framework for parameter tuning of evolutionary algorithms and metaheuristics, with support for instance-based training and validation.

**For Operations Research & Optimization Practitioners:** PyDOPTE provides tools for automatic algorithm configuration (AAC) of optimization solvers, supporting the experimental design and comparison of different configurators on your problem instances.

## Features

- **Multiple Configuration Methods**: Support for various automatic algorithm configurators (AAC) / parameter tuning algorithms including:
  - CMA-ES (Covariance Matrix Adaptation Evolution Strategy)
  - GGA (Gender-based Genetic Algorithm)
  - IRace (Iterated Racing)
  - ParamILS (Parameter Iterative Local Search)
  - REVAC (Relevance Estimation and Value Calibration)
  - SMAC (Sequential Model-based Algorithm Configuration)
  - Random Search
  - Default parameter baseline

- **Flexible Algorithm Integration**: Configure/tune both internal Python algorithms and external executables
- **Instance-based Configuration**: Support for training on multiple problem instances with separate validation sets
- **Extensible Architecture**: Easy to add new configurators and target algorithms
- **Experiment Management**: Built-in tools for running batch experiments and managing results

## Installation

### Prerequisites

- Python 2.7+ (Note: This was originally written for Python 2.x)
- NumPy
- Additional dependencies depending on which tuners you want to use

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yorak/PyDOPTE.git
cd PyDOPTE
```

2. Add PyDOPTE to your PYTHONPATH:
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/PyDOPTE
```

For permanent setup, add the above line to your `~/.bashrc` or `~/.bash_profile`.

## Quick Start

Here's a simple example of configuring/tuning an algorithm with PyDOPTE:

```python
import pydopte
from pydopte.Tuners.RandomTuner import RandomTuner
from pydopte import PathManager

# Initialize your target algorithm (the algorithm to be configured)
# This could be an evolutionary algorithm, metaheuristic, or optimization solver
algorithm = YourAlgorithm()
algorithm.SetTimeLimit(5.0)

# Set up the configurator/tuner
tuner = RandomTuner()
tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
tunerParameters["-eb"] = 1000  # Evaluation budget (number of configurations to try)

# Define training instances (problem instances for algorithm configuration)
instances = ["instance1.dat", "instance2.dat", "instance3.dat"]

# Configure the configuration task
tuner.SetAlgorithm(algorithm)
tuner.SetInstances(instances)

# Run the configuration/tuning process
result = tuner.Tune(tunerParameters)

print("Quality:", result["obj"])
print("Evaluations:", result["ops"])
print("Configured/tuned parameters:", result["special"])
```

## Project Structure

```
PyDOPTE/
├── pydopte/              # Main library code
│   ├── Tuners/           # Parameter tuning implementations
│   │   ├── CMAESTuner.py
│   │   ├── GGATuner.py
│   │   ├── IRaceTuner.py
│   │   ├── ParamILSTuner.py
│   │   ├── REVACTuner.py
│   │   ├── RandomTuner.py
│   │   ├── SMACTuner.py
│   │   └── DefaultTuner.py
│   ├── Algorithms/       # Example algorithm implementations
│   ├── BaseAlgorithm.py  # Base class for algorithms
│   ├── BaseTuner.py      # Base class for tuners
│   ├── ParameterSet.py   # Parameter handling utilities
│   └── PathManager.py    # Path management utilities
├── experiments/          # Example experiments and templates
├── tests/                # Unit tests
├── tools/                # Additional utilities
├── results/              # Results storage (generated)
└── docs/                 # Documentation

```

## Available Configurators / Tuners

| Configurator | Description | Best For |
|--------------|-------------|----------|
| **CMAESTuner** | Evolution strategy with covariance matrix adaptation | Continuous parameters, numerical optimization |
| **GGATuner** | Gender-based genetic algorithm | Mixed parameter types, general purpose |
| **IRaceTuner** | Iteratively races configurations | Large parameter spaces, expensive evaluations |
| **ParamILSTuner** | Iterative local search for parameters | Categorical/discrete parameters |
| **REVACTuner** | Relevance estimation and value calibration | Complex response surfaces |
| **SMACTuner** | Sequential model-based algorithm configuration | Expensive evaluations, mixed parameter types |
| **RandomTuner** | Random search baseline | Baseline comparison, quick exploration |
| **DefaultTuner** | Uses default parameters only | Baseline comparison |

## Creating Custom Target Algorithms

To configure/tune your own algorithm (e.g., your evolutionary algorithm, metaheuristic, or optimization solver), inherit from `BaseAlgorithm`:

```python
from pydopte.BaseAlgorithm import BaseAlgorithm
from pydopte.ParameterSet import ParameterSetDefinition

class MyAlgorithm(BaseAlgorithm):
    def __init__(self):
        BaseAlgorithm.__init__(self)
        # Define your algorithm's configurable parameters
        self._definition = ParameterSetDefinition()
        # Add parameters here (continuous, discrete, categorical, etc.)

    def Evaluate(self, parameterSet):
        # Implement your algorithm evaluation on a problem instance
        # parameterSet is a dictionary of parameter values to test
        # Return dict with "obj" (solution quality), "time" (runtime), "ops" (evaluations)
        return {"obj": objective_value, "time": runtime, "ops": evaluations}
```

## Running Experiments

PyDOPTE includes experiment templates and batch scripts:

```bash
# Run a single experiment
python experiments/experiment_template.py

# Run batch experiments
cd experiments
./run_batch_template.sh
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

## Documentation

Additional documentation can be found in the `docs/` directory.

## License

MIT License - Copyright (c) 2022 Jussi Rasku

See [LICENSE](LICENSE) for full details.

## Author's Note

This was originally developed in 2011-2018 for personal research use and represents an early Python project by the author. As such, it may not follow all modern Python conventions and best practices. **This code has not been maintained since 2018**, and the integrated external configurator tools are seriously outdated.

The software is provided "as is" primarily for:
- Educational purposes and understanding automatic algorithm configuration concepts
- Historical reference for research reproducibility
- Anyone who might find the framework architecture useful

**For current research or production use, please use modern alternatives** mentioned in the notice at the top of this README.

## Citation

If you use PyDOPTE in your research, please consider citing one of the following publications where this framework was used:

```bibtex
@article{rasku2019automatic,
  title={On automatic algorithm configuration of vehicle routing problem solvers},
  author={Rasku, Jussi and Musliu, Nysret and K{\"a}rkk{\"a}inen, Tommi},
  journal={Journal on Vehicle Routing Algorithms},
  volume={2},
  number={1},
  pages={1--22},
  year={2019}
}

@inproceedings{rasku2015automatic,
  title={Automatic customization framework for efficient vehicle routing system deployment},
  author={Rasku, Jussi and Puranen, Teemu and Kalmbach, Anssi and K{\"a}rkk{\"a}inen, Tommi},
  booktitle={European Congress on Computational Methods in Applied Sciences and Engineering},
  pages={105--120},
  year={2015},
  publisher={Springer International Publishing}
}

@incollection{rasku2014automating,
  title={Automating the parameter selection in VRP: an off-line parameter tuning tool comparison},
  author={Rasku, Jussi and Musliu, Nysret and K{\"a}rkk{\"a}inen, Tommi},
  booktitle={Modeling, Simulation and Optimization for Science and Technology},
  pages={191--209},
  year={2014},
  publisher={Springer Netherlands}
}
```

**Publications:**

- Rasku, J., Musliu, N., & Kärkkäinen, T. (2019). On automatic algorithm configuration of vehicle routing problem solvers. *Journal on Vehicle Routing Algorithms*, 2(1), 1-22.

- Rasku, J., Puranen, T., Kalmbach, A., & Kärkkäinen, T. (2015). Automatic customization framework for efficient vehicle routing system deployment. In *European Congress on Computational Methods in Applied Sciences and Engineering* (pp. 105-120). Cham: Springer International Publishing.

- Rasku, J., Musliu, N., & Kärkkäinen, T. (2014). Automating the parameter selection in VRP: an off-line parameter tuning tool comparison. In *Modeling, Simulation and Optimization for Science and Technology* (pp. 191-209). Dordrecht: Springer Netherlands.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.
