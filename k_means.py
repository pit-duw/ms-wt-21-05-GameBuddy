import numpy as np
from PIL import Image
import random
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from colormath import color_conversions as ccv
import colormath.color_objects as co

######################### Settings #############################

image_path = "/home/pit/Pictures/74381609_p0.jpg"
n_clusters = 10 
n_iterations = 20
n_plot_points = 1500
verbose = False
img_size = (100,50)    # Image will be resized to this (while keeping original aspect ratio). Set None to keep original size. 

######################### Function Definitions #######################

# We want to use LAB colorspace because distance in this space more accurately reflects the distance perceived by a human observer than RGB distance
# See https://en.wikipedia.org/wiki/CIELAB_color_space
def rgb2lab(rgbarr):
    """
    Takes a 3-tuple / array of RGB values and returns an array with the 3 corresponding LAB values
    """
    rgbcol = co.sRGBColor(rgbarr[0], rgbarr[1], rgbarr[2])
    labcol = ccv.convert_color(rgbcol, co.LabColor)
    labarr = np.asarray(labcol.get_value_tuple())
    return labarr

def lab2rgb(labarr):
    """
    Takes a 3-tuple / array of LAB values and returns an array with the 3 corresponding RGB values
    """
    labcol = co.LabColor(labarr[0], labarr[1], labarr[2])
    rgbcol = ccv.convert_color(labcol, co.sRGBColor)
    rgbarr = np.asarray(rgbcol.get_value_tuple())
    return rgbarr

def get_distances(color, centers):
    """
    Calculates the distance between the given color and each of the current cluster centers
    """
    return [((color[0]-c[0])**2+(color[1]-c[1])**2+(color[2]-c[2])**2) for c in centers]


def assign_to_clusters(color_array, centers):
    """
    Assigns each point to the cluster with the nearest center.
    """
    clust = [[] for i in range(n_clusters)]
    clust_mult = [[] for i in range(n_clusters)]
    for i, color in enumerate(color_array):
        nearest_id = np.argmin(get_distances(color, centers))
        clust[nearest_id].append(color)
        clust_mult[nearest_id].append(mult_arr[i])
        
    return clust, clust_mult
    

def update_centers(clusters, clusters_mult):
    """
    Calculates the average position of the points within each cluster.
    """
    centers = np.zeros((n_clusters, 3))
    for i in range(n_clusters):
        if not clusters[i]:
            centers[i] = np.random.rand(3)*100
        else:
            n_points = np.sum(clusters_mult[i])
            centers[i] = np.sum(clusters[i]*np.array([clusters_mult[i]]*3).T, axis=0)/n_points
    return centers

######################### Actual Program ############################

with Image.open(image_path) as im:
    if img_size:
        im.thumbnail(img_size)
    img_arr = np.asarray(im)
    
# Loop over all pixels and create a dictionary with them as keys. Each dictionary entry is the number of occurences of that color. 
colors = {}
for line in img_arr:
    for px in line:
        # Dictionary keys cannot be tuples, so we create a 9-digit number from the rgb value
        px_int = int(1E6*px[0]+1E3*px[1]+px[2])
        if not px_int in colors:
            colors[px_int] = 1
        else:
            colors[px_int] += 1

# Transform the key values back into RGB values
color_arr = np.array([[int(col//1E6),int(col-(col//1E6)*1E6)//1E3,int(col-(col//1E3)*1E3)] for col in colors.keys()], dtype=np.float64)/255
mult_arr = np.fromiter(colors.values(), dtype=np.int64)

# Initialize clusters with center points at random positions
centers = np.random.rand(n_clusters,3)*100

# Convert all RGB colors to LAB space
color_arr = np.asarray([rgb2lab(c) for c in color_arr])
centers = np.asarray([rgb2lab(c) for c in centers])
            
for i in range(n_iterations):
    clusters, clusters_mult = assign_to_clusters(color_arr, centers)
    centers = update_centers(clusters, clusters_mult)
    if verbose:
        print(centers)

# Convert colors back to RGB
color_arr = np.asarray([lab2rgb(c) for c in color_arr])
centers = np.asarray([lab2rgb(c) for c in centers])

# Normalize, while taking care of floating point errors
color_arr = color_arr/max(np.max(color_arr), 1.0)*255
centers = centers/max(np.max(centers), 1.0)*255

######################### Plotting #########################

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

step = max(len(color_arr)//n_plot_points,1)
ax.scatter3D(color_arr[::step,0], color_arr[::step,1], color_arr[::step,2], c = color_arr[::step]/255, s = 12500/n_plot_points)


ax.scatter3D(centers[:,0], centers[:,1], centers[:,2], c="black", s=225, depthshade=False)
ax.scatter3D(centers[:,0], centers[:,1], centers[:,2], c="white", s=125, depthshade=False)
ax.scatter3D(centers[:,0], centers[:,1], centers[:,2], c=centers/255, s=50, depthshade=False)
plt.show()