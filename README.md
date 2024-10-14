# Wadhwani AI Pest Management Open Data

This repository acts as a gateway to the Wadhwani Institute for
Artificial Intelligence (Wadhwani AI) pest data set. The data set is
primarily intended for training pest recognition models. Such models
are used by Wadhwani AI to help cotton farmers make better pest
management decisions.

In addition to providing documentation about the data, this repository
contains scripts to format the data for consumption by popular
modelling frameworks. Please see the
[wiki](https://github.com/WadhwaniAI/pest-management-opendata/wiki)
for more information.

## Quick Start

1. Ensure you have [Git](https://git-scm.com/downloads) and the [AWS
   CLI](https://aws.amazon.com/cli/) installed.
2. Clone the repository and download the data (10s of GB); within
   a terminal emulator:

   ```bash
   $> git clone https://github.com/WadhwaniAI/pest-management-opendata.git
   $> cd pest-management-opendata
   $> aws s3 sync --no-sign-request s3://wadhwaniai-agri-opendata/ data/
   ```

The data directory will house images along with compressed CSVs
containing bounding box information for pests in those images. Because
of their format, it is unlikely that the CSVs are directly usable by
popular modelling toolkits. Users are free to write their own parsers
to bridge that gap, or to use one of the parsers provided in this
repository. Details on the data format, and the conversion scripts,
can be found in the
[wiki](https://github.com/WadhwaniAI/pest-management-opendata/wiki).

### Hugging Face

The dataset is also accesible via Hugging Face
[datasets](https://huggingface.co/docs/datasets):

```python
from datasets import load_dataset
dataset = load_dataset('wadhwani-ai/pest-management-opendata', streaming=True)
```

More information can be found in our [wiki](https://github.com/WadhwaniAI/pest-management-opendata/wiki/HuggingFace), and in the Hugging Face
[dataset
repository](https://huggingface.co/datasets/wadhwani-ai/pest-management-opendata).

# Questions, Comments, Issues

If something is not clear, or does not seem correct, please let us
know! This goes for all aspects of this repository: code, data, and
documentation. Issues and pull requests are welcome. You can also
reach out through email:
[agri-ai@wadhwaniai.org](mailto:agri-ai@wadhwaniai.org).
