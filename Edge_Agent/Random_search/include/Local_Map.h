//
// Created by brandonio on 5/4/22.
//
#include <vector>
#include <DarkHelp.hpp>
#include "eyebot++.h"
#define MAX 99
#define buffer 99
#define threadBuff 100
#ifndef RANDOM_SEARCH_LOCAL_MAP_H
#define RANDOM_SEARCH_LOCAL_MAP_H
using namespace std;


/*
 * pos (position) struct stores positional information (IMU) of edge agent
 */

struct position{
    int x;
    int y;
    int phi;
    // variable length array must be
    // last.
};

/*NOT needed anymore - TODO - Prune
 * prediction struct stores 3 items
 *  1. prediction values from DarkHelp API
 *  2. spatial information (pos data)
 *  3. depth information
 *      depth information is stored in a vector - each entry in the vector correlates to an entry in the results vector
 *      i.e. depth information for results at position [0] in the results vector is stored at [0] in the distance vector
 * unpacking of results - could be done by control agent to reduce computation time?
 * probably needs to be done by edge agent for reasoning and stuff
 * see darkelpPredictionResults.cpp for primitives
 */

struct prediction_results {
    vector<DarkHelp::PredictionResult> results;
    std::vector<position> feature_position;
    position* agent_location;
    vector<int> distance;
};

struct feature_info{
    int distance;
    float pose;
};

struct detected_feature{
    std::string name;
    int object_class;
    float confidence;
    position* object_position;
};



/*
 * The LocalMap  structure is used to store all information sensed from the edge agents indluding:
 *
 *      - Movement Data (IMU)
 *              - All movements from start position (referenced from {0,0} for all agents - Controller will offset given robot (edge agent) sim starting position)
 *              - current position on local map (referenced again from a start at {x,y} = {0,0})
 *              - NOTE - 3rd dimensional information NOT GIVEN ( May be updated later to include position in the Z direction) but robot relative pose (phi) is read and stored
 *
 *      - Predictions from DarkHelp - Darknet (YOLO)
 *      - Lidar information - Depth - distance to sensed target (identified object) - provided in predictions structrue
 *      TODO
 *      Add a structure in for detected walls
 *      - Will likely come after reasoning NN and edge filtering is done
 */

/*
struct local_map {
    vector<position> cur_position;
    vector<position> position_list;
    vector<detected_feature> detected_feature_list;
};
 */

struct landmark_map{
    position cur_position;
    detected_feature landmark ;
    vector<detected_feature> detected_feature_list;
    int scan[360];
};

struct local_map{
    position cur_position;
    vector<position> control_correction_list;
    vector<landmark_map> landmark_maps;
};


typedef struct R_thread_arguments {
    int SAFE;
    int speed;
    int scaling;
    int argc;
    std::vector<std::string> argv;
    local_map* _local_map;
}R_thargs_t;

typedef struct Comm_thread_arguments {
    local_map* _local_map;
} C_thargs_t;

typedef struct receive_mes_args{
    int control_agent_ID;
    const char *conf_message;
} Rec_thargs_t;




struct position* create_pos(struct position* s, int x, int y, int phi);

struct prediction_results* create_prediction_results(struct prediction_results* s, std::vector<DarkHelp::PredictionResult> results, position *pos, vector<int> distance);



#endif //RANDOM_SEARCH_LOCAL_MAP_H
