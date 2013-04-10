#include <map>
#include <vector>
#include "arg.h"

using namespace std;

void parse_arg (int argc, char *argv[], map <string, string> &args, vector <string> &files)
{
	for (int i=1 ;i<argc ;i++)
	{
		if (argv[i][0]=='-')
		{
			string index = argv[i];
			args[index] = argv[++i];
		}
		else
			files.push_back (argv[i]);
	}
}
