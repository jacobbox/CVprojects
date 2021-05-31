#include "Ttable.hpp"

using namespace std;



char Ttable::contains(size_t zhash){
	if (this->find(zhash) == this->end()){
		return 0;
	}
    return 1;
}

void Ttable::add(size_t zhash, int depth, int eval){
	this->emplace(zhash,make_pair(depth,eval));
}

void Ttable::add(ChessBoard& board, int depth, int eval){
	this->emplace(board.zhash,make_pair(depth,eval));
}
