''''
Program to find a missing sailor at sea using bayes theorem
'''
import sys
import numpy as np
import cv2 as cv
import itertools
import random
import time

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

        self.p1 = 0.2
        self.p2 = 0.5
        self.p3 = 0.3

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
        cv.waitKey(4000)
        cv.destroyAllWindows()



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

        coords = coords[:int((len(coords)*effectiveness_prob))]

        #coords = coords[:int((len(coords) * effectiveness_prob))] #Working

        loc_actual =(self.sailor_actual[0], self.sailor_actual[1])

        if area_num== self.area_actual and loc_actual in coords:
            return  "Found in area {}".format(area_num), coords
        return 'NOT FOUND' , coords

    def revise_target_probs(self):
        "Update area target probalities based on search effectiveness"

        # I initialized target probabilities here

        denom = self.p1* (1-self.sep1) + self.p2*(1-self.sep2) + self.p3*(1-self.sep3)

        self.p1 = self.p1 * (1-self.sep1)/denom
        self.p2 = self.p2 * (1-self.sep2)/denom
        self.p3 = self.p3 * (1-self.sep3)/denom



def draw_menu(search_num):
    '''Print menu of choices for conducting area searches'''
    print('\nSearch {}'.format(search_num))
    print('''
    
    Choose next areas to search:
    0 - Quit
    1 - Search Area 1 twice
    2 - Search Area 2 twice
    3 - Search Area 3 twice 
    4 - Search Area 1 & 2
    5 - Search Area 1 & 3
    6 - Search Area 2 & 3
    7 - Start Over 
    ''')

def main():
    app = Search('Cape Python')
    app.drawmap(last_known=(160, 290))
    sailor_x,sailor_y = app.sailor_final_location(num_search_areas=3)
    print(sailor_y[0])
    print('_'*65)
    print("P1: {} P2: {} P3: {} ".format(app.p1,app.p2,app.p3))

    search_num = 1

    while True:     #Main application loop
        draw_menu(search_num)
        app.cal_search_effectivenes()

        print("Choice")
        choice= input('>')


        if choice== '0':
            sys.exit()

        elif choice== '1':    #Searching Twice
            result_1, coords1= app.conduct_search(area_num=1,area_array=app.sa1,effectiveness_prob=app.sep1)
            result_2, coords2= app.conduct_search(area_num=1,area_array=app.sa1,effectiveness_prob=app.sep1)

            app.sep1 = (len(set(coords1+coords2)))/(len(app.sa1)**2)
            app.sep2 = 0
            app.sep3 = 0

        elif choice== '2':    #Searching Twice
            result_1, coords1= app.conduct_search(area_num=2,area_array=app.sa2,effectiveness_prob=app.sep2)
            result_2, coords2= app.conduct_search(area_num=2,area_array=app.sa2,effectiveness_prob=app.sep2)

            app.sep2 = (len(set(coords1+coords2)))/(len(app.sa2)**2)
            app.sep1 = 0
            app.sep3 = 0

        elif choice== '3':    #Searching Twice
            result_1, coords1= app.conduct_search(area_num=3,area_array=app.sa3,effectiveness_prob=app.sep3)
            result_2, coords2= app.conduct_search(area_num=3,area_array=app.sa3,effectiveness_prob=app.sep3)

            app.sep3 = (len(set(coords1+coords2)))/(len(app.sa3)**2)
            app.sep1 = 0
            app.sep2 = 0

        elif choice== '4':    #Searching Twice
            result_1, coords1= app.conduct_search(area_num=1,area_array=app.sa1,effectiveness_prob=app.sep1)
            result_2, coords2= app.conduct_search(area_num=2,area_array=app.sa2,effectiveness_prob=app.sep2)


            app.sep3 = 0

        elif choice== '5':    #Searching Twice
            result_1, coords1= app.conduct_search(area_num=1,area_array=app.sa1,effectiveness_prob=app.sep1)
            result_2, coords2= app.conduct_search(area_num=3,area_array=app.sa3,effectiveness_prob=app.sep3)

            app.sep2 = 0

        elif choice == '6':  # Searching Twice
            result_1, coords1 = app.conduct_search(area_num=2, area_array=app.sa2, effectiveness_prob=app.sep2)
            result_2, coords2 = app.conduct_search(area_num=3, area_array=app.sa3, effectiveness_prob=app.sep3)

            app.sep2 = 0

        elif choice == '7':
            main()

        else:
            print("That is not a valid choice. You choose {}\nPlease enter a valid  number between 0-7".format(choice),file=sys.stderr)
            continue  # continue runs the code from the top of the while loop


        app.revise_target_probs()
        print("Searching ...")
        time.sleep(3)
        print("\nSearch {} Results \n\n     Result 1: {} \n     Result 2: {} \n".format(search_num,result_1,result_2))

        print("Effectiveness for Search {}\nE1= {:.3f}\nE2= {:.3f}\nE3= {:.3f}".format(search_num,app.sep1,app.sep2,app.sep3))

        if result_1== result_2:
            print("\nNew Target Probabilities for Search {} \nP1= {:.3f}\nP2= {:.3f}\nP3= {:.3f}".format(search_num+1,app.p1,app.p2,app.p3))
        else:

           # cv.circle(app.img,(sailor_x,sailor_y),3,(255,0,0),-1)

            cv.circle(app.img,(sailor_x[0], sailor_y[0]),5, (255, 0, 0), -1)

            cv.imshow('Search Area', app.img)
            cv.waitKey(4000)
            cv.destroyAllWindows()
            time.sleep(2)


            main()
        search_num+= 1

if __name__== '__main__:':
    main()





main()

























