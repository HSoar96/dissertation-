# Computing Artifacts

There are two computing artifacts I have produced in this repo.

Firstly there is a [main.py](HandTracking/main.py) that requires Python version 3.10 or above it has been tested on [Python 3.10.14](https://www.python.org/downloads/release/python-31014/) and Windows 11. You also require a WebCam connected in a top down orientation with sufficiently good lighting to assist in landmark tracking. It requires the following packages in order to run.

* [Open CV](https://pypi.org/project/opencv-python/)
* [Numpy](https://pypi.org/project/numpy/)
* [MediaPipe](https://pypi.org/project/mediapipe/)
* [PyTest](https://pypi.org/project/pytest/) * 


*Only if you wish to run [test_main.py](HandTracking/main.py)

There is also a unity project based in the [diss](diss) folder. This uses unity version [2021.3.25](https://unity.com/releases/editor/whats-new/2021.3.25).

When running the artifacts you must first run the unity program, before the python script to ensure correct functionality.