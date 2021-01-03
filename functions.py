import os
import shutil
import cv2
import numpy as np

from utils.tree import createtree
from utils.operation import *



def Dimensioning(userId,view,image):

    #Creating temp directory if not present
    os.makedirs('static/temp', exist_ok=True)
    #Getting user input from app
    img = cv2.imread(image,cv2.IMREAD_UNCHANGED)
    #Initialization
    ratio = 0
    shape = "unidentified"
    #Getting the size of image
    w,h,_=img.shape
    drawSize = int(h/300)
    # if(drawSize == 0):
    #     drawSize = 1
    #Convert image to grayscale
    imgrey = cv2.cvtColor(img.copy(),cv2.COLOR_BGR2GRAY)
    #Convert image to black and white
    ret, thresh = cv2.threshold(imgrey,127,255,cv2.THRESH_BINARY_INV)
    #Find contours
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    #Arrange the contours in descending order of area
    hierarchy,contours = zip(*sorted(zip(hierarchy[0],contours),key = lambda x: cv2.contourArea(x[1]),reverse=True))

    for i,c in enumerate(contours):
        #Get the outer most closed contour
        if(hierarchy[i][3] != -1  or (hierarchy[i][3] == -1 and hierarchy[i][2] == -1) ):
            M = cv2.moments(c)
            if(M["m00"] !=0):
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                #Getting the minimum area rectangle enclosing the contour
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                #Getting horizontal rectangle enclosing the contour
                x,y,w,h = cv2.boundingRect(c)
                
                # cv2.putText(img, "#{}".format(i), (box[0][0], box[0][1]), cv2.FONT_HERSHEY_SIMPLEX,
                #     textSize, (255, 0, 0), drawSize,cv2.LINE_AA)

                #detect Shape
                shape, cylinder_type = detect(c)
                                
                if(shape == "unidentified"):
                    continue
                
                if(shape=="triangle" or shape=="pentagon" or shape=="hexagon"):
                    img = cv2.drawContours(img, [box], 0, (0,0, 255), drawSize)
                # w is the width of the rectagle enclosing the circle, i.e diameter of the circle
                if(shape=="circle"):
                    # draw contours
                    img = cv2.rectangle(img,(x,y),(x+w,y+h),(0, 0, 255),drawSize)
                    cv2.line(img, (x,y), (x+w,y), (0,255, 0), 2)
                    ratio = 1/w
                else:
                    # draw contours
                    # img = cv2.drawContours(img, [box], 0, (0,0, 255), drawSize)
                    cv2.line(img, tuple(box[0]), tuple(box[1]), (0,255, 0), 2)
                    #Length per pixel
                    ratio = 1.0/rect[1][1]
                break
    
    #highlighted image path
    folder = 'static/temp/' + userId
    os.makedirs(folder, exist_ok=True)
    #Check whether file already exist and delete
    try:
        os.remove(folder + '/' + view + '.jpg')
    except: pass

    path_file = (folder + '/' + view + '.jpg')

    #reducing the image size
    small = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 
    cv2.imwrite(path_file,small)
    #Convert float to string
    ratio = str(ratio)
    #Json data to send
    data={'image': path_file,'shape': shape,'ratio': ratio}
#     plt.imshow(image)
#     plt.show()
    # display(Image(filename = path_file))
    return data

def Convert(userId, front_image, side_image, top_image, fratio, sratio, tratio):
    os.makedirs('static/' + userId, exist_ok=True)

    img_front = cv2.imread(front_image,cv2.IMREAD_UNCHANGED)
    img_side = cv2.imread(side_image,cv2.IMREAD_UNCHANGED)
    img_top = cv2.imread(top_image,cv2.IMREAD_UNCHANGED)

    fratio = float(fratio)
    sratio = float(sratio)
    tratio = float(tratio)
    filePath = "static/temp/"+userId
#Remove temp file created while dimensioning
    try:
        shutil.rmtree(filePath)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

    primitive = []
    #front
    object_front = valid_contours(img_front,"front",fratio)
    re_arrange(object_front,"front")
    
    #side
    object_side = valid_contours(img_side,"side",sratio)
    re_arrange(object_side,"side")

    #Top
    object_top = valid_contours(img_top,"top",tratio)
    re_arrange(object_top,"top")

    #Thershold error        
    minApprox = 0.05
    primitive = combining(object_front,object_side,object_top,minApprox)
    final = []
    for set in primitive:
        for shape in set:
            final.append(shape[0])
    
    #Check whether file already exist and delete
    try:
        os.remove('static/' + userId + "/" + userId + '.scad')
    except: pass

    #Generate scad file
    path_file = ('static/' + userId + "/" + userId + '.scad')
    #If the list is empty no shape has been detected
    if(len(final) == 0):
        path_file = 'static/error.txt'
        f = open(path_file, "w")
        f.write("Cannot determine the 3d geometry, check your files again!")
        f.close()
    createtree(final,path_file)

    return path_file


def Delete(userId, filetype):

    filePath = "static/temp/"+userId

#Remove temp file created while dimensioning
    if filetype == "temp":
        try:
            shutil.rmtree(filePath)
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))
    else:
        #Check whether scad file already exist and delete
        try:
            os.remove('static/' + userId + "/" + userId + '.scad')
        except: pass
    
    return "Done"
