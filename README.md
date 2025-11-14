# PyDOPTE

**Python Design of Parameter Tuning Experiments**

PyDOPTE is a Python library and framework for designing and conducting parameter tuning experiments for optimization algorithms. It provides a unified interface for multiple state-of-the-art parameter tuning methods and supports both internal (Python-based) and external (executable-based) algorithms.

## Features

- **Multiple Tuning Methods**: Support for various parameter tuning algorithms including:
  - CMA-ES (Covariance Matrix Adaptation Evolution Strategy)
  - GGA (Gender-based Genetic Algorithm)
  - IRace (Iterated Racing)
  - ParamILS (Parameter Iterative Local Search)
  - REVAC (Relevance Estimation and Value Calibration)
  - SMAC (Sequential Model-based Algorithm Configuration)
  - Random Search
  - Default parameter baseline

- **Flexible Algorithm Integration**: Tune both internal Python algorithms and external executables
- **Instance-based Tuning**: Support for tuning on multiple problem instances
- **Extensible Architecture**: Easy to add new tuning methods and algorithms
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

Here's a simple example of tuning an algorithm with PyDOPTE:

```python
import pydopte
from pydopte.Tuners.RandomTuner import RandomTuner
from pydopte import PathManager

# Initialize your algorithm (example with external algorithm)
algorithm = YourAlgorithm()
algorithm.SetTimeLimit(5.0)

# Set up the tuner
tuner = RandomTuner()
tunerParameters = tuner.GetDefinition().NewDefaultParameterSet()
tunerParameters["-eb"] = 1000  # Evaluation budget

# Define training instances
instances = ["instance1.dat", "instance2.dat", "instance3.dat"]

# Configure tuning task
tuner.SetAlgorithm(algorithm)
tuner.SetInstances(instances)

# Run tuning
result = tuner.Tune(tunerParameters)

print("Quality:", result["obj"])
print("Evaluations:", result["ops"])
print("Tuned parameters:", result["special"])
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

## Available Tuners

| Tuner | Description | Best For |
|-------|-------------|----------|
| **CMAESTuner** | Evolution strategy with covariance matrix adaptation | Continuous parameters |
| **GGATuner** | Gender-based genetic algorithm | Mixed parameter types |
| **IRaceTuner** | Iteratively races configurations | Large parameter spaces |
| **ParamILSTuner** | Iterative local search for parameters | Categorical parameters |
| **REVACTuner** | Relevance estimation and value calibration | Complex landscapes |
| **SMACTuner** | Sequential model-based configuration | Expensive evaluations |
| **RandomTuner** | Random search baseline | Baseline comparison |
| **DefaultTuner** | Uses default parameters | Baseline comparison |

## Creating Custom Algorithms

To tune your own algorithm, inherit from `BaseAlgorithm`:

```python
from pydopte.BaseAlgorithm import BaseAlgorithm
from pydopte.ParameterSet import ParameterSetDefinition

class MyAlgorithm(BaseAlgorithm):
    def __init__(self):
        BaseAlgorithm.__init__(self)
        # Define your parameters
        self._definition = ParameterSetDefinition()
        # Add parameters here

    def Evaluate(self, parameterSet):
        # Implement your algorithm evaluation
        # Return dict with "obj", "time", "ops" keys
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

This was originally developed for personal research use and represents an early Python project by the author. As such, it may not follow all modern Python conventions and best practices. The software is provided "as is" for anyone who might find it useful.

## Citation

If you use PyDOPTE in your research, please cite appropriately.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.
