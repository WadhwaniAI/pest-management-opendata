# Wadhwani AI Pest Management Open Data

This repository acts as a gateway to the Wadhwani Institute for
Artificial Intelligence pest data set. The data set is primarily
intended for training pest recognition models. Such models are used by
the institutes to help cotton farmers make better pest management
decisions.

In addition to providing documentation about the data, this repository
also contains scripts to format the data for consumption by popular
modelling frameworks.  Please see the
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
   $> aws s3 sync --no-progress s3://wadhwaniai-agri-opendata/ data/
   ```

The data directory will house images along with compressed CSVs
containing bounding box information for pests in those those
images. Because of their format, it is unlikely that the CSVs are
directly usable in popular modelling toolkits. Users are free to write
their own parsers, or to use one of the parsers provided in this
repository to convert the data. Details on the data format, and the
conversion scripts, can be found in the wiki.

# Questions, Comments, Issues

If you notice anything awry with code, data, or documentation, please
let us know! Issues and pull requests are welcome. You can also reach
out through email:
[agri-ai@wadhwaniai.org](mailto:agri-ai@wadhwaniai.org).
