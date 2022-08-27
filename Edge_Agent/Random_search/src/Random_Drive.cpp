/* Doc String

Description: Random drive algorithm
both drive distance and turn angle is random.

 TODO
 - wall detection algorithm
 - wall follow algorithm
 - map encoders - improve error rate being sent (alot found at control egent)

__author__ = "Brandon Colelough"
__copyright__ = "Open Source"
__credits__ = ["https://robotics.ee.uwa.edu.au/eyesim/", "https://github.com/stephanecharette/DarkHelp", https://github.com/AlexeyAB/darknet]
__license__ = "NIL"
__version__ = "1.0.1"
__maintainer__ = "Brandon Colelough"
__email__ = "brandon.colelough1234@gmail.com"
__status__ = "Production"

Date Last Edited: 04 pr 2022


*/

#include <DarkHelp.hpp>
#include <cstdlib>
#include <cstring>
#include "../include/Random_Drive.h"
#include "eyebot++.h"
#include "../include/Wall_follow.h"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include <iostream>
#include <vector>
using namespace std;


// define the camera resolution properties (Pixels and field of view in x direction) - types given in eyesim types.h
constexpr auto RES      = QVGA;
constexpr auto RES_SIZE = QVGA_SIZE;
int RES_PARAMS_X  = QVGA_X;
int RES_PARAMS_Y =  QVGA_Y;
int FOV = 71; // Raspberry Pi Camera FOV

/*
 * Memory allocation and initialisation of structure
 * Structure primitive is stored in heaade file
 */
struct position* create_pos(struct position* s, int x, int y, int phi)
{
    s = new position;
    s->x = x;
    s->y = y;
    s->phi = phi;
    return s;
}


/*
 * Memory allocation and initialisation of structure
 * Structure primitive is stored in heaade file
 */
struct prediction_results* create_prediction_results(struct prediction_results* s, std::vector<DarkHelp::PredictionResult> results, position *pos, vector<int> distance)
{
    s = new prediction_results;
    std::copy(results.begin(), results.end(), std::back_inserter(s->results));
    s->agent_location =pos;
    s->distance = distance;
    return s;
}

struct feature_info* create_feature_info(struct feature_info* s, int distance, float pose){
    s = new feature_info;
    s->distance = distance;
    s->pose = pose;
    return s;
}

struct detected_feature* create_feature(struct detected_feature* s, int feature_class, float confidence, std::string name, position *feature_position){
    s = new detected_feature;
    s->name = name;
    s->object_class = feature_class;
    s->object_position = feature_position;
    s->confidence = confidence;
    return s;
}


/* used in testing!
cv::Mat GetImageFromMemory(uchar* image, int rows, int length, int flag)
{
    cv::Mat1b data(rows, length, image);
    return  imdecode(data, flag);
}
*/


/*
 * getPosition returns the current position of the edge agent
 * referenced from a starting position of {0,0}
 * It also updates the local map current position and position list (if boolean set to true)
 *
 */

position* getPosition(bool update, local_map *local_map){
    int x,y,phi;
    VWGetPosition(&x, &y, &phi); // the sim positioning system is 90 deg off the plan that it should be - x and y given in altered order here to compensate
    position* position = create_pos(position, x,y,phi);
    if(update){
       local_map->cur_position = *position;
    }
    return position;
}

/*
 * scaled target position returns the x co-ordinate of an identified target
 *
 * This fucntion uses the camera resolution (int he x-direction) as well as the camera field of view to determine
 * where a target is relative to a 360 degree LIDAR scan
 *
 * The function takes in the min and max of the pixel data (0 to camera res x) pix_min, pix_max
 * and the min and max of the field of view  ( 0 - field of view) - fov_min, fov_max
 * lastly, the function takes in the x position of the identified target
 *
 * The funciton scales the range [pix_min, pix_max] to [fov_min, fov_max]
 * The function then returns the scaled x position of the target in the edge agent camera field of view
 *
 * see:
 * https://stackoverflow.com/questions/5294955/how-to-scale-down-a-range-of-numbers-with-a-known-min-and-max-value
 * for algorithm
 *
 * TODO - rename variables as this is used quite a bit
 */

float scaled_target_pos(int pix_min, int pix_max, int fov_min, int fov_max, int targ_loc_x){

    return ( ( (fov_max - fov_min) * (targ_loc_x - pix_min) ) / (pix_max - pix_min) ) + fov_min;

}

/*
 * Get distances funciton returns the distances to identified targets
 * Function has been updated to also return the angle to the target
 *
 * input is the results vector from YOLO
 * output is a vector of distances to each target int he YOLO results output
 *
 * The dimensions for the camera are given at the start of the script below all of the include statement
 *  The resolution dimensions are taken from the types given in EyeSim types.h
 *  The field of view (FOV) is given manually
 *  The lidar scan is only given in the x direction i.e. we can ignore the y direction and height
 *
 *  // LIDAR scan positioning depends on the agent phi position
 *
 *
 *   MPORTANT - Preliminary testing shows that this module may be slightly faulty!
 *   TODO - extensive tests on get distances module
 *        - Look at the possibility of creating a module to reject information that doesn't align with the rest of the picture from the scene!
 *
 */

feature_info* get_distances_and_pose(DarkHelp::PredictionResult results, int scan[360]){
    try{
        feature_info* feature_info;
        float scaled_target_loc, centred_target_pos, adjusted_target_loc, direction;
        int t_pos_x,  t_w, distance; // target positions, height and width from darknet results
        t_pos_x = results.rect.x;
        t_w = results.rect.width;

        // where in the camera field of view is the target - current FOV is 70 deg
        scaled_target_loc = scaled_target_pos( 0, RES_PARAMS_X,0, FOV, (t_pos_x + (t_w/2) ) ); // for target location - use centre of target in x
        /*
        Lidar scan is from 0 - 359
        NOTE THAT Lidar scan numbering depends on the initial phi of the robot!
         Everything is easier if the robot phi always starts at 0
         This will break if it isnt

         The scan must centre around the agents phi and go into 360 to work

        */
        int phi = getPosition(false, NULL)->phi;
        centred_target_pos =  scaled_target_pos(0,FOV,(phi - (FOV/2)),(phi + (FOV/2)),scaled_target_loc);
        adjusted_target_loc = phi - centred_target_pos;
        if(adjusted_target_loc < 0 ){
            adjusted_target_loc = 359 + adjusted_target_loc;
        }else if(adjusted_target_loc > 359){
            adjusted_target_loc = 359 - adjusted_target_loc;
        }



       // adjust direction so that it centres around 0
       // unsure why - but the simulated lidar scan only picks up an object at one degree
       // to resolve this for sim only) - loop through the closest 10 around where the object should be in the scan to find it

       /*
        * USED IN SIM ONLY - Comment out for physical deployment
        * remember to loop around for adjusted target loc > 360
        */

       if(int(adjusted_target_loc) + 5 > 359){
           distance = scan[(int(adjusted_target_loc)-5)];
           for(int idx = (int(adjusted_target_loc)-5); idx<= 359; idx++){
               if(scan[(int(idx)-5)] < distance){
                   distance = scan[(int(idx))];
               }
           }
           for(int idx = 0; idx< (359 - (5+ int(adjusted_target_loc))); idx++){
               if(scan[(int(idx)-5)] < distance){
                   distance = scan[(int(idx))];
               }
           }


       }else if (int(adjusted_target_loc) - 5 < 0) {
           distance = scan[0];
           for(int idx = (359 - (5- int(adjusted_target_loc))); idx<= 359; idx++){
               if(scan[(int(idx)-5)] < distance){
                   distance = scan[(int(idx))];
               }
           }

           for(int idx = 0; idx<= int(adjusted_target_loc)+5; idx++){
               if(scan[(int(idx))] < distance){
                   distance = scan[(int(idx))];
               }
           }


       }else{
           distance = scan[(int(adjusted_target_loc)-5)];
           for(int idx = (int(adjusted_target_loc)-5); idx< (int(adjusted_target_loc)+5); idx++){
               if(scan[(int(idx))] < distance){
                   distance = scan[(int(idx))];
               }
           }
       }

       //direction = scaled_target_pos(0, FOV, -1* ((FOV/2)), ((FOV/2)), scaled_target_loc);
       feature_info = create_feature_info(feature_info, distance, adjusted_target_loc);
       //std::cout << "target: " + results.name + ";  Distance: " +   std::to_string(scan[int(adjusted_target_loc)]) + "mm;  Direction: " +   std::to_string(direction)  + "; Lidar Scan Loc " + std::to_string(adjusted_target_loc) << std::endl;
        return feature_info;
    }catch (const std::exception& e) // reference to the base of a polymorphic object
    {
        std::cout << e.what(); // information from length_error printed
        const std::string logfile      =  getexepath() + "ERROR_LOG.txt";
        ofstream myfile;
        myfile.open (logfile, std::ios_base::app);
        // ------------------------------------------------ used for logging messages

        myfile.open (logfile, std::ios_base::app);
        myfile << "Partner:";
        myfile << "message: ";
        myfile << e.what();
        myfile << "\n";
        myfile.close();
    }
}

/*
 * NOT CURRENTLY WORKING! - Issues with distance (from lidar scan!)
 * TODO - fix so it can be used
 *
 * Determines the target position and bundles feature up in a neat lil feature descriptor
 * there are 2 pose elements used to determine the target location on the global coordinate system used
 * the first is the pose of the robot as given in the agent location (agent_position)
 * This first variable gives which way the centre of the agent is looking towards
 *
 * The second is the angle at which the detected feature is placed
 * the second variable is where the robot sees the feature to be extracted
 * This will either be in the robots first or second quadrant of vision ( squeezed between -90 and 90 in the above funciton)
 */
detected_feature extract_feature_information(DarkHelp::PredictionResult result, int scan[360], position *agent_position){

    try{
        std::vector<detected_feature> extracted_features;
        feature_info* feature_info;
        float agent_phi, phi, gamma, d;
        int feature_x, feature_y;

        // note that agent pose is between -180 to 180, so the first thing we do is squeeze that boi between 0 to 360 deg
        //Agent phi is given from 0 to 180 going from Q4 to Q3 and 0 to -180 going from Q1 to Q2
        //We want agent_phi to be given from 0 to 360 so now we must adjust for that
        if(agent_position->phi>0){
            // we are in either Q3 or Q4, squeeze agent position to be between 180 t0 360 from 180 to 0
            // TODO - rename this function as it is used more than was first intended
            agent_phi = scaled_target_pos(180, 0, 180, 360,agent_position->phi );
        }else if(agent_position->phi<0){
            // we are in either Q1 or Q2, squeeze agent position to be between 0 to 180 from its original 0 to -180
            agent_phi = scaled_target_pos(0, -180, 0, 180,agent_position->phi );
        }else if(agent_position->phi== 0){
            agent_phi = 0;
        }else{
            LCDSetPrintf(18,0, "Error converting agent phi to a local coordinate system ");
        }

            feature_info = get_distances_and_pose(result, scan);
            // since the agents pose is used as an absolute in the global coordinate system and the
            // angle to target is given relatively with the centreline set to 0, these two angles can be
            // added to determine the overall angle to target on the global coordinate system


            if(feature_info->pose + agent_phi  < 0){
                phi = 360 + (feature_info->pose + agent_phi);
            }else if(feature_info->pose + agent_phi  > 360 ){
                phi = 360 - (feature_info->pose + agent_phi );
            }else if(0 <= (feature_info->pose + agent_phi) && (feature_info->pose + agent_phi) <= 360){
                phi = feature_info->pose + agent_phi;
            }

            /*
            if(0 <= (feature_info->pose + agent_phi) <= 360){
                phi = feature_info->pose + agent_phi;
            }else if(feature_info->pose + agent_phi  < 0){
                phi = 360 + (feature_info->pose + agent_phi);
            }else if(feature_info->pose + agent_phi  > 360 ){
                phi = 360 - (feature_info->pose + agent_phi );
            }
             */

            // switch statements don't support greater than or less than - sad
            //using some simple geometry yo find the angle needed to get measurements from a right angled triangle on the x-y plane
            if(phi <= 90){
                gamma = (90 - phi);
            }else if (90<phi && phi<=180){
                gamma = phi-90;
            }else if(180<phi && phi <=270){
                float alpha = phi - 180;
                gamma = 90 - alpha;
            }else if(phi > 270){
                gamma = phi - 270;
            }

            d = feature_info->distance;
            float angleToRad = gamma * (3.14 / 180);
            feature_x = (int) ((sin(angleToRad) * d) + agent_position->x );
            feature_y = (int) ((cos(angleToRad) * d) + agent_position->y);
            // adjust x & y for which quadrant they were in
            if(phi <= 90){
                // first quadrant - do nothing
            }else if (90<phi && phi<=180){
                feature_x = -1 * feature_x;
            }else if(180<phi && phi <=270){
                feature_x = -1 * feature_x;
                feature_y = -1 * feature_y;
            }else if(phi > 270){
                feature_y = -1 * feature_y;
            }

            position* feature_position = create_pos(feature_position, feature_x, feature_y, 0); // TODO add feature pose ?
            detected_feature* new_feature = create_feature(new_feature, result.best_class, result.best_probability, result.name, feature_position);
            return *new_feature;

    }catch (const std::exception& e) // reference to the base of a polymorphic object
    {
        std::cout << e.what(); // information from length_error printed
        const std::string logfile      =  getexepath() + "ERROR_LOG.txt";
        ofstream myfile;
        myfile.open (logfile, std::ios_base::app);
        // ------------------------------------------------ used for logging messages

        myfile.open (logfile, std::ios_base::app);
        myfile << "Partner:";
        myfile << "message: ";
        myfile << e.what();
        myfile << "\n";
        myfile.close();
    }

}

/*
 * Used to add a feature to the localmap - called from main after a robot comes close enough to a feature
 */
detected_feature get_feature(BYTE img[QVGA_SIZE], DarkHelp::NN *nn, local_map *local_map,int scan[360], int SAFE, int scaling, int scan_loc){
    int dis_to_feat = scan[scan_loc];;
    CAMGet(img);    // edge agent camera demo
    LCDImage(img);  // only

    // convert the unsigned char byte image data to a CV mat data type that is suitable for DarkNet
    cv::Mat TempImg(RES_PARAMS_Y, RES_PARAMS_X, CV_8UC3, img,cv::Mat::AUTO_STEP);

    // conduct a prediction at each timestep before moving!
    // conduct a prediction after each camget() call
    // feed image from edge agent through YOLO algorithm - analyze the image and return a vector of structures with all sorts of informationt
    const auto result = nn->predict(TempImg);


    if( result.size()> 0) {
        // current work around (not the most accurate) - determine which feature you are in front of using the distance provided
        // and use the agents position to make a new feature position
        // Reminder
        // Q1 is 090 - 180 --> 180 - 35+  = 145
        // Q2 is 180 - 270 --> 180 + 35 = 215
        // squeeze from 145 - 215 into 0 - fov
        float angle_to_feat = scaled_target_pos(145, 215, 0, FOV,scan_loc );
        //std::vector<float> feat_angles;
        float closest_angle = FOV; // this will be the maximum
        int result_pos = 0;
        //find the angle for each of the things we are looking at
        for(int idx = 0; idx < result.size(); idx++) {
            feature_info* feature_info;
            float scaled_target_loc, adjusted_target_loc, direction;
            int t_pos_x,  t_w, distance; // target positions, height and width from darknet results
            t_pos_x = result.at(idx).rect.x;
            t_w = result.at(idx).rect.width;
            // where in the camera field of view is the target - current FOV is 70 deg
            scaled_target_loc = scaled_target_pos( 0, RES_PARAMS_X,0, FOV, (t_pos_x + (t_w/2) ) ); // for target location - use centre of target in x
            if(std::abs((scaled_target_loc - angle_to_feat)) < closest_angle){
                closest_angle = scaled_target_loc;
                result_pos = idx;
            }

        }


        // now that all that is out of the way, add the feature to the detected feature list
        position *feature_position = getPosition(false, NULL);
        //need a whole bunch of annoying maths to figure out the x and y position of hte feature from the agent due to
        //the pose of the agent and the position on the camera frame its odne up above in a different module that isnt used anymore)
        // for now, just add a a standoff of 75% the distance to the feature depending
        // note that the pose of the  agent in has an effect on this too
        // TODO - fix this by adding in the maths
        int new_x, new_y;
        // for y - if the agent is looking up ( pose between 45 and 135- add
        if(45 <= feature_position->phi && feature_position->phi <=135 ){
            new_y = feature_position->y + (0.75*dis_to_feat);
        }else if(225 <= feature_position->phi && feature_position->phi <=315 ) {
            new_y = feature_position->y - (0.75*dis_to_feat);
        }else{
            new_y = feature_position->y;
        }
        // for x - if the agent is looking right ( pose between 0 and 180 - add
        if(feature_position->phi <= 45  || feature_position->phi >=315){
            new_x = feature_position->x + (0.75*dis_to_feat);
        }else if (feature_position->phi <= 225  && feature_position->phi >=135){
            new_x = feature_position->x - (0.75*dis_to_feat);
        }else{
            new_x = feature_position->x;
        }
        position *updated_feature_position = create_pos(updated_feature_position, new_x, new_y, feature_position->phi);
        detected_feature* new_feature = create_feature(new_feature, result.at(result_pos).best_class, result.at(result_pos).best_probability, result.at(result_pos).name, updated_feature_position);
        return *new_feature;


        /* Doesn't work - TODO Fix
        std::vector<feature_info> feature_info_list{};
        for(int idx = 0; idx < result.size(); idx++) {
            new_feature_info = get_distances_and_pose(result.at(idx), scan);
            feature_info_list.push_back(*new_feature_info);
        }

        for(int idx = 0; idx < feature_info_list.size(); idx++){
            if(feature_info_list.at(idx).distance < (SAFE+50)){
                // TODO - improve this (or fix essentially)
                position *position = getPosition(false, NULL);
                //std::vector<detected_feature> feature_locations = extract_feature_information(result.at(idx), scan, position);
                detected_feature* new_feature = create_feature(new_feature, result.best_class, result.best_probability, result.name, feature_position);
                local_map->detected_feature_list.push_back(feature_locations.at(0));
            }
        }
          */
    }
}

/*
* Handle camera funciton used to show edge agent camera output and cnduct and store preductions into local_map
*/
feature_info* handle_camera(BYTE img[QVGA_SIZE], DarkHelp::NN *nn, local_map *local_map,int scan[360], int SAFE, int scaling){
    try
    {
        CAMGet(img);    // edge agent camera demo
        LCDImage(img);  // only

        // convert the unsigned char byte image data to a CV mat data type that is suitable for DarkNet
        cv::Mat TempImg(RES_PARAMS_Y, RES_PARAMS_X, CV_8UC3, img,cv::Mat::AUTO_STEP);

        // conduct a prediction at each timestep before moving!
        // conduct a prediction after each camget() call
        // feed image from edge agent through YOLO algorithm - analyze the image and return a vector of structures with all sorts of informationt
        const auto result = nn->predict(TempImg);


        cv::Mat output = nn->annotate();
        // display results of predictions
        std::cout << result << std::endl;
        imshow("prediction output", output);
        cv::waitKey(1);



        // find the closest feature and issue orders to go to it
        feature_info* new_feature_info;
        if( result.size()> 0) {
            // legacy impleentation - TODO merge the two for loops below into one
            std::vector<feature_info> feature_info_list{};
            for(int idx = 0; idx < result.size(); idx++) {
                new_feature_info = get_distances_and_pose(result.at(idx), scan);
                feature_info_list.push_back(*new_feature_info);
            }
            int smallest_dist = 0;
            bool obj_found = false;

            for(int idx = 0; idx < feature_info_list.size(); idx++){
                if(feature_info_list.at(idx).distance<feature_info_list.at(smallest_dist).distance){
                   smallest_dist = idx;
                }
            }

            new_feature_info = create_feature_info(new_feature_info, feature_info_list.at(smallest_dist).distance,feature_info_list.at(smallest_dist).pose);
            return new_feature_info;
        }

        // need a random feature info vector to return if no feature is found so
        // stops the program from crashing
        int dis =scaling * (float)rand()/RAND_MAX;      // generate a random distance for the robot to go
        int dir = 180 * ((float)rand()/RAND_MAX-0.5);
        new_feature_info = create_feature_info(new_feature_info, dis,dir);
        return new_feature_info;

    }catch (const std::exception& e) // reference to the base of a polymorphic object
    {
        std::cout << e.what(); // information from length_error printed
        const std::string logfile      =  getexepath() + "ERROR_LOG.txt";
        ofstream myfile;
        myfile.open (logfile, std::ios_base::app);
        // ------------------------------------------------ used for logging messages

        myfile.open (logfile, std::ios_base::app);
        myfile << "Partner:";
        myfile << "message: ";
        myfile << e.what();
        myfile << "\n";
        myfile.close();
    }


        /*
        // used in testing!
        // get DarkHelp to annotate with the most recent results
        cv::Mat output = nn->annotate();
        // display results of predictions
        std::cout << result << std::endl;
        imshow("prediction output", output);
        cv::waitKey(1);
        */

        // used in testing!
        //imshow("1",TempImg);
        //cv::waitKey(0);

        /* Depreciated code - TODO Prune
        //cv::Mat dst;
        //dst.create(608,608,CV_8UC3);
        //resize(TempImg, dst, dst.size(), 0, 0, cv::INTER_NEAREST);
        */

}

void scan_area(BYTE img[QVGA_SIZE], DarkHelp::NN *nn, vector<detected_feature> *detected_feature_list, int scan[360], int scan_loc){
    CAMGet(img);    // edge agent camera demo
    LCDImage(img);  // only
    // convert the unsigned char byte image data to a CV mat data type that is suitable for DarkNet
    cv::Mat TempImg(RES_PARAMS_Y, RES_PARAMS_X, CV_8UC3, img,cv::Mat::AUTO_STEP);

    // conduct a prediction at each timestep before moving!
    // conduct a prediction after each camget() call
    // feed image from edge agent through YOLO algorithm - analyze the image and return a vector of structures with all sorts of informationt
    const auto result = nn->predict(TempImg);

    cv::Mat output = nn->annotate();
    // display results of predictions
    std::cout << result << std::endl;
    imshow("prediction output", output);
    cv::waitKey(1);

    // get the approx position for of all the features at this landmark
    try {
        for (int idx = 0; idx < result.size(); idx++) {
            position *agent_position = getPosition(false, NULL);
            detected_feature feature_location = extract_feature_information(result.at(idx), scan, agent_position);
            detected_feature_list->push_back(feature_location);
        }
    }catch (const std::exception& e) // reference to the base of a polymorphic object
    {
        std::cout << e.what(); // information from length_error printed
        const std::string logfile      =  getexepath() + "ERROR_LOG.txt";
        ofstream myfile;
        myfile.open (logfile, std::ios_base::app);
        // ------------------------------------------------ used for logging messages

        myfile.open (logfile, std::ios_base::app);
        myfile << "Partner:";
        myfile << "message: ";
        myfile << e.what();
        myfile << "\n";
        myfile.close();
    }

}


void * Random_Drive(void *arguments){

    // ------------------------------- parameter initialisation

    //unpack parameters from arguments
    int SAFE= ((R_thargs_t*)arguments)->SAFE;
    int speed = ((R_thargs_t*)arguments)->speed;
    int scaling = ((R_thargs_t*)arguments)->scaling;
    int argc = ((R_thargs_t*)arguments)->argc;
    std::vector<std::string> argv = ((R_thargs_t*)arguments)->argv;
    // define the local map this edge agent is going to develop
    // moved from global variable to here - may be issues !
    local_map* local_map = ((R_thargs_t*)arguments)->_local_map;

    // set up an instance of LocalMap structure and all of its variables
    int x,y,phi;
    VWGetPosition(&x, &y, &phi);
    position* position = getPosition(false, NULL);
    // initialise prediciton results structure!

    //set up an instance of yolo for edge agent
    const std::string project_dir   =  getexepath();
    std::string const HOME = std::getenv("HOME") ? std::getenv("HOME") : ".";
    const std::string names_file    =  project_dir + argv[0];
    const std::string config_file   =  project_dir + argv[1];
    const std::string weights_file  =  project_dir +  argv[2];

    DarkHelp::Config cfg(config_file, weights_file, names_file );
    cfg.enable_tiles					= false;
    cfg.combine_tile_predictions		= true;
    cfg.annotation_auto_hide_labels		= false;
    cfg.annotation_include_duration		= true;
    cfg.annotation_include_timestamp	= false;
    DarkHelp::NN nn(cfg);

    // Camera type (resolution) MUST be defined in thee script - Cannot be given through CLI (tried to do this - It was too much effort!)

    BYTE img[RES_SIZE]; // QVGA is 320 x 240 x 3
    int l, f, r,dir, dis, scan[360];
    LCDMenu("", "", "", "END");
    CAMInit(RES);

    // ------------------------------- parameter initialisation


    // main Loop for movement and detection
    while(KEYRead() != KEY4)
    {
        try
        {
            pthread_mutex_lock(&agent);
            // Robot movement and edge sensor packaging
            dis =scaling * (float)rand()/RAND_MAX;      // generate a random distance for the robot to go
            dir = 180 * ((float)rand()/RAND_MAX-0.5);
            LCDSetPrintf(19,0, "Random direction %3d,  and distance: %3d to travel", dir,dis);
            while(dis > SAFE){

                // LIDAR scan has a weird numbering system
                //Q1 (front left) is 090 - 180
                //Q2 (front right) is 180 - 270
                // Q3 (rear right) is 270 - 360
                // Q4 (rear left) is 0 - 90
                LIDARGet(scan);

                // call handle camera to show edge agent camera output and conduct and store predictions into local map

                feature_info* feature_info  = handle_camera(img, &nn, local_map, scan, SAFE, scaling);

                dis = feature_info->distance;
                dir = feature_info->pose; // multiply by neg 1 as camera is -tve in q4, + q1 and the turn function is the opposite
                // direction needs to be fixed to match the rob ios funcitons
                if(dir>180) {
                    // we are in either Q3 or Q4, squeeze agent position to be between 180 t0 360 from 180 to 0
                    // TODO - rename this function as it is used more than was first intended
                    dir = scaled_target_pos(180, 359, -180, 0, dir);
                }



                // turn towards the found feature
                // error will make anything less than 5 deg negligable
                if(std::abs(dir) > 5){
                    VWTurn(dir, 90); VWWait(); // turn [-90..+90]
                }


                LCDSetPrintf(18,0, "PSD Left%3d Front%3d Right%3d Rear%3d", scan[90], scan[180], scan[270], scan[360]);

                // tolerance for collision avoidance with LIDAR will be 25 degrees from the front of the edge agent
                // Q1 is 090 - 180 --> 180 - 35+  = 145
                // Q2 is 180 - 270 --> 180 + 35 = 215
                // hence, range to check scan is between 155 and 205
                // TODO - improve efficiency of this!

                bool collision_flag = false;
                int idx = 145;
                while(!collision_flag && idx <=215){
                    if (scan[idx]<SAFE)
                    {
                        collision_flag = true;
                    }
                    idx +=1;
                }
                if (!collision_flag) {
                    VWStraight(SAFE / 2, speed);//start driving
                    getPosition(true, local_map); // also updates position and position list!
                }
                else
                {
                    // get this features location
                    detected_feature landmark = get_feature(img, &nn, local_map, scan, SAFE, scaling, idx);

                    // upon finding a feature, the edge agent will conduct a resection to figure out where it is
                    // once teh edge agent has conducted the resection it will send that through to the control
                    // agent as a feature map within its local map.
                    // the edge agent will htne wait for confirmation as to where exactly it is
                    // and will update its local map accordingly and continue onto another feature that it has spotted within
                    // the feature map that was just generated
                    // first, back up a lil
                    VWStraight(-200, 400); VWWait(); // back up
                    // then turn so that your pose is 0
                    phi = getPosition(true, local_map)->phi;
                    int turn;
                    if(phi > 180){
                        turn = 360 - phi;
                    }else{
                        turn = -1*phi;
                    };
                    VWTurn((turn), 90); VWWait(); // turn [-90..+90]
                    // take a lidar scan of the current area
                    LIDARGet(scan);
                    //make x turns to capture a full 360 of this current area through camera
                    int num_turns = ceil(360/FOV);
                    int deg_turn = ceil(360/num_turns);
                    vector<detected_feature> detected_feature_list;
                    for(int idx = 0; idx < num_turns; idx++){
                        scan_area(img, &nn, &detected_feature_list, scan, idx);
                        VWTurn(deg_turn, 90); VWWait(); // turn [-90..+90]
                    }


                    VWStraight(-200, 400); VWWait(); // back up
                    dir = 360 * ((float)rand()/RAND_MAX-0.5);
                    LCDSetPrintf(19,0, "Turn %d", dir);
                    VWTurn(dir + 45, 90); VWWait(); // turn [-90..+90]
                    // drive a bit to get away from that feature
                    VWStraight(SAFE / 2, speed);//start driving
                    LCDSetPrintf(19,0, "          ");
                    getPosition(true, local_map);// also updates position and position list!
                    // follow along the wall you just found
                    //wall_follow(SAFE);
                }
                dis -=SAFE / 2;
                OSWait(100);
            }// while loop
            pthread_mutex_unlock(&agent);

        }catch (const std::exception& e) // reference to the base of a polymorphic object
        {
            std::cout << e.what(); // information from length_error printed
            const std::string logfile      =  getexepath() + "ERROR_LOG.txt";
            ofstream myfile;
            myfile.open (logfile, std::ios_base::app);
            // ------------------------------------------------ used for logging messages

            myfile.open (logfile, std::ios_base::app);
            myfile << "Partner:";
            myfile << "message: ";
            myfile << e.what();
            myfile << "\n";
            myfile.close();
        }

    } // while
}
