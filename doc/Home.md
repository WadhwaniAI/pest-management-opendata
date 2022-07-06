Welcome to the pest-management-opendata wiki!

# Quick Start

1. Ensure you have [Git](https://git-scm.com/downloads) and the [AWS
   CLI](https://aws.amazon.com/cli/) installed.
2. Clone the repository and download the data (10s of GB):

   ```bash
   $> git clone https://github.com/WadhwaniAI/pest-management-opendata.git
   $> cd pest-management-opendata
   $> aws s3 sync --no-progress s3://wadhwaniai-agri-opendata/ data/
   ```

The data directory contains images, along with compressed CSVs
containing bounding box information. It is likely that, because of
their format, the CSVs are not relevant for your modelling
toolkit. Please see the data documentation for details about the
format, and for resources that may make your processing easier.

# Background

The pest management project at the Wadhwani Institute for Artificial
Intelligence (Wadhwani AI) is an effort to help cotton farmers make
better pest management decisions. The project works by asking farmers
to install pheromone traps throughout their field designed to capture
various types of bollworms. Farmers and farming extension workers
periodically empty the trap and use a mobile application developed by
the institute to take photos of what they find. The application then
uses those photos to provide an action recommendation: whether a
pesticide spray is required, and if so the ideal composition and
concentration.

To go from mobile phone image to pesticide recommentation, the project
uses an object detection model trained to localise and label relevant
pests within an image. The S3 bucket around which this repository is
designed contains the data used to train and test that model.

## Further reading

* [Pest Management for Cotton
  Farming](https://www.wadhwaniai.org/programs/pest-management/)
* [Pest Management In Cotton Farms: An AI-System Case Study from the Global South](https://doi.org/10.1145/3394486.3403363) ([Open access](https://www.kdd.org/kdd2020/accepted-papers/view/pest-management-in-cotton-farms-an-ai-system-case-study-from-the-global-sou) provided by ACM SIGKDD)

# Questions, Comments, Issues

If you notice anything awry with our code, data, or documentation,
please let us know. Issues and pull requests are welcome. You can also
reach out through email:
[agri-ai@wadhwaniai.org](mailto:agri-ai@wadhwaniai.org).
