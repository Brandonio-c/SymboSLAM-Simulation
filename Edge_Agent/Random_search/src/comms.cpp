/* Doc String

Description: main file communications between edge and control agents

 TODO
- implement confirmation message upon control agent receipt

    currently having issues with waiting on the control agent to send through message -
    - program freezes as the receipt message is never received by this agent
    - have tried implementing multi-threading to receive and add a time delay to retry if confirmation message not sent by control agent

__author__ = "Brandon Colelough"
__copyright__ = "Open Source"
__credits__ = ["https://robotics.ee.uwa.edu.au/eyesim/"]
__license__ = "Open Source"
__version__ = "1.0.1"
__maintainer__ = "Brandon Colelough"
__email__ = "brandon.colelough1234@gmail.com"
__status__ = "Production"

Date Last Edited: 04 pr 2022

*/

#include "../include/comms.h"
#include "../include/read_file.h"
#include <iostream>
#include <thread>
bool message_received = false;

std::string map_encoder(local_map* local_map, int pos_list_num,int pred_list_num){
    /* note the following operators are used:
     * , - separator comma deliminated)
     * /0 - deliminator for 3 structure types
     * /1 - deliminator for positions in position list (also used in prediction position list)
     * /2 - deliminator for prediciton results list
     */

    /*
    // put current position into a string format
    std:string position = std::to_string(local_map->cur_position[0].x) + "," + std::to_string(local_map->cur_position[0].y ) + "," + std::to_string(local_map->cur_position[0].phi ) + ",/0";

    // put position_list into a string format
    // note that we are only sending things that we haven't sent before!
    // i.e. send from pos_list_num to position list size
    std::string position_list;
    for(int idx = pos_list_num; idx < local_map->position_list.size(); idx++){
        position_list = position_list + std::to_string(local_map->position_list[idx].x)  + "," + std::to_string(local_map->position_list[idx].y)  + "," + std::to_string(local_map->position_list[idx].phi)  + ",/1";
    }
    position_list = position_list + "/0";

    // put prediction results list into string format
    std::string prediction_list;
    for(int idx = pred_list_num; idx < local_map->detected_feature_list.size(); idx++){
        // add position - deliminator is , between data and \2 for the end of position
        prediction_list = prediction_list + std::to_string(local_map->detected_feature_list[idx].object_position->x)  + "," + std::to_string(local_map->detected_feature_list[idx].object_position->y)  + "," + std::to_string(local_map->detected_feature_list[idx].object_position->phi) + ",/2";
        // add information from the results - need a for loop as each prediction result item may have multiple targets identified
        // only take relevent information from prediction results - rect information, best class, best probability, name
        std::string prediction_list_results;

        // next, add the object name, delim is /2
        prediction_list = prediction_list + local_map->detected_feature_list[idx].name + "/2";

        prediction_list = prediction_list + std::to_string((int)((local_map->detected_feature_list[idx].confidence)*100)) + "/2";

        prediction_list = prediction_list + std::to_string(local_map->detected_feature_list[idx].object_class) + "/2/1";

    }
    if(!prediction_list.empty()){
        prediction_list = prediction_list + "/0";
    }
    std::string message;
    message = position +position_list + prediction_list;
    return message;

     */
    return "pls fix me";
}


void receive(void *arguments) {
    int partner;
    char buf[MAX];
    int control_agent_ID = ((Rec_thargs_t*)arguments)->control_agent_ID;
    const char *conf_message =((Rec_thargs_t*)arguments)->conf_message;
    while(true){

        RADIOReceive(&partner, buf, MAX);
        if((partner == control_agent_ID)){ //(partner == control_agent_ID) && ((strcmp(buf, conf_message) == 0))
            message_received = true;

        }
    }

}



[[noreturn]] void *comms(void *arguments)
{

    // ---------------------------------------------- params
    int i, my_id, partner, agent_num,pos_list_num, pred_list_num;
    int IDList[buffer];
    char buf[MAX];
    int control_agent_ID;
    const char *conf_message;
    local_map* local_map = ((C_thargs_t*)arguments)->_local_map;
    // track the current agents local map through the size of its position list and predictions list
    // initialise this with a size of 0
    pos_list_num=0;
    pred_list_num=0;

    // ---------------------------------------------- params

    // wait until the control agent sends out its signal to assert dominance over the network
    RADIOInit();
    my_id = RADIOGetID();
    LCDPrintf("Edge agent - my id is %d\n", my_id);
    pthread_mutex_lock(&agent);
    RADIOReceive(&partner, buf, MAX);
    LCDPrintf("%s is at ID %d \n",buf, partner);
    std::string tmp_string(buf);
    std::cout << tmp_string + "is at ID" + std::to_string(partner)<< std::endl;
    control_agent_ID = partner;
    conf_message = ("r/" +  std::to_string(my_id)).c_str();
    pthread_mutex_unlock(&agent);
    std::chrono::seconds interval( 4 );
    pthread_t c1;
    Rec_thargs_t thrgs_Rec;
    int mesID = 0;

    // ------------------------------------------------ used for logging messages
    const std::string logfile      =  getexepath() + "comms_logs/logfile_" + std::to_string(my_id) + ".txt";
    ofstream myfile;
    myfile.open (logfile, std::ios_base::app);
    myfile << "Thread created \n";
    // ------------------------------------------------ used for logging messages


    while(true) // infinite loop as we're always going to be scanning for comms and sending local map information through
    {
        // check to find other edge agents on the network - minimum number is 1 as this agent will be on the network
        pthread_mutex_lock(&agent);
        agent_num = RADIOStatus(IDList);
        if(agent_num > 1) {
            //local_map->position_list.size() > pos_list_num
            if (true) {
                std::string message = map_encoder(local_map, pos_list_num, pred_list_num);
                char message_array[message.length() + 1];
                strcpy(message_array, message.c_str());

                // save message to log file - Used in testing! ---------------------------------------------------------

                myfile.open (logfile, std::ios_base::app);
                myfile << "Partner:";
                myfile <<std::to_string(partner) + "\n";
                myfile << "message: ";
                myfile << message;
                myfile << "\n";
                myfile.close();

                // save message to log file - Used in testing! ---------------------------------------------------------

                //max amount of characters that can be sent to Python control agent  at once is 128 (boo python)
                // (documentation says 1024 bytes - this is wrong, its 1024 bits of 128 bytes = 128 chars)
                // further testing showed that it was actually 100 bytes or less - unsure why
                // therefore, check if characters too long and send in parts
                size_t size = sizeof(message_array) / sizeof(message_array[0]);
                if(size >= MAX){
                    // determine number of packets that you'll have to send and send start message
                    int num_packets =  (ceil( static_cast< float >(size) / (MAX - 7)));
                    if(num_packets < 99){
                        std::string mesID_str = std::to_string(mesID);
                        if(mesID<10) {
                            mesID_str = "0" + mesID_str;
                        }
                        char const *mesID_ch = mesID_str.c_str();
                        std::string start_message = "s|" + std::to_string(num_packets) + "|" + std::to_string(size) + "|"  +mesID_str + "|";
                        char start_message_array[start_message.length() + 1];
                        strcpy(start_message_array, start_message.c_str());
                        RADIOSend(control_agent_ID, start_message_array);
                        // now send broken up packets of hte message
                        // prep message ID
                        int idx;
                        for(idx = 0; idx < num_packets-1; idx++){
                            int start_pos = (idx)*(MAX - 7);
                            char tmp_arr[MAX] ;
                            memcpy(tmp_arr, message_array + start_pos /* Offset */, (MAX - 7) /* Length */);
                            // add in message ID and message number
                            // note that the max number of packets that can be sent is 99
                            // prep packet number
                            std::string pack_num_str = std::to_string(idx);
                            if(mesID<10) {
                                pack_num_str = "0" + pack_num_str;
                            }
                            char const *packet_num_ch = pack_num_str.c_str();
                            //add the stuff
                            tmp_arr[(MAX - 7)] = '|';
                            tmp_arr[(MAX - 6)] = mesID_ch[0];
                            tmp_arr[(MAX - 5)] = mesID_ch[1];
                            tmp_arr[(MAX - 4)] = '|';
                            tmp_arr[(MAX - 3)] = packet_num_ch[0];
                            tmp_arr[(MAX - 2)] = packet_num_ch[1];
                            tmp_arr[(MAX -1)] = '|';
                            RADIOSend(control_agent_ID, tmp_arr);
                            OSWait(50); // allows time for control agent python API to read messages
                        }
                        // do the last packet
                        int last_msg_size = ((size - ((num_packets-1)*(MAX - 7)))+7); // 6 here and not 7 as we want to remove the char last character ( \000) as having it before end of message causes data loss
                        char last_msg_arr[last_msg_size] ;
                        memcpy(last_msg_arr, message_array + (idx)*(MAX - 7) /* Offset */, (last_msg_size -8) /* Length */);
                        std::string pack_num_str = std::to_string(idx);
                        if(mesID<10) {
                            pack_num_str = "0" + pack_num_str;
                        }
                        char const *packet_num_ch = pack_num_str.c_str();
                        //add the stuff
                        last_msg_arr[(last_msg_size - 8)] = '|';
                        last_msg_arr[(last_msg_size - 7)] = mesID_ch[0];
                        last_msg_arr[(last_msg_size - 6)] = mesID_ch[1];
                        last_msg_arr[(last_msg_size - 5)] = '|';
                        last_msg_arr[(last_msg_size - 4)] = packet_num_ch[0];
                        last_msg_arr[(last_msg_size - 3)] = packet_num_ch[1];
                        last_msg_arr[(last_msg_size -2)] = '|';
                        last_msg_arr[(last_msg_size -1)] = '\000';

                        RADIOSend(control_agent_ID, last_msg_arr);
                        OSWait(50); // allows time for control agent python API to read messages

                        // iterate and reset the message ID
                        mesID++;
                        if(mesID>=100) {
                            mesID = 0;
                        }

                    }else{
                        LCDPrintf("Error sending message number: %d , number of packets: %d exceeds limit of 99 \n",mesID, num_packets);
                    }
                }else{
                    RADIOSend(control_agent_ID, message_array);
                }

                // send message and then wait for a confirmation message to ensure it was recieved
                /*
                message_received = false;
                while (!message_received) {
                    partner = control_agent_ID;
                    // receive messages
                    thrgs_Rec.conf_message = conf_message; // TODO - this is static so move it into receive fcn
                    thrgs_Rec.control_agent_ID = control_agent_ID;
                    pthread_mutex_lock(&agent);
                    pthread_create(&c1, NULL, reinterpret_cast<void *(*)(void *)>(receive), &thrgs_Rec);
                    std::this_thread::sleep_for(interval);
                    pthread_detach(c1);
                    pthread_mutex_unlock(&agent);
                    OSWait(1000); // give the system the opportunity to do other things
                }
                 */
                //pos_list_num = local_map->position_list.size();
                //pred_list_num = local_map->detected_feature_list.size();
            }
            /*  used in testing to ensure constant communication!
            message = (char*)"Message from edge agent";
            RADIOSend( partner, message);
             */

        }else{
            LCDPrintf("ERROR! Control agent disconnected from network!");
            std::cout << "ERROR! Control agent disconnected from network "<< std::endl;
        } // else - do nothing as there is nobody to communicate with

        pthread_mutex_unlock(&agent);
        OSWait(1000); //wait between each ping
    }


}

