
import math
from skimage import io, color
import numpy as np

def open_image(path):
    '''
    Return:
        3D array, row col [LAB]
    '''
    rgb = io.imread(path)
    lab_arr = color.rgb2lab(rgb)
    return lab_arr

def save_lab_image(path, lab_arr):
    '''Convert the aray to RBG, then save the image'''
    rgb_arr = color.lab2rgb(lab_arr)
    io.imsave(path, rgb_arr)

class Cluster(object):
    def __init__(self,x,y,l=0,a=0,b=0):
        self.update(x,y,l,a,b)

    def update(self,x,y,l,a,b):
        self.x = x
        self.y = y
        self.l = l
        self.a = a
        self.b = b

    def __str__(self):
        return "{},{}:{} {} {} ".format(self.x, self.y, self.l, self.a, self.b)


if __name__ == '__main__':
    image_arr = open_image('lenna.png')
    image_height = image_arr.shape[0]
    image_width = image_arr.shape[1]

    K = 2000
    N = image_width * image_height
    label = np.zeros((image_width, image_height))
    dis = np.full((image_width, image_height), np.inf)

    C = []
    print 'N:', N

    # Initialization
    S = int(math.sqrt(N/K)) # S the distance
    print 'S: ',S
    i = S/2
    j = S/2
    while i<image_height:
        while j<image_width:
            C.append(Cluster(i,j,image_arr[i][j][0],image_arr[i][j][1],image_arr[i][j][2]))
            j+=S
        j=S/2
        i+=S
    print 'len(C):', len(C)

    def get_gradient(x,y):
        if x+1>=image_width:
            x = image_width - 2
        if y+1>=image_height:
            y = image_height - 2

        gradient = image_arr[x+1][y+1][0] - image_arr[x][y][0] + \
                   image_arr[x+1][y+1][1] - image_arr[x][y][1] + \
                   image_arr[x+1][y+1][2] - image_arr[x][y][2]
        return gradient

    # re-choose a point in 3x3
    for point in C:
        point_gradient = get_gradient(point.x, point.y)
        for i in range(-1,2):
            for j in range(-1,2):
                x = point.x + i
                y = point.y + j
                new_gradient = get_gradient(x,y)
                if new_gradient < point_gradient:
                    point_gradient = new_gradient
                    point.update(x,y,image_arr[x][y][0],image_arr[x][y][1],image_arr[x][y][2])

    # Assignment
    print 'Assignment...'
    for point in C:
        print point
        for i in range(point.x-2*S, point.x+2*S):
            if i<0 or i>=image_width:
                continue
            for j in range(point.y-2*S, point.y+2*S):
                if j<0 or j>=image_height:
                    continue
                L,A,B = image_arr[i][j]
                m = 30
                Dc = math.sqrt(
                        math.pow(L-point.l,2)+
                        math.pow(A-point.a,2)+
                        math.pow(B-point.b,2))
                Ds = math.sqrt(
                        math.pow(i-point.x,2)+
                        math.pow(j-point.y,2))
                D = math.pow(Dc/m,2) + math.pow(Ds/S,2)
                D = math.sqrt(D)
                if D < dis[i][j]:
                    label[i][j] = C.index(point)
                    dis[i][j] = D

    print 'Update...'
    for point in C:
        print point
        point_index = C.index(point)
        pixels = []
        sum_x = sum_y =  number = 0
        for i in range(image_width):
            for j in range(image_height):
                if int(label[i][j]) == point_index:
                    sum_x += i
                    sum_y += j 
                    number += 1
        avg_x = sum_x/number
        avg_y = sum_y/number
        point.update(avg_x, avg_y, image_arr[avg_x][avg_y][0],image_arr[avg_x][avg_y][1],image_arr[avg_x][avg_y][2])


    for i in range(0,image_width):
        for j in range(0,image_height):
            point = C[int(label[i][j])]
            image_arr[i][j][0] = point.l
            image_arr[i][j][1] = point.a
            image_arr[i][j][2] = point.b

    for point in C:
        image_arr[point.x][point.y][0] = 0
        image_arr[point.x][point.y][1] = 0
        image_arr[point.x][point.y][2] = 0

    save_lab_image('arr.png', image_arr)
