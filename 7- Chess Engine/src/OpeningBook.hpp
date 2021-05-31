#ifndef __OPENINGBOOK__
#define __OPENINGBOOK__ 1

/*-----------------includes-----------------*/
#include<unordered_map>
#include<vector>
#include<string>
#include<iostream>
#include<fstream>
#include<utility>


#include <stdio.h>

#include "SingleMove.hpp"
#include "ChessBoard.hpp"

/*-----------------Classes------------------*/

namespace OPENINGBOOK_INTERNAL {
	class PreservingHasher
	{
		public:
			size_t operator()(const size_t& val) const
			{
				return val;
			}
	};
}

class OpeningBook: public std::unordered_map<size_t,std::vector<SingleMove>,OPENINGBOOK_INTERNAL::PreservingHasher>{
	
	public:
		//constructor
		OpeningBook();
		OpeningBook(char);
	
		// Usage
		char contains(size_t);
		void add(size_t, SingleMove&);
		void add(size_t, std::vector<SingleMove>&);
		void add(ChessBoard&, std::vector<SingleMove>&);
		
		void appendMove(ChessBoard&, SingleMove&);
		void appendMove(size_t, SingleMove&);
		//IO
		void loadBookFromFile();
		void loadBookFromFile(std::string);
		
		void parseLine(std::string);
};


/*----------------Prototypes----------------*/




#endif
