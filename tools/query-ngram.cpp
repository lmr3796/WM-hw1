#include <iostream>
#include <map>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "lib/arg.h"
#include "lib/ustring.h"

using namespace std;

map <string, string> args;
vector <string> files;
vector <int> tmp_terms;
vector <string> inputs;
vector <string> input_ngrams;
vector <int> ans;

map <string, int> terms;

void process_ascii (char *buff);
void process_utf8 (char *buff);
void process_big5 (char *buff);

void record_ngram ();

int main (int argc, char *argv[])
{
	args["-o"] = "-";
	args["-tmp"] = "/tmp";
	//args["-encoding"] = "utf-8";
	parse_arg (argc, argv, args, files);

	if (args.find("-vocab")==args.end())
	{
		cerr << "Error: no vocabulary file." << endl;
		exit (1);
	}

	if (args.find("-ngram")==args.end())
	{
		cerr << "Error: no ngram file." << endl;
		exit (1);
	}

	FILE *fin;
	char buff[8192];

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
		terms[buff] = id++;
	}
	fclose (fin);
	cerr << "Complete!" << endl;

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
			tmp_terms = vector <int> ();
			inputs.push_back (buff);
			ans.push_back (0);
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

			record_ngram ();
		}

		fclose (fin);
	}

	cerr << "Load ngram file...";
	fin = fopen (args["-ngram"].c_str(), "r");
	int freq;

	while (fscanf (fin, "%s %d", buff, &freq)==2)
	{
		for (int i=0 ;i<inputs.size() ;i++)
		{
			if (input_ngrams[i]==buff)
				ans[i] = freq;
		}
	}
	fclose (fin);
	cerr << "Complete!" << endl;

	FILE *fout;
	if (args["-o"]=="-")
		fout = stdout;
	else
		fout = fopen (args["-o"].c_str(), "w");

	for (int i=0 ;i<inputs.size() ;i++)
		fprintf (fout, "%d %s", ans[i], inputs[i].c_str());

	fclose (fout);

	return 0;
}

void record_ngram ()
{
	string tmp = "";
	char buff[8192];
	for (int i=0 ;i<tmp_terms.size() ;i++)
	{
		sprintf (buff, "%d", tmp_terms[i]);
		if (i!=0)
			tmp += string("_") + buff;
		else
			tmp += buff;
	}
	input_ngrams.push_back (tmp);
}

void process_term (string in)
{
	int curr_term = terms[in];

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
