/* Doc String

Description: used as helper to read files from current working directory




__author__ = "Brandon Colelough"
__copyright__ = "Open Source"
__credits__ = [""]
__license__ = "Open Source"
__version__ = "1.0.1"
__maintainer__ = "Brandon Colelough"
__email__ = "brandon.colelough1234@gmail.com"
__status__ = "Production"

Date Last Edited: 05 pr 2022

*/


#include "../include/read_file.h"

/*
 * used to remove a word from a string - used in conjunction with getexepath function
 */
void RemoveWordFromLine(std::string &line, const std::string &word)
{
    auto n = line.find(word);
    if (n != std::string::npos)
    {
        line.erase(n, word.length());
    }
}
/*
 * getexepath used to get the current system operating path of the executable
 * to be used to determine the path of parameters put in through CLI
 */
std::string getexepath()
{
    char result[ PATH_MAX ];
    ssize_t count = readlink( "/proc/self/exe", result, PATH_MAX );
    std::string path_str = std::string( result, (count > 0) ? count : 0 );
    // remove tge exe name from path
    RemoveWordFromLine(path_str, "/Random_search.x");
    //also  remove build or cmake build from string if it exists
    RemoveWordFromLine(path_str, "cmake-build-debug");
    RemoveWordFromLine(path_str, "build");
    return path_str;
}


void read_agent_loc(std::string fileName, std::vector<std::vector<int>> *start_pos_list){
    std::ifstream in(fileName);
    std::string delim_0 = ",";
    std::vector<std::string> vecOfStrs;
    int token;
    // Check if object is valid
    if(!in)
    {
        std::cerr << "Cannot open the File : "<<fileName<<std::endl;
    }
    std::string str;
    // Read the next line from File until it reaches the end.
    while (std::getline(in, str))
    {
        // Line contains string of length > 0 then save it in vector
        if(str.size() > 0)
            vecOfStrs.push_back(str);
    }
    //Close The File
    in.close();
    // further break up the vector of robot locations into a vector of a vector of integers
    // each starting location is given as x, y phi
    //split by comma delim
    for(int idx = 0; idx < vecOfStrs.size(); idx ++){
        size_t pos = 0;
        while ((pos = vecOfStrs.at(idx).find(delim_0)) != std::string::npos) {
            token = std::stoi( vecOfStrs.at(idx).substr(0, pos));
            start_pos_list->at(idx).push_back(token);
            vecOfStrs.at(idx).erase(0, pos + delim_0.length());
        }
    }

}

void read_class_names(std::string fileName, std::map<int, std::string> *class_names_map){
    std::ifstream in(fileName);
    std::string delim_0 = ",";
    std::vector<std::string> vecOfStrs;
    std::string token;
    // Check if object is valid
    if(!in)
    {
        std::cerr << "Cannot open the File : "<<fileName<<std::endl;
    }
    std::string str;
    // Read the next line from File until it reaches the end.
    while (std::getline(in, str))
    {
        // Line contains string of length > 0 then save it in vector
        if(str.size() > 0)
            vecOfStrs.push_back(str);
    }
    //Close The File
    in.close();
    // further break up the vector of robot locations into a vector of a vector of integers
    // each starting location is given as x, y phi
    //split by comma delim
    for(int idx = 0; idx < vecOfStrs.size(); idx ++){
        token =  vecOfStrs.at(idx);
        class_names_map->insert(std::pair<int, std::string>(idx, token));
    }

}