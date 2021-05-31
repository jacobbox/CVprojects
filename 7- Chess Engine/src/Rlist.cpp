#include "Rlist.hpp"

using namespace std;



char Rlist::contains(size_t zhash){
	if (this->find(zhash) == this->end()){
		return 0;
	}
    return 1;
}

void Rlist::increment(ChessBoard& board){
	this->increment(board.zhash);
}

void Rlist::increment(size_t zhash){
	if(this->contains(zhash)){
		(*this)[zhash]++;
	} else {
		this->emplace(zhash,1);
	}
}

int Rlist::get(size_t zhash){
	if(this->contains(zhash)){
		return (*this)[zhash];
	} else {
		return 0;
	}
}


