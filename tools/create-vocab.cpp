#include <iostream>
#include <map>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "lib/arg.h"
#include "lib/ustring.h"

using namespace std;

#define HASH_SIZE 1000000

map <string, string> args;
vector <string> files;
map <string, int> terms[HASH_SIZE];

void process_ascii (char *buff);
void process_utf8 (char *buff);
void process_big5 (char *buff);

int hash (string &in)
{
	//using djb2 hash function
	//Ref: http://www.cse.yorku.ca/~oz/hash.html
	
	int hash = 5381;
	int len = in.length();
	for (int i=0 ;i<len ;i++)
	{
		hash = ((hash << 5) + hash) + in[i];

		while (hash>=HASH_SIZE)
			hash -= HASH_SIZE;
	}

	return hash;
}

int main (int argc, char *argv[])
{
	args["-o"] = "-";
	args["-tmp"] = "/tmp";
	args["-encoding"] = "utf8";
	parse_arg (argc, argv, args, files);

	FILE *fin;
	char buff[8192];

	if (files.size()==0)
		files.push_back (":STDIN");

	for (int k=0 ;k<files.size() ;k++)
	{
		if (files[k]==":STDIN")
			fin = stdin;
		else
			fin = fopen (files[k].c_str(), "r");

		while (fgets (buff, 8192, fin))
		{
			if (args["-encoding"]=="ascii")
				process_ascii (buff);
			else if (args["-encoding"]=="utf8")
				process_utf8 (buff);
			else if (args["-encoding"]=="big5")
				process_big5 (buff);
			else
			{
				cerr << "Unrecognized character encoding: " << args["-encoding"] << endl;
				exit (1);
			}
		}

		fclose (fin);
	}

	FILE *fout;
	if (args["-o"]=="-")
		fout = stdout;
	else
		fout = fopen (args["-o"].c_str(), "w");

	fprintf (fout, "%s\n", args["-encoding"].c_str());

	for (int k=0 ;k<HASH_SIZE ;k++)
	{
		for (map<string, int>::iterator it=terms[k].begin() ;it!=terms[k].end() ;++it)
			fprintf (fout, "%s\n", (it->first).c_str());
	}

	fclose (fout);

	return 0;
}

bool is_term_cons (char in)
{
	if ('a'<=in and in<='z')
		return true;
	if ('A'<=in and in<='Z')
		return true;
	if ('0'<=in and in<='9')
		return true;
	if (in=='-' and in=='\'' and in=='_')
		return true;
	return false;
}

void inline process_term (string in)
{
	terms[hash(in)][in] = 1;
}

void process_ascii (char *buff)
{
	int len = strlen (buff);
	char term_buf[8192];
	int term_len = 0;

	for (int i=0 ;i<len ;i++)
	{
		if (buff[i]==' ' or buff[i]=='\t' or buff[i]=='\n' or buff[i]=='\r')
		{
			if (term_len>0)
			{
				term_buf[term_len] = '\0';
				process_term (term_buf);
				term_len = 0;
			}
		}
		else if (is_term_cons (buff[i]))
			term_buf[term_len++] = buff[i];
		else
		{
			if (term_len>0)
			{
				term_buf[term_len] = '\0';
				process_term (term_buf);
				term_len = 0;
			}
			term_buf[0] = buff[i];
			term_buf[1] = '\0';
			process_term (term_buf);
		}
	}
}

void process_utf8 (char *buff)
{
	ustring data;
	data.parse (buff);
	char term_buf[8192];
	int term_len = 0;

	int len = data.length();

	for (int i=0 ;i<len ;i++)
	{
		if (data[i].length()==1)
		{
			char tmp = data[i][0];
			if (tmp==' ' or tmp=='\t' or tmp=='\n' or tmp=='\r')
			{
				if (term_len>0)
				{
					term_buf[term_len] = '\0';
					process_term (term_buf);
					term_len = 0;
				}
			}
			else if (is_term_cons (tmp))
				term_buf[term_len++] = tmp;
			else
			{
				if (term_len>0)
				{
					term_buf[term_len] = '\0';
					process_term (term_buf);
					term_len = 0;
				}
				process_term (data[i]);
			}
		}
		else
		{
			if (term_len>0)
			{
				term_buf[term_len] = '\0';
				process_term (term_buf);
				term_len = 0;
			}
			process_term (data[i]);
		}
	}
}
void process_big5 (char *buff)
{
	char term_buf[8192];
	int term_len = 0;

	int len = strlen (buff);

	for (int i=0 ;i<len ;i++)
	{
		if ((unsigned)buff[i]<=0x7F)
		{
			char tmp = buff[i];
			if (tmp==' ' or tmp=='\t' or tmp=='\n' or tmp=='\r')
			{
				if (term_len>0)
				{
					term_buf[term_len] = '\0';
					process_term (term_buf);
					term_len = 0;
				}
			}
			else if (is_term_cons (tmp))
				term_buf[term_len++] = tmp;
			else
			{
				if (term_len>0)
				{
					term_buf[term_len] = '\0';
					process_term (term_buf);
					term_len = 0;
				}
				term_buf[0] = tmp;
				term_buf[1] = '\0';
				process_term (term_buf);
			}
		}
		else
		{
			if (term_len>0)
			{
				term_buf[term_len] = '\0';
				process_term (term_buf);
				term_len = 0;
			}

			term_buf[0] = buff[i++];
			//if ((unsigned)buff[i]<0x40 or (unsigned)buff[i]>0x7E)
			//	continue;
			term_buf[1] = buff[i];
			term_buf[2] = '\0';

			process_term (term_buf);
		}
	}
}
