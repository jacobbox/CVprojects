#include "SingleMove.hpp"

using namespace std;

/*
	Extra meaning:
		P = prmote
		C = Caste
		e = en-passunt offered
		E = en-passunt taken

*/

//int debugtemp = 0;


SingleMove::SingleMove(int src, int dest){
	this->source_tile = src;
	this->dest_tile = dest;
	this->extra = ' ';
	this->promo = ' ';
	
	//this->debug_num = debugtemp++;
	//cout << "SingleMove Made: ->" << this->debug_num << " : " << *this << endl;
}

SingleMove::SingleMove(int src, int dest,char extra){
	this->source_tile = src;
	this->dest_tile = dest;
	this->extra = extra;
	this->promo = ' ';
	
	//this->debug_num = debugtemp++;
	//cout << "SingleMove Made: ->" << this->debug_num << " : " << *this << endl; 
}


SingleMove::SingleMove(int src, int dest,char extra,char promo){
	this->source_tile = src;
	this->dest_tile = dest;
	this->extra = extra;
	this->promo = promo;
	
	//this->debug_num = debugtemp++;
	//cout << "SingleMove Made: ->" << this->debug_num << " : " << *this << endl; 
}

SingleMove::SingleMove(const SingleMove& sourceMove){
	this->source_tile = sourceMove.source_tile;
	this->dest_tile = sourceMove.dest_tile;
	this->extra = sourceMove.extra;
	this->promo = sourceMove.promo;
	
	//this->debug_num = debugtemp++;
	//cout << "SingleMove Copy: ->" << this->debug_num << " : " << *this << endl; 
}

SingleMove::SingleMove(string src_rep, string dest_rep) : 
            SingleMove(((56-src_rep[1])*8)+::toupper(src_rep[0])-65,((56-dest_rep[1])*8)+::toupper(dest_rep[0])-65) {}

SingleMove::SingleMove(string src_rep, string dest_rep, char extra) : SingleMove(src_rep, dest_rep){
	this->extra = extra;
}

SingleMove::SingleMove(string src_rep, string dest_rep, char extra, char promo) : SingleMove(src_rep, dest_rep){
	this->extra = extra;
	this->promo = promo;
}


SingleMove::~SingleMove(){
	//cout << "SingleMove Gone: <-" << this->debug_num << " : " << *this << endl; 
}

ostream& operator<<(ostream& os, const SingleMove& sm)
{
	if(0){
		if(sm.extra == ' '){
			os << "SM(" << sm.source_tile << "->" << sm.dest_tile << ')' ;
		} else {
			if(sm.promo == ' '){
				os << "SM(" << sm.source_tile << "->" << sm.dest_tile << ':' << sm.extra << ')';
			} else {
				os << "SM(" << sm.source_tile << "->" << sm.dest_tile << ':' << sm.extra << '-' << sm.promo << ')';
			}
		}
    } else {
    	os << (char)(65+(sm.source_tile % 8)) << 8-(sm.source_tile / 8) 
    	   << (char)(65+(sm.dest_tile % 8))   << 8-(sm.dest_tile / 8);
    	if(sm.promo != ' '){
    		os << sm.promo;
    	}
    }
    
    return os;
}








void printMoveVector(vector<SingleMove>& vsm){
	//guardian for the empty vector
	if(vsm.size() == 0){
		cout << "[NIL]" << endl;
		return;
	}
	
	cout << vsm[0];
	for(int i = 1; i < vsm.size(); i++){
		cout << ", " << vsm[i] ;
	}
	cout << endl;
}










