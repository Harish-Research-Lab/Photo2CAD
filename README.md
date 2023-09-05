# Photo2CAD

## Copyright

Copyright (c) 2017-2021: Ajay Research Lab

## Cite us

How to cite us: A. B. Harish and A. R. Prasad, "Automated 3D solid reconstruction from 2D CAD using OpenCV," arXiv:2101.04248 (2021)

## About ACAD-Gen

Automated CAD model generator given 3 views of the model, namely front, side and top view to SCAD format. Further the SCAD file is used to generate stl and pcd format.

## Pre-Requisites

- Install OpenSCAD from https://www.openscad.org/downloads.html
- Install OpenCV package, used for image process
- Install Open3D package, used for displaying the cloud points generated at the end

## Shapes that are supported

Rectangle, square, regular triangle, regular pentagon, regular hexagon. This project has the same limitations of scad files, as we generate the scad file from the given 2D drawings.

## How to run!!

### Run on local machine

There are mainly 3 simple steps to convert your 2D drawings.

1. Run the dimensioning function in the function.py file with proper parameters

   > There is 3 arguments for Dimensioning function
   >
   > 1. userId, which will be used for naming of gerented intermediate and final 3D model files, so keep it unique if you are converting many models.
   > 2. view, which view it is, it can have either "front", "side" or "top" based on the image provided
   > 3. image, provide the image location for the given view

   This function will generated a image with highlighted length of one of the shapes provided and also the unit length to pixel for the highlighted line.

2. Next multiple the length of the highlighted line and multiply with the ratio given for respective views, we are doing this because the pixel density of different view might be different
3. Final step is to call the def Convert funtion which convert the drawing into 3D SCAD model.

   > There is 3 arguments for Dimensioning function
   >
   > 1. userId, which will be used for naming of gerented intermediate and final 3D model files, so keep it unique if you are converting many models.
   > 2. 3 images, provide the image location for all the view
   > 3. 3 ratios, provide the the length to pixel ratio for each view

   This funtion will generate the final scad file and provides the path for the same

Additional if you want to convert this scad file to other formats one can use openscad export function to export as other formats such as

> 3D formats
>
> - STL (both ASCII and Binary)
> - OFF
> - AMF [Note: Requires version 2019.05]
> - 3MF [Note: Requires version 2019.05]
>   2D formats
> - DXF
> - SVG [Note: Requires version 2019.05]

you can use gui for export or use cli way

```
openscad -o stl_filename(to format)  scad_filename(from format)
```

> Example
>
> openscad -o temp.stl exmaple.scad
> Ths is to convert scad to stl file in the same location

#### To generate point cloud

To generate the point cloud for the generated scad file, first we convert to stl format using openscad and use open3d library function

```python
#stl_filename is the stl location
mesh = o3d.io.read_triangle_mesh(stl_filename)
pointcloud = mesh.sample_points_poisson_disk(100000)
o3d.io.write_point_cloud(pcd_filename, pointcloud)
o3d.visualization.draw_geometries([pointcloud])
```

The full process in done in the main.py file for your reference using the few test bench examples provided. Here is the outline

```python
# Dimensioning

#front_image, side_image, top_image are the paths to those views
d1 = Dimensioning(userId, "front", front_image)
d2 = Dimensioning(userId, "side", side_image)
d3 = Dimensioning(userId, "top", top_image)
if(d1 == None or d2 == None or d3 == None):
    exit(0)

# Here 2 is the length of the highlighted line in front view
fratio = float(d1["ratio"]) * 2
# side view length of highlighted line
sratio = float(d2["ratio"]) * 2
# top view length of highlighted line
tratio = float(d3["ratio"]) * 2

# Convert to scad, which gives the output in the static folder
print(Convert(userId, front_image, side_image, top_image, fratio, sratio, tratio))

```

### Run using the Notebook

Follow the each code blocks in the same order, give proper image locations, dimensions and ratio. The examples in the notebook points to the test bench set make sure to change it. Also after converting to scad one can even convert the scad to point cloud have visual interactive window for the same. we use PyntCloud library for visualization.

One can change the point size and the background color of the interactive window in notebook
