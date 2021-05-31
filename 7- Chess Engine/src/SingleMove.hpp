#ifndef __SINGLEMOVE__
#define __SINGLEMOVE__ 1


/*-----------------includes-----------------*/
#include<iostream>
#include<vector>
#include<string>

/*-----------------classes------------------*/


class SingleMove{
	public:
		int source_tile;
		int dest_tile;
		char extra;
		char promo;
		
		int debug_num;
		
		SingleMove(int,int);
		SingleMove(int,int,char);
		SingleMove(int,int,char,char);
		SingleMove(std::string,std::string);
		SingleMove(std::string,std::string,char);
		SingleMove(std::string,std::string,char,char);
		SingleMove(const SingleMove&);
		~SingleMove();
		
		friend std::ostream& operator<<(std::ostream&, const SingleMove&);
		
};

/*----------------prototypes----------------*/

void printMoveVector(std::vector<SingleMove>&);


#endif
