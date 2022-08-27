/* Doc String

Description: used  save local and global maps

 TODO - lOAD FILE NOT CURENTLY WORKING -    unsure why -- FIX

__author__ = "Brandon Colelough"
__copyright__ = "Open Source"
__credits__ = ["https://robotics.ee.uwa.edu.au/eyesim/"]
__license__ = "Open Source"
__version__ = "1.0.1"
__maintainer__ = "Brandon Colelough"
__email__ = "brandon.colelough1234@gmail.com"
__status__ = "Production"

Date Last Edited: 07 pr 2022

*/


#include <vector>
#include "../include/save_maps.h"
#include <bits/stdc++.h>
#include <iostream>
#include <sys/stat.h>
#include <stdio.h>
#include <string>

[[noreturn]] void *save_local_maps(void *arguments){
    while(1){
        pthread_mutex_lock(&agent);
        std::vector<local_map>* map_list = ((save_thargs_t*)arguments)->_map_list;
        std::string map_name = ((save_thargs_t *) arguments)->map_name;
        const std::string file_dir     =  getexepath() + map_name;
        char dir[file_dir.length() + 1];
        strcpy(dir, file_dir.c_str());
        // Creating a directory
        if (mkdir(dir, 0777) == -1) {
            cerr << "Error :  " << strerror(errno) << endl;
        }else {
            cout << "Directory created";
        }
        // write each local map to disk
        cout << "Writing to disk" << endl;
        for(int idx = 0; idx < map_list->size(); idx++){
            //if(!map_list->at(idx).cur_position.empty()){
                cout << "Writing map " + std::to_string(idx) + " to disk" << endl;
                std::string file = file_dir  + "/map_" + std::to_string(idx)+ "_.dat";
                char new_file[file.length() + 1];
                strcpy(new_file, file.c_str());
                FILE *fout = fopen(new_file, "wb+");
                fwrite( &map_list->at(idx),  sizeof(local_map), 1, fout);
                fclose(fout);



           // }
        }
        LCDPrintf("Local Maps saved to file!");
        pthread_mutex_unlock(&agent);
        OSWait(10000);
    }


}

/*
 * reads local maps given number of local maps to read and the directory to read them from
 * making convention is map_xx - xx corresponds to agent number
 */
void *load_local_maps(void *arguments){
    pthread_mutex_lock(&agent);

    std::vector<local_map>* map_list = ((save_thargs_t*)arguments)->_map_list;
    std::string map_name = ((save_thargs_t *) arguments)->map_name;
    const std::string file_dir     =  getexepath() + map_name;
    char dir[file_dir.length() + 1];
    strcpy(dir, file_dir.c_str());
    // Creating a directory
    if (mkdir(dir, 0777) == -1) {
        cerr << "Error :  " << strerror(errno) << endl;
    }else {
        cout << "Directory created";
    }
    // write each local map to disk
    cout << "reading from disk" << endl;
    for(int idx = 0; idx < map_list->size(); idx++){
        std::string file = file_dir  + "/map_" + std::to_string(idx)+ "_.dat";
        //map_list->at(idx).cur_position.clear();
        map_list->at(idx).control_correction_list.clear();
        map_list->at(idx).landmark_maps.clear();
        // read the local map
        // file naming conventions are the exact same as above
        //std::string file = file_dir  + "/map_" + std::to_string(idx)+ "_.dat";
        char open_file[file.length() + 1];
        strcpy(open_file, file.c_str());
        // should make a GUI and allow user to pick a global map to read the local maps from> - TODO
        FILE* fin = fopen(open_file, "r");
        fread(&map_list->at(idx), sizeof(open_file), 1, fin);
        fclose(fin);

    }
    LCDPrintf("Local Maps loaded from file!");
    pthread_mutex_unlock(&agent);


}

