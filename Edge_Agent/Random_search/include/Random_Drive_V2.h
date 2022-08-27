//
// Created by brandonio on 13/05/22.
//

#ifndef RANDOM_SEARCH_RANDOM_DRIVE_V2_H
#define RANDOM_SEARCH_RANDOM_DRIVE_V2_H
#include "Local_Map.h"

extern pthread_mutex_t agent;

using namespace std;

class Random_Drive_V2 {

};

std::string getexepath();

void RemoveWordFromLine(std::string &line, const std::string &word);

position* getPosition(bool update, local_map *local_map);

float scaled_target_pos(int pix_min, int pix_max, int fov_min, int fov_max, int targ_loc_x);

detected_feature extract_feature_information(DarkHelp::PredictionResult result, int scan[360], position *agent_position);

void add_feature(BYTE img[QVGA_SIZE], DarkHelp::NN *nn, local_map *local_map,int scan[360], int SAFE, int scaling, int scan_loc);

feature_info* get_distances_and_pose(DarkHelp::PredictionResult results, int scan[360]);

void * Random_Drive_V2(void *arguments);

feature_info* handle_camera(BYTE img[QVGA_SIZE], DarkHelp::NN *nn, local_map *local_map,int scan[360], int SAFE, int scaling);



#endif //RANDOM_SEARCH_RANDOM_DRIVE_V2_H
