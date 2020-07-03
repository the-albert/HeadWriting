# Import the OpenCV, dlib and pyautogui libraries
import cv2
import dlib
#import keyboard
import time
import pyautogui
import win32gui
import win32con

# Initialize a face cascade using the frontal face haar cascade provided with the OpenCV library
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# The deisred output width and height
OUTPUT_SIZE_WIDTH = 775
OUTPUT_SIZE_HEIGHT = 600

toplist = []
winlist = []
def enum_callback(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

def detectAndTrackLargestFace():

    #checks if 'c' was pressed display on/off range rectangle
    pressed_c = -1
    #tracker that will tell us on wich move we are to display the proper part of keyboard
    move = 0
    #tracker to count frames that passed without a move, to go back to whole keyboard after some time of not moving
    frame = 0
    #tracker to check if head came back to neutral position before picking another part of keyboard
    neutral = 0
    # Open the first webcame device
    capture = cv2.VideoCapture(0)

    # Create two opencv named window
    cv2.namedWindow("result-image", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("keys", cv2.WINDOW_AUTOSIZE)

    # Position the windows next to eachother
    cv2.moveWindow("keys", 0, 100)
    cv2.moveWindow("result-image", 400, 100)

    # Start the window thread for the two windows we are using
    cv2.startWindowThread()

    # Create the tracker we will use
    tracker = dlib.correlation_tracker()

    # The variable we use to keep track of the fact whether we are currently using the dlib tracker
    trackingFace = 0

    # The color of the rectangle we draw around the face
    rectangleColor = (0, 165, 255)

#######################################################################################################################
    ###STARTING THE LOOP TO DETECT AND TRACK THE LARGEST FACE###
    try:
        while True:
            #we are incrementing a frame tracker with every loop
            frame = frame + 1
            # Retrieve the latest image from the webcam
            rc, fullSizeBaseImage = capture.read()

            # Resize the image to 320x240
            baseImage = cv2.resize(fullSizeBaseImage, (320, 240))

            #copy te image that we are capturing to draw a rectangle on it and display it
            resultImage = baseImage.copy()

            # If we are not tracking a face, then try to detect one
            if not trackingFace:

                #convert the base image into gray scale image
                gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
                # Now use the haar cascade detector to find all faces in the image
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)

                print("Using the cascade detector to detect face")

                #set the variables that will be used to track only the largest face
                maxArea = 0
                x = 0
                y = 0
                w = 0
                h = 0

                #we simply count the biggest detected face to know wchich one we should track
                for (_x, _y, _w, _h) in faces:
                    if _w * _h > maxArea:
                        x = int(_x)
                        y = int(_y)
                        w = int(_w)
                        h = int(_h)
                        maxArea = w * h

                # If one or more faces are found, initialize the tracker on the largest face in the picture
                if maxArea > 0:
                    # Initialize the tracker
                    tracker.start_track(baseImage,
                                        dlib.rectangle(x - 10,
                                                       y - 20,
                                                       x + w + 10,
                                                       y + h ))

                    # Set the indicator variable such that we know the tracker is tracking a region in the image
                    trackingFace = 1

            # Check if the tracker is actively tracking a region in the image
            if trackingFace:


                # Update the tracker and request information about the quality of the tracking update
                trackingQuality = tracker.update(baseImage)

                # If the tracking quality is good enough, determine the
                # updated position of the tracked region and draw the
                # rectangle
                if trackingQuality >= 8.75:
                    tracked_position = tracker.get_position()

                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())
                    cv2.rectangle(resultImage, (t_x, t_y),
                                  (t_x + t_w, t_y + t_h),
                                  rectangleColor, 2)

                else:
                    trackingFace = 0



            #displaying range of head movement (by pressing 'c') that we need to cross to make action
            #we can also turn it off by pressing 'c' again to activate it later at different possition
            #we can adjust the size of rectangle by adding values to range variables

            if cv2.waitKey(2) & 0xFF == ord('c') and trackingFace==1:
                pressed_c = pressed_c * (-1)
                range_x = t_x - 15
                range_y = t_y - 10
                range_w = t_x+t_w +15
                range_h = t_y+t_h +10

            if pressed_c==1:
                #win32gui.EnumWindows(enum_callback, toplist)
                #keyboard = [(hwnd, title) for hwnd, title in winlist if 'keys' in title.lower()]
                # just grab the first window that matches
                #keyboard = keyboard[0]
                # use the window handle to minimize
                #win32gui.ShowWindow(keyboard[0], win32con.SW_MINIMIZE)
                #win32gui.SetForegroundWindow(keyboard[0])

                cv2.rectangle(resultImage, (range_x, range_y), (range_w, range_h), (0, 0, 255), 2)

            largeResult = cv2.resize(resultImage,
                                     (OUTPUT_SIZE_WIDTH, OUTPUT_SIZE_HEIGHT))
######################################################################################################################
            ###DETECTING TILTING OF HEAD###

            if trackingFace==1 and pressed_c==1:
                #we check if user came back to neutral position after making a move before another move
                if (t_y+t_h) < (range_h) and (t_y) > (range_y) and (t_x) > (range_x) and (t_x+t_w) < (range_w):
                    neutral = 1
                #################################################FIRST MOVE
                if move == 0:
                    #DOWN
                    if ( (t_y+t_h) > (range_h) ) and neutral == 1:
                        keys = cv2.imread("keys/1dol.png")
                        move = 1
                        frame = 0
                        neutral = 0
                    #UP
                    elif ((t_y) < (range_y)) and neutral == 1:
                        keys = cv2.imread("keys/1gora.png")
                        move = 2
                        frame = 0
                        neutral = 0
                    #LEFT
                    elif ((t_x) < (range_x)) and neutral == 1:
                        keys = cv2.imread("keys/1lewy.png")
                        move = 3
                        frame = 0
                        neutral = 0
                    #RIGHT
                    elif ((t_x+t_w) > (range_w)) and neutral == 1:
                        keys = cv2.imread("keys/1prawo.png")
                        move = 4
                        frame = 0
                        neutral = 0

                ###################################################SECOND MOVE
                if move > 0 and move < 5 and neutral == 1:
                    #FIRST WAS DOWN
                    if move == 1:
                        # DOWN
                        if (t_y + t_h) > (range_h):
                            keys = cv2.imread("keys/1dold.png")
                            move = 5
                            frame = 0
                            neutral = 0
                        # UP
                        elif (t_y) < (range_y):
                            keys = cv2.imread("keys/1dolg.png")
                            move = 6
                            frame = 0
                            neutral = 0
                        # LEFT
                        elif (t_x) < (range_x):
                            keys = cv2.imread("keys/1doll.png")
                            move = 7
                            frame = 0
                            neutral = 0
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            keys = cv2.imread("keys/1dolp.png")
                            move = 8
                            frame = 0
                            neutral = 0

                    #FIRST WAS UP
                    if move == 2:
                        # DOWN
                        if (t_y + t_h) > (range_h):
                            keys = cv2.imread("keys/1goradol.png")
                            move = 9
                            frame = 0
                            neutral = 0
                        # UP
                        elif (t_y) < (range_y):
                            keys = cv2.imread("keys/1gorag.png")
                            move = 10
                            frame = 0
                            neutral = 0
                        # LEFT
                        elif (t_x) < (range_x):
                            keys = cv2.imread("keys/1goral.png")
                            move = 11
                            frame = 0
                            neutral = 0
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            keys = cv2.imread("keys/1gorap.png")
                            move = 12
                            frame = 0
                            neutral = 0

                    #FIRST WAS LEFT
                    if move == 3:
                        # DOWN
                        if (t_y + t_h) > (range_h):
                            keys = cv2.imread("keys/1lewydol.png")
                            move = 13
                            frame = 0
                            neutral = 0
                        # UP
                        elif (t_y) < (range_y):
                            keys = cv2.imread("keys/1lewyg.png")
                            move = 14
                            frame = 0
                            neutral = 0
                        # LEFT
                        elif (t_x) < (range_x):
                            keys = cv2.imread("keys/1lewyl.png")
                            move = 15
                            frame = 0
                            neutral = 0
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            keys = cv2.imread("keys/1lewyp.png")
                            move = 16
                            frame = 0
                            neutral = 0

                    #FIRST WAS RIGHT
                    if move == 4:
                        # DOWN
                        if (t_y + t_h) > (range_h):
                            keys = cv2.imread("keys/1prawod.png")
                            move = 17
                            frame = 0
                            neutral = 0
                        # UP
                        elif (t_y) < (range_y):
                            keys = cv2.imread("keys/1prawog.png")
                            move = 18
                            frame = 0
                            neutral = 0
                        # LEFT
                        elif (t_x) < (range_x):
                            keys = cv2.imread("keys/1prawol.png")
                            move = 19
                            frame = 0
                            neutral = 0
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            keys = cv2.imread("keys/1prawop.png")
                            move = 20
                            frame = 0
                            neutral = 0

##########################################################THIRD MOVE

                if move > 4 and move < 9 and neutral == 1:
                    if move == 5:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('w')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('x')
                            neutral = 0
                            frame = 100

                if move > 4 and move < 9 and neutral == 1:
                    if move == 6:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('q')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('r')
                            neutral = 0
                            frame = 100
                if move > 4 and move < 9 and neutral == 1:
                    if move == 7:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('s')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('t')
                            neutral = 0
                            frame = 100
                if move > 4 and move < 9 and neutral == 1:
                    if move == 8:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('u')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('v')
                            neutral = 0
                            frame = 100


                if move > 8 and move < 13 and neutral == 1:
                    if move == 9:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('g')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('h')
                            neutral = 0
                            frame = 100

                if move > 8 and move < 13 and neutral == 1:
                    if move == 10:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('a')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('b')
                            neutral = 0
                            frame = 100
                if move > 8 and move < 13 and neutral == 1:
                    if move == 11:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('c')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('d')
                            neutral = 0
                            frame = 100
                if move > 8 and move < 13 and neutral == 1:
                    if move == 12:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('e')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('f')
                            neutral = 0
                            frame = 100



                if move > 12 and move < 17 and neutral == 1:
                    if move == 13:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press(',')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('enter') #tu powinna byc klawiatura numeryczna, ale narazie bedzie enter
                            neutral = 0
                            frame = 100

                if move > 12 and move < 17 and neutral == 1:
                    if move == 14:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('y')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('z')
                            neutral = 0
                            frame = 100

                if move > 12 and move < 17 and neutral == 1:
                    if move == 15:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('space')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):

                            pyautogui.press('backspace')
                            neutral = 0
                            frame = 100

                if move > 12 and move < 17 and neutral == 1:
                    if move == 16:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('.')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('?')
                            neutral = 0
                            frame = 100

                if move > 16 and move < 21 and neutral == 1:
                    if move == 17:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('o')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('p')
                            neutral = 0
                            frame = 100

                if move > 16 and move < 21 and neutral == 1:
                    if move == 18:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('i')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('j')
                            neutral = 0
                            frame = 100
                if move > 16 and move < 21 and neutral == 1:
                    if move == 19:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('k')
                            neutral = 0
                            frame = 100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('l')
                            neutral = 0
                            frame = 100

                if move > 16 and move < 21 and neutral == 1:
                    if move == 20:
                        # LEFT
                        if (t_x) < (range_x):
                            pyautogui.press('m')
                            neutral = 0
                            frame=100
                        # RIGHT
                        elif (t_x + t_w) > (range_w):
                            pyautogui.press('n')
                            neutral = 0
                            frame = 100


            ######################################################################################################################
            # Finally, we want to show the images on the screen
            #if we didn't make any move or starting picking a letter, whole keyboard is set
            if move==0:
                keys = cv2.imread("keys/1.png")
            #we displaying a keyboard next to the camera window
            keys = cv2.resize(keys, (350,350))
            cv2.imshow("keys", keys)
            #we display a camera with rectangles window
            cv2.imshow("result-image", largeResult)
            if cv2.waitKey(2) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                exit(0)
                break
            #we set move tracker to 0 after some frames of not moving passed to go back to first keyboard
            if frame>50:
                move = 0

    # To ensure we can also deal with the user pressing Ctrl-C in the console
    # we have to check for the KeyboardInterrupt exception and destroy
    # all opencv windows and exit the application
    except KeyboardInterrupt as e:
        cv2.destroyAllWindows()
        exit(0)


if __name__ == '__main__':
     detectAndTrackLargestFace()

     #filtr kalmana uśrednianie wartości w czasie
     #sprobowac inny traker z wbudowanym filtrem
     #ograniczac rozdzielczosc kamery jesli ilosc klatek bedzie mala