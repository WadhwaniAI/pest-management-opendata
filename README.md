# Wadhwani AI Pest Management Open Data

This repository acts as a gateway to the Wadhwani Institute for
Artificial Intelligence pest data set. The data set is primarily
intended for training pest recognition models at the institute, which
in turn are used to help cotton farmers make better pest management
decisions.

In addition to providing documentation about the data and its format,
the repository also contains scripts to format the data for
consumption by popular neural network frameworks.

## Quick Start

1. Ensure you have [Git](https://git-scm.com/downloads) and the [AWS
   CLI](https://aws.amazon.com/cli/) installed.
2. Clone the repository and download the data (10s of GB); within
   a terminal emulator:

   ```bash
   $> git clone https://github.com/WadhwaniAI/pest-management-opendata.git
   $> cd pest-management-opendata
   $> aws s3 sync --no-progress s3://wadhwaniai-agri-opendata/ data/
   ```

The data directory contains images, along with compressed CSVs
containing bounding box information. It is likely that, because of
their format, the CSVs are not directly usable in your modelling
toolkit. Please see the data documentation for details about the
format, and for resources that may make your processing easier.

# Questions, Comments, Issues

If you notice anything awry with our code, data, or documentation,
please let us know. Issues and pull requests are welcome. You can also
reach out through email:
[agri-ai@wadhwaniai.org](mailto:agri-ai@wadhwaniai.org).

Please see the
[wiki](https://github.com/WadhwaniAI/pest-management-opendata/wiki)
for more information.
