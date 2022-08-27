/* Doc String

Description: main file random drive algorithm

 - Project is currenlty linked to YOLO object detection algorithm (YOLOv4 architecture running V2 headers)
 - Project is linked through DarkHelp C++ API

 TODO
- Make the path for neural network config files etc relative (currently absolute)
- improve wall following algorithm (saw tooth design as opposed to linear path)
- clean out commented code that is depreciated



__author__ = "Brandon Colelough"
__copyright__ = "Open Source"
__credits__ = ["https://robotics.ee.uwa.edu.au/eyesim/", "https://github.com/stephanecharette/DarkHelp", https://github.com/AlexeyAB/darknet]
__license__ = "Open Source"
__version__ = "1.0.1"
__maintainer__ = "Brandon Colelough"
__email__ = "brandon.colelough1234@gmail.com"
__status__ = "Production"

Date Last Edited: 04 pr 2022

*/


#include "../include/Random_Drive.h"
#include "../include/comms.h"
pthread_mutex_t agent;

// define the local map this edge agent is going to develop
local_map local_map;


/*
 * Ensure control agent is initialised BEFORE any edge agent to ensure they are placed as master (1) on network
 * TODO - write a script to make this happen regardless of initialisation
 */

int main(int argc, char *argv[]){
    // generate two threads, one for the agent random drive and one for comms - also generate the argument structures for each
    pthread_t t1, t2;
    R_thargs_t thrgs_R;
    C_thargs_t thrgs_C;

    // set up arguments for random search thread
    thrgs_R.SAFE = 400; // 40cm
    thrgs_R.speed = 300;
    thrgs_R.scaling = 1500;
    thrgs_R.argc = argc;
    thrgs_R.argv.push_back(argv[1]);
    thrgs_R.argv.push_back(argv[2]);
    thrgs_R.argv.push_back(argv[3]);
    thrgs_R._local_map = &local_map;
    // set up arguments for comm thread
    thrgs_C._local_map = &local_map;

    XInitThreads();
    pthread_mutex_init(&agent, NULL);
    pthread_create(&t1, NULL, reinterpret_cast<void *(*)(void *)>(Random_Drive), &thrgs_R);
    OSWait(1000); // wait before starting comms to allow edge agents time to initialise
    //pthread_create(&t2, NULL, comms, &thrgs_C);
    KEYWait(KEY4);
    pthread_exit(0); // will terminate program

    return 0;

}
