Welcome to the pest-management-opendata wiki!



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
* [Pest Management In Cotton Farms: An AI-System Case Study from the Global South](https://doi.org/10.1145/3394486.3403363)
  * An [open
  access](https://www.kdd.org/kdd2020/accepted-papers/view/pest-management-in-cotton-farms-an-ai-system-case-study-from-the-global-sou)
    version of this article is provided by ACM SIGKDD

# Dependencies

## Python

Python scripts in this repository are known to work on Python
3.8+. For library dependencies see the requrements.txt file at the top
of this repository. Detectron2 has a non-standard [installation
process](https://detectron2.readthedocs.io/en/latest/tutorials/install.html). If
you do not intend to use that library for modelling, you can safetly
ignore that requirement.

## Terminal

Shell scripts in this repository were designed under Bash. They are
known to work if you are using standard GNU Bash utils. For Linux
users this should not be an issue. For Mac users this generally means
[Homebrew](https://brew.sh/) versions of Terminal programs; notably
[coreutils](https://formulae.brew.sh/formula/coreutils).
