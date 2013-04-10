#ifndef USTRING_H
#define USTRING_H

#include <vector>
#include <string>

using namespace std;

class ustring
{
private:
	vector <string> data;
public:
	ustring ();
	ustring (string);
	void parse (string);
	int length ();
	string operator[] (int);
};

#endif
