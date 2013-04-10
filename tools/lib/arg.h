#ifndef ARG_H
#define ARG_H

#include <map>
#include <vector>
#include <string>

using namespace std;

void parse_arg (int argc, char *argv[], map <string, string> &args, vector <string> &files);

#endif
