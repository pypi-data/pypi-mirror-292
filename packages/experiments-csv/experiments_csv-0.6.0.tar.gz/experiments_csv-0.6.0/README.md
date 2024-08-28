# experiments_csv - experiment tracking via CSV files
[![PyPI version](https://badge.fury.io/py/experiments_csv.svg)](https://badge.fury.io/py/experiments_csv)

## Motivation
You run an experiments with various input parameters. You check various input combinations and run the experiment on each combination.

Suddenly, during one of the runs, the program crashes. You have to restart the experiment for the current and future inputs, but you do not want to repeat it for all previous inputs.

## Solution
`experiments_csv` saves all the experiment input and output data into a CSV file. When you restart the experiment, it reads the CSV file and notes all the input combinations for which the experiment already completed. It then automatically skips these input combinations.

## Installation

Basic installation:

```
    pip install experiments-csv
```

Installation with plotting ability:

```
    pip install experiments-csv[plotting]
```



## Usage
See the demo programs in the [examples](examples/) folder for usage examples. In detail, you should:

1. Write a function for running a single instance of the experiment.
The function may take any number of arguments as inputs.
It should return a dict with any number of arguments as outputs.
For example:

```
    def fair_division_algorithm(num_of_agents:int, num_of_items:int, threshold:float, criterion:str):
        # ...
        # Run the fair division algorithm with the given parameters
        # ...
        return {
            "runtime": runtime,
            "max_value": max(values),
            "min_value": min(values)
        }
```

2. Decide what ranges you want for your input parameters, for example:

```
    input_ranges = {
        "num_of_agents": [2, 3, 4],
        "num_of_items": range(2,10),
        "threshold": [0.5],
        "criterion": ["proportionality", "envy-freeness"]
    }
```

3. Create an Experiment object. It takes as arguments the folder for the experiment results, the experiment file name, and the folder for backups:

```
    import experiments_csv
    ex = experiments_csv.Experiment("results/", "results.csv", "results/backups")
```

4. Run the experiment:

```
   ex.run(fair_division_algorithm, input_ranges)
```

This loops over all combinations of inputs in the ranges you passed (the Cartesian product of the ranges in input_ranges), calls the single-instance function, and records the results in the given CSV file. The CSV file will have a column for every input and output (in the example: num_of_agents, num_of_items, threshold, criterion, runtime, min_value, max_value), and a single row for every run.

If the experiment stops abruptly due to an error, you can re-run the same code, and it will not repeat the experiments with the combinations of arguments it already completed - it will only run the experiments for the combinations not done yet.

If you do want to restart the experiment from scratch, either manually delete the CSV file, or use a new CSV file with a different name, or do

```
   ex.clear_previous_results()
```

To log the inputs and outputs during run, you can do:
```
    ex.logger.setLevel(logging.INFO)
```

## Plotting

To plot the results, you can use the `plot_results` function, for example:

```
    from matplotlib import pyplot as plt
    experiments_csv.plot_results(plt, "results.csv", filter={"algorithm": "abc"}, xcolumn="size", ycolumn="runtime", zcolumn="bits")
```

See the [demo programs](demo/) for usage examples.