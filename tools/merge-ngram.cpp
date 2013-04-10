#include <iostream>
#include <map>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "lib/arg.h"
#include "lib/ustring.h"
#include "lib/merge.h"

using namespace std;

map <string, string> args;
vector <string> files;

int main (int argc, char *argv[])
{
	args["-o"] = "-";
	args["-tmp"] = "/tmp";
	parse_arg (argc, argv, args, files);

	if (files.size()==0)
		files.push_back (":STDIN");

	merge (files, args["-o"]);

	return 0;
}

