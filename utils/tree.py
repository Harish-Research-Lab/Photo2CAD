from .shape import node


def writetofile(filename, string):
    file = open(filename, "a")
    file.write(string)
    file.close()


def createtree(nodes, filename):
    if(len(nodes) == 0):
        print("No shapes detected")
        return

    subtree = []
    string = ''
    # Initialize empty node
    present = node()
    # Add the first node in left child
    present.left = nodes[0]
    # Generates function/string for the shape as in openscad
    nodes[0].name()
    # Add the generated string to the present node
    present.string = nodes[0].string
    # If there is only one node, write it to the file
    if(len(nodes) == 1):
        writetofile(filename, present.string)
    # If the number of nodes is more than one enter the loop
    for i, object in enumerate(nodes[1:]):
        # Generate function/statement for the shape as in openscad
        object.name()
        # If Node is child of shapes
        if(object.operation != 'None'):
            # If the right child in tree is free
            if(present.right == 'None'):
                # Assign the right parent
                present.right = object
                # Update the present string
                present.string = object.operation + \
                    "() {\n\t" + present.string + \
                    '\n\t' + object.string + '}\n'
                # Store it for appending into the file
                string = present.string
            else:
                # If right is not free, create a new node and make the present node as left child to the new node
                temp = present
                present = node()
                present.left = temp
                present.string = temp.string
                # Then make the object as right child of the new node
                present.right = object
                # Update the string
                present.string = object.operation + \
                    "() {\n\t" + present.left.string + \
                    '\n\t' + object.string + '}\n'
                # Store it for appending
                string = present.string
        else:
            # Satisfies this condition only when there is two consecutive parent shape with no child
            if(present.right == 'None'):
                # Append the present string to the file
                writetofile(filename, present.string)

            # So as parent-child list is completly traversed, it is added to subtree and the subtree string is appended to the file
            subtree.append(present)
            writetofile(filename, string)
            # Create a new subtree
            string = ''
            present = node()
            present.left = object
            present.string = object.string
            # If the last node is the parent shape node
            if(i == len(nodes)-2):
                writetofile(filename, present.string)
    # If the last node is a child shape node
    if(string != ''):
        writetofile(filename, string)
    # Add the last subtree
    subtree.append(present)
    print("Subtree:", len(subtree))
