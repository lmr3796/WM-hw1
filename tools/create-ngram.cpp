#include <iostream>
#include <map>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <queue>
#include "lib/arg.h"
#include "lib/ustring.h"
#include "lib/merge.h"

#define HASH_SIZE_TERM 1000000

using namespace std;

map <string, string> args;
vector <string> files;
vector <string> tmp_files;
vector <int> tmp_terms;
int n;
map <string, int> terms[HASH_SIZE_TERM];
map <string, int> ngram;
int total_terms;

void process_ascii (char *buff);
void process_utf8 (char *buff);
void process_big5 (char *buff);

int hash_term (string in)
{
    //using djb2 hash function
    //Ref: http://www.cse.yorku.ca/~oz/hash.html

    int hash = 5381;
    int len = in.length();
    for (int i=0 ;i<len ;i++)
    {
        hash = ((hash << 5) + hash) + in[i];

        while (hash>=HASH_SIZE_TERM)
            hash -= HASH_SIZE_TERM;
    }

    return hash;
}

string gen_next_filename ()
{
	char tmp[8192];
	sprintf (tmp, "%s/ngram.%d.tmp", args["-tmp"].c_str(), tmp_files.size()+1);
	return string(tmp);
}

void write_tmpfile (string filename)
{
	FILE *fout;
	fout = fopen (filename.c_str(), "w");

	for (map<string, int>::iterator it=ngram.begin() ;it!=ngram.end() ;++it)
		fprintf (fout, "%s %d\n", (it->first).c_str(), it->second);
	ngram = map<string, int>();
	fclose (fout);

}

int main (int argc, char *argv[])
{
	args["-o"] = "-";
	args["-tmp"] = "/tmp";
	args["-n"] = "3";
	//args["-encoding"] = "utf-8";
	parse_arg (argc, argv, args, files);

	if (args.find("-vocab")==args.end())
	{
		cerr << "Error: no vocabulary file." << endl;
		exit (1);
	}


	n = atoi (args["-n"].c_str());

	FILE *fin;
	char buff[8192];

	total_terms = 0;
	cerr << "Loading vocabulary file...";
	fin = fopen (args["-vocab"].c_str(), "r");

	fgets (buff, 8192, fin);
	if (buff[strlen(buff)-1]=='\n')
		buff[strlen(buff)-1] = '\0';
	if (args.find("-encoding")==args.end())
		args["-encoding"] = buff;
	int id = 1;
	while (fgets (buff, 8192, fin))
	{
		if (buff[strlen(buff)-1]=='\n');
			buff[strlen(buff)-1] = '\0';
		terms[hash_term(buff)][buff] = id++;
		total_terms++;
	}
	fclose (fin);
	cerr << "Complete!" << endl;

	if (files.size()==0)
		files.push_back (":STDIN");

	int lines = 0;

	for (int k=0 ;k<files.size() ;k++)
	{
		if (files[k]==":STDIN")
			fin = stdin;
		else
			fin = fopen (files[k].c_str(), "r");

		lines = 0;
		while (fgets (buff, 8192, fin))
		{
			lines++;
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

			if (lines>600000)
			{
				string filename = gen_next_filename();
				tmp_files.push_back (filename);
				write_tmpfile (filename);
				lines = 0;
			}
		}


		fclose (fin);

		if (lines>0)
		{
			string filename = gen_next_filename();
			tmp_files.push_back (filename);
			write_tmpfile (filename);
		}
	}

	merge (tmp_files, args["-o"]);
	return 0;
}

void record_ngram ()
{
	string tmp = "";
	char buff[8192];
	for (int i=0 ;i<n ;i++)
	{
		sprintf (buff, "%d", tmp_terms[i]);
		if (i!=0)
			tmp += string("_") + buff;
		else
			tmp += buff;
	}
	ngram[tmp] ++;
}

void process_term (string in)
{
	int curr_term = terms[hash_term(in)][in];

	if (tmp_terms.size()>=n-1)
	{
		if (tmp_terms.size()==n-1)
			tmp_terms.push_back (curr_term);
		else
			tmp_terms[n-1] = curr_term;

		record_ngram ();
		
		for (int i=0 ;i<n-1 ;i++)
			tmp_terms[i] = tmp_terms[i+1];
	}
	else
		tmp_terms.push_back (curr_term);
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
