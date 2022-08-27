//
// Created by brandonio on 7/4/22.
//

#include "Local_Map.h"
#include "read_file.h"

#ifndef CONTROL_AGENT_SAVE_MAPS_H
#define CONTROL_AGENT_SAVE_MAPS_H

typedef struct save_thread_arguments{
    std::vector<local_map>* _map_list;
    std::string map_name;
} save_thargs_t;

class save_maps {

};

[[noreturn]] void *save_local_maps(void *arguments);

void *load_local_maps(void *arguments);


#endif //CONTROL_AGENT_SAVE_MAPS_H
