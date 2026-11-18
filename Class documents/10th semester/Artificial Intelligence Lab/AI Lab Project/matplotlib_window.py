import json
import sys

import matplotlib

matplotlib.use("TkAgg")

import differentiator
import integrator
import inverting_amp
import non_inverting_amp
import summing_amp


SIMULATORS = {
    "inverting": inverting_amp,
    "non_inverting": non_inverting_amp,
    "integrator": integrator,
    "differentiator": differentiator,
    "summing": summing_amp,
}


def main():
    kind = sys.argv[1]
    inputs = json.loads(sys.argv[2])
    SIMULATORS[kind].run(inputs=inputs)


if __name__ == "__main__":
    main()
