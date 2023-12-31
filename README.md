## Note: This analysis is just for fun, simply to get an idea of how the Nearest Neighbour analysis is done in python. So, the result of this analysis does not exactly reflects the actual condition of the municipality taken into consideration.

# Nearest Neighbour analysis
This is a map of showing buildings and stops in Molde Municipality which gives information about the distance of each buildings from their closest stops. The distance is calculated in meter and the distance attribute pops up when you hover the mouse over the building points. The distance is linear. The data of buildings is taken from the website: https://www.geonorge.no/ and the busstop points are extracted from Open Steet Map service website: https://openstreetmap.org/.
# Method:
BallTree function from scikit-learn library in Python is used for this analysis. The python file namely: Closest_busstops.py is also uploaded in this repository.

# Analysis:
Descriptive statistics of the analysis are as follows:
![image](https://github.com/manojpariyar/Closest_stops/assets/114010808/13f0e2e1-7e65-4ea5-b99d-c423be946ec4)


16498 buildings are included for the analysis. The average distance between the buildings and the stops is 340 meter. The closest and the farthest distance between the building and the busstop are 2.405078 m and 7112.685417 m respectively. About 25 % of buildings lies within a distance of 101 meter from the busstops, 50 % within 165 meter from the busstops and 75 % within 278 meter from the busstops.

# Links visualization between the buildings and the stops:
![BuildingLinksToStop](https://github.com/manojpariyar/Closest_stops/assets/114010808/93dcda69-f588-46fa-b8dd-82407e0f0a19)

# Actual map:
![Closest_busstops](https://github.com/manojpariyar/Closest_stops/assets/114010808/fee1d330-e7c0-41d8-87b3-6aa0e825e226)
