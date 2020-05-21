#from  https://stackoverflow.com/questions/48154642/how-to-count-number-of-dots-in-an-image-using-python-and-opencv
import cv2
import numpy as np
gray = cv2.imread("replicatedavide/fig1baseline.png",0)

rows,cols = gray.shape
cv2.imshow('original',gray)

for i in range(rows):
    for j in range(cols):
        k = gray[i,j]
        if(k != 255):
            gray[i,j] = 0
            #print(k)

cv2.imshow('Manual gray',gray)
## threshold
th, threshed = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)

#threshed = gray


cv2.imshow('threshold',threshed)



## findcontours
cnts = cv2.findContours(threshed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
print(cnts)

## filter by area
s1= 3
s2 = 50
xcnts = []
for cnt in cnts:
    #print(cv2.contourArea(cnt))
    #if s1<cv2.contourArea(cnt) <s2:
        xcnts.append(cnt)

print("Dots number: {}".format(len(xcnts)))

gray = cv2.drawContours(gray, cnts, -1, (0,255,0), 3)
cv2.imshow('contours',gray)

k = cv2.waitKey(0) & 0xFF
if k == 27:         # wait for ESC key to exit
    cv2.destroyAllWindows()