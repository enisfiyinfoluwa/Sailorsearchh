''''
Program to find a missing sailor at sea using bayes theorem
'''
import sys
import numpy as np
import cv2 as cv
import itertools
import random

MAP_FILE = 'cape_python.png'
# Assign search area corner points

SA1_CORNERS = (130,265,180,315) #(UL-X,UL-Y,LR-X,LR-Y)
SA2_CORNERS = (80,255,130,305)
SA3_CORNERS = (105,205,155,255)

class Search():
    def __init__(self,name):
        self.name = name
        self.img = cv.imread(MAP_FILE, cv.IMREAD_COLOR)
        if self.img is None:
            print("Image not found")
            sys.exit(1)

        # Set placeholders for sailor's actual loc
        self.area_actual =0
        self.sailor_actual = [0,0]  #As local coordinates within sarch area

        self.sa1 = self.img[SA1_CORNERS[1]:SA1_CORNERS[3],
                   SA1_CORNERS[0]:SA1_CORNERS[2]]

        # Mine: Add assertion to ensure compatibility of vectors
        assert self.sa1.shape == (50,50,3) , f"Expected shape of sa1 to be: (50,50,3)"


        # #Test 1
        # app = Search('Bonny basin')
        # print(app.sa1)
        # print(app.sa1.shape)
        self.sa2 = self.img[SA2_CORNERS[1]:SA2_CORNERS[3],
                   SA2_CORNERS[0]:SA2_CORNERS[2]]
        self.sa3 = self.img[SA3_CORNERS[1]:SA3_CORNERS[3],
                   SA3_CORNERS[0]:SA3_CORNERS[2]]


        #initialize search effectiveness
        self.sep1 = 0
        self.sep2 = 0
        self.sep3 = 0

    def drawmap(self,last_known):
        ''' Display base map with scale ,draw last known location and search areas'''
        cv.line(self.img,(20,370),(70,370),(0,0,0),2)
        cv.putText(self.img,'0',(8,370),cv.FONT_HERSHEY_PLAIN,1,(0,0,0))
        cv.putText(self.img,'50 Nuatical Miles',(71,370),cv.FONT_HERSHEY_PLAIN,1,(0,0,0))

        cv.putText(self.img,'* = Actual Position',(274,370),cv.FONT_HERSHEY_PLAIN,1,(255,0,0))
        cv.putText(self.img,'+ = Last Known Position',(274,355),cv.FONT_HERSHEY_PLAIN,1,(0,0,255))

        cv.rectangle(self.img, (SA1_CORNERS[0],SA1_CORNERS[1]),(SA1_CORNERS[2],SA1_CORNERS[3]),(0,0,0),1)
        cv.putText(self.img,'1',(SA1_CORNERS[0]+3,SA1_CORNERS[1]+15),cv.FONT_HERSHEY_PLAIN,1,(0,0,0))
        cv.putText(self.img,'+',(last_known),cv.FONT_HERSHEY_PLAIN,1,(0,0,255))

        cv.rectangle(self.img,(SA2_CORNERS[0],SA2_CORNERS[1]),(SA2_CORNERS[2],SA2_CORNERS[3]),(0,0,0),1)
        cv.putText(self.img,'2',(SA2_CORNERS[0]+3,SA2_CORNERS[1]+15),cv.FONT_HERSHEY_PLAIN,1,(0,0,0),1)


        cv.rectangle(self.img,(SA3_CORNERS[0],SA3_CORNERS[1]),(SA3_CORNERS[2],SA3_CORNERS[3]),(0,0,0),1)
        cv.putText(self.img,'3',(SA3_CORNERS[0]+3,SA3_CORNERS[1]+15),cv.FONT_HERSHEY_PLAIN,1,(0,0,0))

        cv.imshow("Search Area",self.img)
        cv.moveWindow("Search Area",750,10)
        cv.waitKey(7000)



    def sailor_final_location(self,num_search_areas):
        "returns the final location of the missing sailor"
        self.sailor_actual[0]= np.random.choice(self.sa1.shape[1],1)
        self.sailor_actual[1]= np.random.choice(self.sa1.shape[0],1)    # This is because in Numpy all Y's come before X's

        area = int(random.triangular(1,num_search_areas+1))
        # This is because initial probability is skewed towrds the center 2 at 0.5,
        # .triangular favors a skewed distribution that looks like a triangle

        #convert local coordinates to map coordinates
        if area ==1:
            x=self.sailor_actual[0] + SA1_CORNERS[0]
            y=self.sailor_actual[1] + SA1_CORNERS[1]
            self.area_actual = 1

        elif area ==2:
            x=self.sailor_actual[0]+ SA2_CORNERS[0]
            y=self.sailor_actual[1]+ SA2_CORNERS[1]
            self.area_actual= 2

        elif area ==3:
            x=self.sailor_actual[0]+ SA3_CORNERS[0]
            y=self.sailor_actual[1]+ SA3_CORNERS[1]
            self.area_actual= 3

        return x,y

    def cal_search_effectivenes(self):
        "set decimal search effectiveness value"

        self.sep1 = random.uniform(0.2,0.9)
        self.sep2 = random.uniform(0.2,0.9)
        self.sep3 = random.uniform(0.2,0.9)


    def conduct_search(self,area_num,area_array,effectiveness_prob):
        "Return search results and list of searched coordinates"

        local_y_range= range(area_array.shape[0])
        local_x_range= range(area_array.shape[1])

        coords =list (itertools.product(local_y_range,local_x_range))

        random.shuffle(coords)

        coords= coords[:int(len((coords)*effectiveness_prob))]
        loc_actual =(self.sailor_actual[0], self.sailor_actual[1])

        if area_num== self.area_actual and loc_actual in coords:
            return  "Found in area {}".format(area_num), coords
        return 'NOT FOUND' , coords

    def revise_target_probs(self):
        "Update area target probalities based on search effectiveness"

        # I initialized target probabilities here
        p1=0.2
        p2=0.5
        p3=0.3

        denom = self.p1 * (1-self.sep1) +self.p2*(1-self.sep2) + self.p3*(1-self.sep3)

        self.p1 = self.p1 * (1-self.sep1)/denom
        self.p2 = self.p2 * (1-self.sep2)/denom
        self.p3 = self.p3 * (1-self.sep3)/denom

        return p1,p2,p3







def main():
    app = Search('Cape Python')
    app.drawmap(last_known=(160, 290))

main()

























