//
// Created by brandonio on 7/4/22.
//
#include <iostream>
#include <vector>
#include <unistd.h>
#include <fstream>
#include "opencv2/imgproc/imgproc.hpp"
#include <map>

#ifndef CONTROL_AGENT_READ_FILE_H
#define CONTROL_AGENT_READ_FILE_H
extern pthread_mutex_t agent;

class read_file {

};

void RemoveWordFromLine(std::string &line, const std::string &word);

std::string getexepath();

void read_agent_loc(std::string fileName, std::vector<std::vector<int>> *start_pos_list);

void read_class_names(std::string fileName, std::map<int, std::string> *class_names_map);


#endif //CONTROL_AGENT_READ_FILE_H
