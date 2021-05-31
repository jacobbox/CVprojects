#ifndef __TTABLE__
#define __TTABLE__ 1

/*-----------------includes-----------------*/
#include<unordered_map>
#include<utility>

#include <stdio.h>

#include "ChessBoard.hpp"

/*-----------------Classes------------------*/
namespace TTABLE_INTERNAL {
	class PreservingHasher
	{
		public:
			size_t operator()(const size_t& val) const
			{
				return val;
			}
	};
}

class Ttable: public std::unordered_map<size_t,std::pair<int,int>,TTABLE_INTERNAL::PreservingHasher>{
	
	public:
		char contains(size_t);
		void add(size_t, int, int);
		void add(ChessBoard&, int, int);
};


/*----------------Prototypes----------------*/




#endif
