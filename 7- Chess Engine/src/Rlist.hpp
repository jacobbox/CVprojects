#ifndef __RLIST__
#define __RLIST__ 1

/*-----------------includes-----------------*/
#include<unordered_map>
#include<utility>

#include <stdio.h>

#include "ChessBoard.hpp"

/*-----------------Classes------------------*/
namespace RLIST_INTERNAL {
	class PreservingHasher
	{
		public:
			size_t operator()(const size_t& val) const
			{
				return val;
			}
	};
}

class Rlist: public std::unordered_map<size_t,int,RLIST_INTERNAL::PreservingHasher>{
	
	public:
		char contains(size_t);
		void increment(ChessBoard&);
		void increment(size_t);
		int get(size_t);
};


/*----------------Prototypes----------------*/




#endif
