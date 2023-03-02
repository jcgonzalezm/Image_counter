# Containers Documentation

This is the documentation for the containers used on the Object_count solution.

## Overall installation

All conatiners are meant to be created using the the ./_containers/build_images.sh executable file as it will as well container the installation of requiered pacakges for the containers to reach from.

Tensorflow serving its build during the process, as it is requested by the minimum available product of the respective services, a separete executable file was included only for this purpose, For the other images, it was enough to pull them from Docker's hub.

WARNING: Most of the images where build using :latest as image refference so we may expecte some additional changes in the future

## Ports used

As day of this commit, this are the ports used on the containers:

* MongoDB: 27017
* MySQL: 3306 : 33060
* Torchserve: 8080 : 8081 : 8082
* Tensorflow serve: 8500 : 8501

