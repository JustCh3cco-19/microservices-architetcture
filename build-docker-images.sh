###################################
# .sh file to build every container
###################################

cd dummy-path-planning
bash build_image.sh

cd ..

cd dummy-computer-vision
bash build_image.sh

cd ..

cd dummy-high-level-control
bash build_image.sh

cd ..

cd dummy-slam
bash build_image.sh

cd ..