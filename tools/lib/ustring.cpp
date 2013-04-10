#include "ustring.h"
#include <iostream>

using namespace std;

ustring::ustring ()
{
	data = vector <string> ();
}

ustring::ustring (string in)
{
	parse (in);
	ustring ();
}

void ustring::parse (string in)
{
	int L = in.length();

	for (int i=0 ;i<L ;i++)
	{
		int tmp = (unsigned char)in[i];

		if (tmp<128)
		{
			string s = "";
			s += in[i];
			data.push_back (s);
		}
		else
		{
			int count = 1;

			while ((tmp >> 7-count) & 0x01)
				count++;

			data.push_back (in.substr (i, count));

			i += count-1;
		}
	}
}

int ustring::length ()
{
	return data.size();
}

string ustring::operator[] (int i)
{
	return data[i];
}
