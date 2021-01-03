import cv2
from .shape import node
import math

#Round up
def round_up(n, decimals=2):
    multiplier = 10 ** decimals
    n = math.ceil(n * multiplier) / multiplier
    return n

#To rearrange the parts in the views, like for front store all the parts such that the center of the shape is arranged in descending order of x pixel value
#otherwise do ascending order in side and top
def re_arrange(objects,type):
    if(type == "front"):
        objects.sort(key = lambda x: x[0][1][0],reverse = True)
    else:
        objects.sort(key = lambda x: x[0][1][0])

def draw_contour(img, out):
     #Converting into greyscale
    imgrey = cv2.cvtColor(img.copy(),cv2.COLOR_BGR2GRAY)
    #COnverting into greyscale image to black and white image
    ret, thresh = cv2.threshold(imgrey,127,255,cv2.THRESH_BINARY_INV)
    #Finding contours
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    #REarranging in descending order of area
    hierarchy,contours = zip(*sorted(zip(hierarchy[0],contours),key = lambda x: cv2.contourArea(x[1]),reverse=True))

    for i,c in enumerate(contours):


         if ( hierarchy[i][3] != -1 or (hierarchy[i][3] == -1 and hierarchy[i][2] == -1) ):
            M = cv2.moments(c)
            if(M["m00"] !=0):
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                area = cv2.contourArea(c)
                rect = cv2.minAreaRect(c)

                #Ignoring small areas
                # if(area <= 4):
                #     break
                
                # calculate coordinates of the minimum area rectangle
                box = cv2.boxPoints(rect)
                # draw the countour number on the image
                # cv2.putText(img, "#{}".format( i), (box[0][0], box[0][1]), cv2.FONT_HERSHEY_SIMPLEX,
                #     1.0, (255, 0, 0), 1)
                # draw contours
                cv2.drawContours(img, [c], 0, (0,0, 255), 1)
    cv2.imwrite(out,img)

def add_part(objects,part,pos,type,ratio):

    #Translate based on the centers of the given shape with largest shape
    if(type == "front"):
        part[0].translate(round_up((part[1][0]-pos[0]) * ratio) , 0 , round_up((pos[1]-part[1][1]) * ratio ))
    if(type == "side"):
        part[0].translate(0 , round_up((part[1][0]-pos[0]) * ratio)  , round_up((pos[1]-part[1][1]) * ratio ))
    if(type == "top"):
        part[0].translate(round_up((part[1][1]-pos[1]) * ratio) , round_up((part[1][0]-pos[0]) * ratio) , 0 )

    #Search for the parent shape and place it inside that parent list
    for i,object in enumerate(objects):
        if(cv2.pointPolygonTest(object[0][2],part[1],False)>=0):
            part[0].operation = "difference"            
            #Adding in position
            object.append(part)
            return

    #If shape not found his parent, make a new list making it has parent 
    objects.append([part])
    return

def combining(front_parts,side_parts,top_parts,roundOffApprox):
#All the views are thought to be seen in y direction
#For cube the "l" is length that is length of the rectangle/sqaure, "h" is height that is nothing but breadth of rectangle/sqaure,
# "b" is the breath(thickness in y direction) of the cube
# Cylinder will be upright position along z-axis(i.e when no ration is applied)

#Looping through the Different parent child lists
    for i,front in enumerate(front_parts):
        first = 0
        #looping through all the parts of a parent and its child
        for j,part_f in enumerate(front):
            #part length is usually 5 - includes shape object,center,contour,height and width, if its six the shape is already considered and finalised
            if(len(part_f) >= 6):
                continue
            #Give the width of the parent to all its child when the parent is width found from side view
            if(first == 1):
                #If the child shape is cube
                if(part_f[0].shape == "cube"):
                    #Parent is also cube
                    
                    if(front[0][0].shape == "cube"):
                        part_f[0].b = front[0][0].b
                    else:
                        part_f[0].b = front[0][0].h
                    #when the parent is rotated in z axis
                    if(front[0][0].rz!=0):
                        part_f[0].b = front[0][3]
                #If the child is cylinder
                if(part_f[0].shape == "cylinder"):
                    #Parent is cube
                    if(front[0][0].shape == "cube"):
                        part_f[0].h = front[0][0].b
                    else:
                        part_f[0].h = front[0][0].h
                    #when the parent is rotated in z axis
                    if(front[0][0].rz!=0):
                        part_f[0].h = front[0][3]
            #For checking whether the front shape is visible in side
            found = 0
            #Search side view
            for k,side in enumerate(side_parts):
                #For adding rest of the shapes in side view list, once a shape is found
                add_rest = 0
                for l,part_s in enumerate(side):
                    # ADD inner parts of side view only visible from side view and making sure the same shape is not added again once the shape is available in side view
                    if(add_rest == 1 and part_s[3]!=-1): 
                        #Increasing the size of parts list
                        part_s.append("used")
                        part_s[3]=-1
                        #Giving the x translation
                        part_s[0].tx = part_f[0].tx
                        #If the shape is cylinder give height to it
                        if(part_s[0].shape == "cylinder"):
                            part_s[0].h = part_f[4]
                        #If its a cube give breadth
                        elif(part_s[0].shape == "cube"):
                            part_s[0].b = part_f[4]
                        front.append(part_s)

                        continue
                    #check whether the height in front view is same in side view
                    if(abs(part_f[3]-part_s[3]) < roundOffApprox and found==0):
                        #If the shape is found in side view     
                        found = 1
                        #If its a parent in front view
                        if(j == 0):
                            first = 1
                        #If the side shape is not parent then its protruding, so make the operation as union
                        if(l!=0):
                            part_s[0].operation="union"
                        #If Front view is cube
                        if(part_f[0].shape =="cube"):
                            #If side view is also cube
                            if(part_s[0].shape == "cube"):
                                #Check whether it is cylinder in top view or if there is any rotation in z-axis if the top view is also found to be cube

                                for top in top_parts:
                                    for m,part_t in enumerate(top):
                                        #Checking whether the shape is available in top view by comparing the height in top view 
                                        # with the width in front view, as all the shapes are considered to be viewed in the direction of y-axis we need to compare 
                                        # the height in top view with width in front view
                                        if(abs(part_t[3] - part_f[4]) < roundOffApprox and len(part_t)==5):
                                           
                                            #If the shape in top view is child it must be protruding from it's parent to be visible in front view, so 
                                            # we change the operation of the shape of the top view to union operation 
                                            if(m!=0):
                                                part_t[0].operation = "union"
                                            #If it is a parent make the operation None
                                            if(j==0):  
                                                part_t[0].operation = "None"
                                            #If its a circle from top view replace the front view in "front_part" list with top view shape, while giving it a height
                                            #  and z-translate
                                            if(part_t[0].shape == "cylinder"):
                                                #Providing height and z-tranzlate for the shape in top view
                                                part_t[0].h = part_f[0].h
                                                part_t[0].tz = part_f[0].tz
                                                #Get to know the position of which parent we are adding in "front_part" so that the remaining shapes
                                                # in the top view after this shape can be added later into the "front_part" list 
                                                part_t[1] = i
                                                #Marking that the shape in the top view is used
                                                part_t[2] = -1
                                                part_t.append("used")
                                                #Replace the shape in the front view by the shape obtained from top view                                             
                                                part_f[0] = part_t[0]
                                                #Mark that the side view is used
                                                part_s[3] = -1
                                                #Giving signal to add rest of the child in side view after the current shape
                                                add_rest = 1
                                                break
                                            if(part_t[0].shape == "cube" and part_s[0].ry == 0 and part_f[0].ry == 0 and part_t[0].rz != 0 and abs(part_t[0].rz) != 90):
                                                #For the top view, cube will be rotated along x-axis so we need to provide them breadth rather
                                                #  than height 
                                                part_t[0].b = part_f[0].h
                                                #Provide the z-translation from top view
                                                part_t[0].tz = part_f[0].tz
                                                #Get to know the position of which parent we are adding in "front_part" so that the remaining shapes
                                                # in the top view after this shape can be added later into the "front_part" list 
                                                part_t[1] = i
                                                #Marking that the shape in the top view is used
                                                part_t[2] = -1
                                                part_t.append("used")
                                                #Replace the shape in the front view by the shape obtained from top view
                                                part_f[0] = part_t[0]
                                                #giving the thickness of the shape, helpful when the parent is rotated along z axis
                                                part_f[3] =part_t[3]
                                                #Mark that the side view is used
                                                part_s[3] = -1
                                                #Giving signal to add rest of the child in side view after the current shape
                                                add_rest = 1
                                                break
                                    else:
                                        #Using for else construct, which helps here to continue to traverse through the list until the shape is found in top view 
                                        # or it exists from the top_part loop 
                                        continue
                                    #Reaches here if counterpart for the front shape is in top view
                                    break
                            #If the shape was found in top view and we if we replaced with top view, then skip rest of the work below it
                            if(part_s[3] == -1):
                                continue

                            #If the side view is cylinder
                            if(part_s[0].shape == "cylinder"):
                                #Get height of the cylinder
                                part_s[0].h = part_f[0].l
                                #Get x-translation
                                part_s[0].tx = part_f[0].tx
                                #If the cube is front view cube is rotated along y axis
                                part_s[0].ry = part_f[0].ry
                                #Replace front view by side
                                
                                if(j==0):  #If it is a parent make the operation None
                                    part_s[0].operation = "None"
                                    
                                part_f[0] = part_s[0]
                                part_s[3] = -1
                                add_rest = 1
                                continue
                            
                            #If the side view is cube
                            if(part_s[0].shape == "cube"):
                                #If the cube is rotated in front view i.e along y axis, then just provide the thickness and y translation
                                if(part_f[0].ry != 0 or part_s[0].ry == 0):
                                    part_f[0].b = part_s[0].l
                                    part_f[0].ty = part_s[0].ty
                                    part_s[3] = -1
                                    add_rest = 1
                                    continue
                                else:
                                    #Replacing front view by side view 
                                    #thickness of the view
                                    part_s[0].b = part_f[0].l
                                    # x translation
                                    part_s[0].tx = part_f[0].tx
                                    #Replace front view by side view
                                    part_f[0] = part_s[0]
                                    part_s[3] = -1
                                    add_rest = 1
                                    continue

                        #If the shape in Front View is cylinder 
                        if(part_f[0].shape == "cylinder"):
                            # If the side view is cube, which is obvious but still checking
                            if(part_s[0].shape == "cube"):
                                # The thickness/height for the cylinder is given by the length of the cube in side view(as side view shapes are rotated 
                                # in 90 about z-axis) and also give the y-translation
                                part_f[0].h = part_s[0].l
                                part_f[0].ty = part_s[0].ty
                                #If the cube is rotated along x axis, by x axis rotation in side view is given by y axis as we are rotating the side view 
                                # by 90 along z axis
                                part_f[0].rx = part_s[0].ry 

                        #Side shape is used
                        part_s[3] = -1
                        #Add the rest of the shapes in side view for this parent/ this child's parent 
                        add_rest = 1
                        continue
                #If the shape in front view is already found, dont check any other shapes in the next parent child list
                if(found==1):
                    break

            #If the corresponding shape of the front view is not found in side view check in top view to get the thickness of the shape
            if(found == 0):
                #Search top view, here we are assuming 
                for top in top_parts:
                    for m,part_t in enumerate(top):
                        
                        #Checking whether the height of top view is same as width in front view and the top view shape should not be used before
                        if((abs(part_t[3]-part_f[4]) < roundOffApprox) and len(part_t)==5):
                            #Experimental :- Check if the front shape is child, and x translation is too far - neglect same height in top and width in front which are of different shape
                            if(abs(part_f[0].tx - part_t[0].tx) > 0.5):
                                continue
                            #Checking whether the front view is a parent or not
                            if(j == 0):
                                first = 1
                            #If the shape in top view is child it must be protruding from it's parent to be visible in front view, so 
                            # we change the operation of the shape of the top view to union operation 
                            if(m!=0):
                                part_t[0].operation = "union"
                            #If it's a cylinder provide height and y-translation
                            if(part_f[0].shape == "cylinder"):
                                #This checking is not required as it is obvious, but still doing anyway
                                if(part_t[0].shape == "cube"):
                                    part_f[0].h = part_t[0].h
                                    part_f[0].ty = part_t[0].ty
                                    #If the cube is rotated in z axis
                                    part_f[0].rz = part_t[0].rz
                                    #For adding the rest of the child later give the top shape with height, z-translation and the position of the
                                    # "front_parts" we are comparing now
                                    part_t[0].b = part_f[3]
                                    part_t[0].tz = part_f[0].tz
                                    #Get to know the position of which parent we are adding in "front_part" so that the remaining shapes
                                    # in the top view after this shape can be added later into the "front_part" list 
                                    part_t[1] = i
                                    #Marking that the shape in the top view is used
                                    part_t[2] = -1
                                    part_t.append("used")
                                    break

                            if(part_f[0].shape == "cube"):

                                part_t[0].tz = part_f[0].tz
                                if(part_t[0].shape == "cube"):
                                    part_t[0].b = part_f[0].h
                                    #Check whether the cube is rotated along z axis( in top view)
                                    if(part_t[0].rz != 0):
                                        part_f[0] = part_t[0]
                                    else:
                                        #Getting thickness for the front view, which is the length of the top view
                                        part_f[0].b = part_t[0].l
                                        part_f[0].ty = part_t[0].ty

                                elif(part_t[0].shape == " cylinder"):
                                    #If cube is rotated along y axis
                                    part_t[0].ry = part_f[0].ry
                                    part_t[0].h = part_f[0].h
                                    part_f[0] = part_t[0]
                                
                                part_t[1] = j
                                #Marking that the shape in the top view is used
                                part_t[2] = -1
                                part_t.append("used")
                                break
                    else:
                        #Continue until you find the matching of front and top view
                        continue
                    break

    #Add the shape that is only visible in side view and top view(parent part and its child)
    for side in side_parts: 
        #If the parent is not used, get the thickness from top view, we are not checking front view because all the shapes visible in front view 
        # are already considered         
        if(side[0][3]!=-1):
            addCompleteList = []
            for part_s in side:
                #Looping through top view
                if(part_s[3] == -1):
                    break

                for k,top in enumerate(top_parts):
                    for l,part_t in enumerate(top):
                        #Check whether their width are same in both side and top view and top view should not be used already
                        if((abs(part_s[4]-part_t[4]) < roundOffApprox) and len(part_t)==5) :

                            if(part_s[0].shape=="cube"):
                                #Giving z-translation
                                part_t[0].tz = part_s[0].tz
                                if(part_t[0].shape == "cube"):
                                    #Giving thickness to top view shape
                                    part_t[0].b = part_s[0].h
                                    #Check whether the cube is rotated along z axis( in top view)
                                    if(part_t[0].rz != 0):
                                        part_s[0] = part_t[0]
                                    else:
                                        #Getting thickness for the front view
                                        part_s[0].b = part_t[0].h
                                        #Give x-translation
                                        part_s[0].tx = part_t[0].tx

                                elif(part_t[0].shape == " cylinder"):
                                    #Rotated along x axis, but as we have rotated the side view along z axis to 90, we use ry of side view
                                    part_t[0].rx = part_s[0].ry
                                    part_t[0].h = part_s[0].h
                                    part_s[0] = part_t[0]
                                
                                #Getting the location of the parent-child side view we are going to add to "front_parts"
                                part_t[1] = len(front_parts)
                                #Marking that the shape in the top view is used
                                part_t[2] = -1
                                part_t.append("used")
                            #If its a cylinder get its height
                            if(part_s[0].shape=="cylinder"):
                                #This checking is not required as it is obvious, but still doing anyway
                                if(part_t[0].shape == "cube"):
                                    #Get height
                                    part_s[0].h = part_t[0].h
                                    #Give x-translation
                                    part_s[0].tx = part_t[0].tx
                                    #Rotation in z axis
                                    part_s[0].rz = part_t[0].rz
                                    #For adding the rest of the child later give the top shape with height, z-translation and the position of the
                                    # "front_parts" we are comparing now
                                    part_t[0].b = part_s[3]
                                    part_t[0].tz = part_s[0].tz
                                    #Get to know the position of which parent we are adding in "front_part" so that the remaining shapes
                                    # in the top view after this shape can be added later into the "front_part" list 
                                    part_t[1] = len(front_parts)
                                    #Marking that the shape in the top view is used
                                    part_t[2] = -1
                                    part_t.append("used")
                addCompleteList.append(part_s)
            #Append whole parent-child list into "front_parts"
            front_parts.append(addCompleteList)

    #Add shapes only visible in top
    for top in top_parts:
        #Need to give the top view heights
        height = -1
        #For z-translation
        tz = -1
        #Position of the parent-child list where we need to add, which is stores in part list earlier
        position = -1
        #Loop through parent-child list to first find the position of the shape which is used while comparing with front view
        for part_t in top:
            #Check whether the height of the used shape is given and also check whether the shape in top view is already used
            if(height != -1 and len(part_t)==5):
                #If its a cylinder provide height and z-translation
                if(part_t[0].shape == "cylinder"):
                    part_t[0].h = height
                    part_t[0].tz = tz
                # If its a cube provide breadth(as the cube is rotated along x axis in top view) and z-translation
                elif (part_t[0].shape == "cube"):
                    part_t[0].b = height
                    part_t[0].tz = tz
                #Appending the shape in front_parts in the position obtained from previous top shape
                try:
                    front_parts[position].append(part_t)
                except:
                    print("Error occurred")
            #Check if the given top view is used
            try:
                class Spam(int): pass
                if(isinstance(Spam(part_t[2]),int)):
                    #Store its z-translation
                    tz = part_t[0].tz
                    #Get the position in front_parts list to add the rest of the child shape
                    position = part_t[1]
                    #Getting the height of the top shape already used, for cube its given by breadth, for cylinder, it is it's height 
                    if(part_t[0].shape == "cylinder"):
                        height = part_t[0].h
                    elif (part_t[0].shape == "cube"):
                        height = part_t[0].b
            except TypeError:
                pass

    return front_parts


def detect(c):
    # initialize the shape name and approximate the contour
    shape = "unidentified"
    peri = cv2.arcLength(c, True)
    #Finding the number of line segment required to make the polygon
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    #Cylinder type in openscad for making regular prism
    cylinder_type = 0

    # if the shape is a triangle, it will have 3 vertices
    if len(approx) == 3:
        shape = "triangle"
        cylinder_type = 3
    # if the shape has 4 vertices, it is either a square or a rectangle
    elif len(approx) == 4:
        # compute the bounding box of the contour and use the
        # bounding box to compute the aspect ratio
        (x, y, w, h) = cv2.boundingRect(approx)
        ar = w / float(h)
        rect = cv2.minAreaRect(c)
        ar = rect[1][0] / float(rect[1][1])
        # a square will have an aspect ratio that is approximately
        # equal to one, otherwise, the shape is a rectangle
        shape = "square" if ar >= 0.999 and ar <= 1.001 else "rectangle"

    # if the shape is a pentagon, it will have 5 vertices
    elif len(approx) == 5:
        shape = "pentagon"
        cylinder_type = 5
    # if the shape is a hexagon, it will have 6 vertices
    elif len(approx) == 6:
        shape = "hexagon"
        cylinder_type = 6
    # otherwise, we assume the shape is a circle
    else:
        shape = "circle"
        cylinder_type = 1

    # return the name of the shape
    return shape,cylinder_type

def valid_contours(img,type,ratio):
    #List to build parent and child shapes
    objects = []
    #Converting into greyscale
    imgrey = cv2.cvtColor(img.copy(),cv2.COLOR_BGR2GRAY)
    #COnverting into greyscale image to black and white image
    ret, thresh = cv2.threshold(imgrey,127,255,cv2.THRESH_BINARY_INV)
    #Finding contours
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    #Rearranging such that the contours are arranged in descending order
    hierarchy,contours = zip(*sorted(zip(hierarchy[0],contours),key = lambda x: cv2.contourArea(x[1]),reverse=True))

    #Looping through all contours
    for i,c in enumerate(contours):
         #Choosing inner side of the two same shape created by thickness of the line  
        if ( hierarchy[i][3] != -1 or (hierarchy[i][3] == -1 and hierarchy[i][2] == -1) ):
            M = cv2.moments(c)
            if(M["m00"] !=0):
                #Getting the center of the contour
                cX = int(M["m10"] / M["m00"]) 
                cY = int(M["m01"] / M["m00"])
                #Getting Contour area
                area = cv2.contourArea(c)
                #Rescaling based on input from user
                area = area * ratio
                #getting minimum area rectangle that is enclosing the contour
                rect = cv2.minAreaRect(c)
                #Ignoring small areas
                if(area <= 4*ratio):
                    break
                # calculate coordinates of the minimum area rectangle
                box = cv2.boxPoints(rect)
                #Rescaling based on input from user
                rectLength = round_up(rect[1][0] * ratio)
                rectBreadth = round_up(rect[1][1] * ratio)

                #it's a horizontal rectangle which encloses the contour
                x,y,w,h = cv2.boundingRect(c)
                w = round_up(w * ratio)
                h = round_up(h * ratio)
                #Making largest contour's center has reference for translation of other shape
                if(len(objects)==0):
                    pos = [cX,cY]
                
                # draw the contour number on the image
                # cv2.putText(img, "#{}".format(i), (box[0][0], box[0][1]), cv2.FONT_HERSHEY_SIMPLEX,
                #     1.0, (255, 0, 0), 1)
                # draw contours
                cv2.drawContours(img, [c], 0, (0,0, 255), 1)
                #Detecting the shape of the contour
                shape, cylinder_type = detect(c)
                    
                # To store the shape and its details
                part = []

                if(shape == "square"):
                    #Adding shape
                    part.append(node(shape="cube",l=rectLength,b=rectLength,h=rectLength))
                    #Giving rotatation
                    if(type == "front"):
                        part[0].rotate(0,rect[2],0)
                    elif(type == "side"):
                        part[0].rotate(0,rect[2],90)
                    elif(rect[2]==0):
                        part[0].rotate(90,0,90)
                    else:
                        part[0].rotate(90,0,rect[2])
                        
                    #Adding center of the contour
                    part.append(tuple([cX,cY]))
                    #Adding contour
                    part.append(c)
                    #Adding height of the horizontal rectangle enclosing the contour
                    part.append(h)
                    #Adding width of the horizontal rectangle enclosing the contour
                    part.append(w)
                    #Adding to the list of shape in parent child manner
                    add_part(objects,part,pos,type,ratio)
                elif(shape == "rectangle"):
                    if(type == "front"):
                        if(rect[2]==-90):
                            part.append(node(shape="cube",l=rectBreadth,b=rectBreadth,h=rectLength))
                            part[0].rotate(0,0,0)
                        else:
                            part.append(node(shape="cube",l=rectLength,b=rectLength,h=rectBreadth))
                            part[0].rotate(0,rect[2],0)
                    elif(type == "side"):
                        if(rect[2]==-90):
                            part.append(node(shape="cube",l=rectBreadth,b=rectBreadth,h=rectLength))
                            part[0].rotate(0,0,90)
                        else:
                            part.append(node(shape="cube",l=rectLength,b=rectLength,h=rectBreadth))
                            part[0].rotate(0,rect[2],90)
                    #If there is no rotation in top view rotate 90 along in both x and z axis 
                    elif(rect[2]==-90):
                        part.append(node(shape="cube",l=rectBreadth,b=rectBreadth,h=rectLength))
                        part[0].rotate(90,0,90)
                    elif(rect[2]==0):
                        part.append(node(shape="cube",l=rectLength,b=rectLength,h=rectBreadth))
                        part[0].rotate(90,0,90)
                    else:
                        #If there is some rotation, rotate in z axis
                        part.append(node(shape="cube",l=rectLength,b=rectLength,h=rectBreadth))
                        part[0].rotate(90,0,rect[2])

                    part.append(tuple([cX,cY]))
                    part.append(c)
                    part.append(h)
                    part.append(w)
                    add_part(objects,part,pos,type,ratio)
                #Cylinder type in openscad
                elif(cylinder_type > 0):
                    #Cylinder
                    if(shape == "circle"):
                        _,radius = cv2.minEnclosingCircle(c)
                        radius = round_up(radius * ratio)
                        part.append(node(shape="cylinder",r = radius,r1 = radius,h=rectLength))
                        if(type == "front"):
                            part[0].rotate(90,0,0)
                        elif(type == "side"):
                            part[0].rotate(0,90,0)
                        part.append(tuple([cX,cY]))
                        part.append(c)
                        part.append(h)
                        part.append(w)
                        add_part(objects,part,pos,type,ratio)
                    else:
                        #Regular prism
                        _,radius = cv2.minEnclosingCircle(c)
                        radius = round_up(radius * ratio)
                        part.append(node(shape="cylinder",r = radius,r1 = radius,h=rectLength,fn = cylinder_type))
                        if(type == "front"):
                            part[0].rotate(90,-90 - rect[2],0)
                        elif(type == "side"):
                            part[0].rotate(0,90,0)
                        else:
                            part[0].rotate(0,0,rect[2])
                        part.append(tuple([cX,cY]))
                        part.append(c)
                        part.append(h)
                        part.append(w)
                        add_part(objects,part,pos,type,ratio)          
                else:
                    print("shape not detected")
    # cv2.imwrite("result1"+type+".png",img)
    return objects