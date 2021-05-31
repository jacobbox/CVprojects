#ifndef __NODE__
#define __NODE__ 1


/*-----------------includes-----------------*/
//#include<algorithm>
#include<iostream>
//#include<vector>
//#include<string>

#include "SingleMove.hpp"

/*----------------prototypes----------------*/


/*-----------------classes------------------*/


class Node{
	public:
		SingleMove move;
		int value;
		int depth;
		
		//Constructors
		Node(SingleMove&,int,int);
		
		
		
		friend std::ostream& operator<<(std::ostream&, const Node&);
};





#endif
