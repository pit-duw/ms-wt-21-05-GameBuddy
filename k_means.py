import numpy as np
from PIL import Image
import random
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

########### Settings ############

image_path = "/home/pit/Pictures/wave.png"
n_clusters = 10
distance_definition = 0 # for different options (linear, quadratic, human perception rgb, etc.)


colors = {}

with Image.open(image_path) as im:
    #im.thumbnail((60, 30))
    img_arr = np.asarray(im)
    
for line in img_arr:
    for px in line:
        px_int = int(1E6*px[0]+1E3*px[1]+px[2])
        if not px_int in colors:
            colors[px_int] = 1
        else:
            colors[px_int] += 1

color_arr = np.array([[int(col//1E6),int(col-(col//1E6)*1E6)//1E3,int(col-(col//1E3)*1E3)] for col in colors.keys()], dtype=np.int64)
mult_arr = np.fromiter(colors.values(), dtype=np.int64)

# Initialize clusters with center points at random positions
centers = np.random.rand(n_clusters,3)*255
#print(centers)
#centers = np.array([[194.98265828,  63.34664421, 145.74097142], [158.35524599, 174.57667375, 144.33882195]])

clusters = [[] for i in range(n_clusters)]
clusters_mult = [[] for i in range(n_clusters)]

def get_distances(color):
    return [((color[0]-c[0])**2+(color[1]-c[1])**2+(color[2]-c[2])**2) for c in centers]

def assign_to_clusters(color_array):
    """
    Assigns each point to the cluster with the nearest center.
    """
    clust = [[] for i in range(n_clusters)]
    clust_mult = [[] for i in range(n_clusters)]
    for i, color in enumerate(color_array):
        nearest_id = np.argmin(get_distances(color))
        #print(nearest_id)
        clust[nearest_id].append(color)
        clust_mult[nearest_id].append(mult_arr[i])
        
    return clust, clust_mult
    

def update_centers():
    """
    Calculates the average position of the points within each cluster.
    """
    for i in range(n_clusters):
        if not clusters[i]:
            centers[i] = np.random.rand(3)*255
        else:
            n_points = np.sum(clusters_mult[i])
            centers[i] = np.sum(clusters[i]*np.array([clusters_mult[i]]*3).T, axis=0)/n_points
            
for i in range(10):
    clusters, clusters_mult = assign_to_clusters(color_arr)
    update_centers()
    print(centers)

# 65.5, 63.5, 62.5

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter3D(color_arr[:,0], color_arr[:,1], color_arr[:,2], c = color_arr/255)
ax.scatter3D(centers[:,0], centers[:,1], centers[:,2], c="black", s=225, depthshade=False)
ax.scatter3D(centers[:,0], centers[:,1], centers[:,2], c="white", s=125, depthshade=False)
#ax.scatter3D(centers[:,0], centers[:,1], centers[:,2], c=(np.array([255,255,255])-centers)/255, s=50, depthshade=False)
ax.scatter3D(centers[:,0], centers[:,1], centers[:,2], c=centers/255, s=50, depthshade=False)
#ax.scatter3D(centers[:,0], centers[:,1], centers[:,2], color = "white", s=50, depthshade=True)
plt.show()