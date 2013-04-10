#include <iostream>
#include <map>
#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <queue>
#include "merge.h"

using namespace std;

class Element
{
private:
public:
	string data;
	int freq;
	int from;

	friend bool operator < (Element, Element);
};

bool operator < (Element a, Element b)
{
	return a.data > b.data;
}

class MyQue
{
private:
	priority_queue <Element> que;
	FILE *fin[8192];
	bool end[8192];
	char buf[8192];
	int freq;

public:
	MyQue (vector <string> &files);
	Element pop ();
	void push (string, int, int);
	bool empty () { return que.empty(); };
};

MyQue::MyQue (vector <string> &files)
{
	que = priority_queue <Element> ();

	for (int i=0 ;i<files.size () ;i++)
	{
		if (files[i]==":STDIN")
			fin[i] = stdin;
		else
			fin[i] = fopen (files[i].c_str(), "r");
		end[i] = 0;
	}

	Element tmp;

	for (int i=0 ;i<files.size() ;i++)
	{
		end[i] = (fscanf (fin[i], "%s %d", buf, &freq)!=2);
		if (!end[i])
			push (buf, freq, i);
	}

}

Element MyQue::pop ()
{
	Element e = que.top ();
	que.pop ();

	if (!end[e.from])
	{
		end[e.from] = (fscanf (fin[e.from], "%s %d", buf, &freq)!=2);
		if (!end[e.from])
			push (buf, freq, e.from);
	}

	return e;
}

void MyQue::push (string d, int fre, int fro)
{
	Element tmp;
	tmp.data = d;
	tmp.freq = fre;
	tmp.from = fro;
	que.push (tmp);
}

void merge (vector <string> &files, string outfile)
{
	if (files.size()==0)
		files.push_back (":STDIN");


	FILE *fout;
	if (outfile=="-")
		fout = stdout;
	else
		fout = fopen (outfile.c_str(), "w");

	MyQue que (files);
	Element curr = que.pop();

	while (!que.empty())
	{
		Element e = que.pop ();
		if (curr.data==e.data)
			curr.freq += e.freq;
		else
		{
			fprintf (fout, "%s %d\n", curr.data.c_str(), curr.freq);
			curr = e;
		}
	}

	fprintf (fout, "%s %d\n", curr.data.c_str(), curr.freq);

	fclose (fout);
}

