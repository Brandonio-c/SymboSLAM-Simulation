/* Doc String

Description: wall following algorithm

 current wall following algorithm that uses PSD front, left and right doesn't work great. A more robust solution that follows the wall and stays parallel to it is needed
 as opposed to the current algorithm that just drives in a semi-straight line until it hits another intersection!

 The 2nd algorithm to do this (the lidar one) needs work as it currently is not working!

__author__ = "Brandon Colelough"
__copyright__ = "Open Source"
__credits__ = ["https://robotics.ee.uwa.edu.au/eyesim/"]
__license__ = "NIL"
__version__ = "1.0.1"
__maintainer__ = "Brandon Colelough"
__email__ = "brandon.colelough1234@gmail.com"
__status__ = "Production"

Date Last Edited: 21 Mar 2022


*/


#include "eyebot++.h"
#include "../include/Wall_follow.h"


void * wall_follow(int SAFE){
    int L, R, F, theta, leftFlag, rightFlag;
    /* not necessary when used with random drive fcn
    // find the first wall and turn!
    do {
         VWSetSpeed(200, 0); //
        //VWStraight(SAFE / 2, 100);//start driving
        OSWait(50);
    }while (PSDGet(PSD_FRONT) > SAFE); // find the first corner

     */
    VWSetSpeed(0, 0);
    leftFlag = 0;
    rightFlag = 0;

    while(leftFlag <=4 && rightFlag <=4) {
        L = PSDGet(PSD_LEFT);
        R = PSDGet(PSD_RIGHT);
        F = PSDGet(PSD_FRONT);

        if (L > R) {
            rightFlag = 0;
            leftFlag +=1; // we only want to turn either left or right a max of 4 times as any more will just be going around in a box

            // after we've figured out which way we are turning, determine the turn angle


            theta = atan2(R, F);
            if(theta < 45){theta = 80;}
            VWTurn(theta, 90);
            VWWait(); // turn [-90..+90]

            //

            do {

                if (PSDGet(PSD_RIGHT)<SAFE) VWSetSpeed(200, -20);

                else VWSetSpeed(200, +3); // turn right or left

                OSWait(50);
            }while (PSDGet(PSD_FRONT) > SAFE); // next corner
        } else {
            // and if means L == R, just turn right by default
            leftFlag = 0;
            rightFlag +=1; // we only want to turn either left or right a max of 4 times as any more will just be going around in a box
            theta = atan2(L, F);
            // throw away theta result if it less than 45 deg as you're probably at a corner
            if(theta < 45){theta = -90;}
            VWTurn(theta, 90);
            VWWait(); // turn [-90..+90]
            do {

                if (PSDGet(PSD_LEFT)<SAFE) VWSetSpeed(200, -3);

                else VWSetSpeed(200, +3); // turn right or left

                OSWait(50);
            }while (PSDGet(PSD_FRONT) > SAFE); // next corner

        }
    }
    VWSetSpeed(0, 0);
}

// NOT CURRENTLY WORKING - NEEDS TO BE FIXED!
void Lidar_Follow(int SAFE, int SPEED){
    int a, angle, s;
    int *scan;
    while (KEYRead() != KEY4)
         {
             LIDARGet(scan);
        if(scan[180] < SAFE) // check for front collision
            VWTurn(-90, 360); VWWait(); // turn right 90°
            //find the smallest scan value and the corresponding angle!
             //findMin(scan, 45, 135, &angle, &s); // check left
             printf("min angle %d val %d\n", angle, s);
        a = 180-angle;
        //VWCurve(50, k1*(a-90) + k2*(angle, s-250), SPEED);
        }
}

/*
void wall_follow_2(int SAFE, int SPEED){
    int L,R,F;
    VWGetPosition(&x1,&y1,&phi1);
    do
    { L=PSDGet(PSD_LEFT); F=PSDGet(PSD_FRONT);
        R=PSDGet(PSD_RIGHT);
        if (100<L && L<180 && 100<R && R<180) // check space
            VWSetSpeed(SPEED, L-R); // drive difference curve
        else if (100<L && L<180) // space check LEFT
            VWSetSpeed(SPEED, L-DIST);// drive left if left>DIST
        else if (100<R && R<180) // space check RIGHT
            VWSetSpeed(SPEED, DIST-R); // drive left if DIST>right
        else // no walls for orientation
            VWSetSpeed(SPEED, 0); // just drive straight
        VWGetPosition(&x2,&y2,&phi2);
        drivedist = sqrt(sqr(x2-x1)+sqr(y2-y1));
    } while (drivedist<MSIZE && F>MSIZE/2-50); // stop in time

}

/*
void drive(int SAFE){
    do {

        if (PSDGet(PSD_LEFT)<SAFE) VWSetSpeed(200, -3);

        else VWSetSpeed(200, +3); // turn right or left

        OSWait(50);
    }while (PSDGet(PSD_FRONT) > SAFE); // next corner

}

void turn(){
    VWSetSpeed(0, -100);
    while (PSDGet(PSD_FRONT) < 2*PSDGet(PSD_LEFT))
        OSWait(50);
 }
 */
