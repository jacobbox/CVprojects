#include "ChessBoard.hpp"
#include "ChessAI.hpp"
#include "Rlist.hpp"


using namespace std;

/*--------- Define Static class members values ---------*/
//============boards =====================//
char ChessBoard::blankBoard[65] = {' ',' ',' ',' ',' ',' ',' ',' ',
                                   ' ',' ',' ',' ',' ',' ',' ',' ',
                                   ' ',' ',' ',' ',' ',' ',' ',' ',
                                   ' ',' ',' ',' ',' ',' ',' ',' ',
                                   ' ',' ',' ',' ',' ',' ',' ',' ',
                                   ' ',' ',' ',' ',' ',' ',' ',' ',
                                   ' ',' ',' ',' ',' ',' ',' ',' ',
                                   ' ',' ',' ',' ',' ',' ',' ',' ','\0'
                                   };
                                   
char ChessBoard::baseBoard[65] = {'r','n','b','q','k','b','n','r',
                                  'p','p','p','p','p','p','p','p',
                                  ' ',' ',' ',' ',' ',' ',' ',' ',
                                  ' ',' ',' ',' ',' ',' ',' ',' ',
                                  ' ',' ',' ',' ',' ',' ',' ',' ',
                                  ' ',' ',' ',' ',' ',' ',' ',' ',
                                  'P','P','P','P','P','P','P','P',
                                  'R','N','B','Q','K','B','N','R','\0'
                                  };

int ChessBoard::baseWhiteIndexs[64] = {63,62,61,60,59,58,57,56,55,54,53,52,51,50,49,48};

int ChessBoard::baseBlackIndexs[64] = {0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10,11,12,13,14,15};

//==============matrixes===============//

int ChessBoard::kingEndMap[65] = {-10,-9 ,-8 ,-7 ,-7 ,-8 ,-9 ,-10,
                                  -9 ,-8 ,-6 ,-5 ,-5 ,-6 ,-8 ,-9 ,
                                  -8 ,-6 ,-3 ,-1 ,-1 ,-3 ,-6 ,-8 ,
                                  -7 ,-5 ,-1 , 0 , 0 ,-1 ,-5 ,-7 ,
                                  -7 ,-5 ,-1 , 0 , 0 ,-1 ,-5 ,-7 ,
                                  -8 ,-6 ,-3 ,-1 ,-1 ,-3 ,-6 ,-8 ,
                                  -9 ,-8 ,-6 ,-5 ,-5 ,-6 ,-8 ,-9 ,
                                  -10,-9 ,-8 ,-7 ,-7 ,-8 ,-9 ,-10,'\0'
                                  };

int ChessBoard::knightMap[65] =  {-20,-16,-6 ,-6 ,-6 ,-6 ,-16,-20,
                                  -16,-4 , 0 , 0 , 0 , 0 ,-4 ,-16,
                                  -6 , 0 , 0 , 1 , 1 , 0 , 0 ,-6 ,
                                  -6 , 0 , 1 , 2 , 2 , 1 , 0 ,-6 ,
                                  -6 , 0 , 1 , 2 , 2 , 1 , 0 ,-6 ,
                                  -6 , 0 , 0 , 1 , 1 , 0 , 0 ,-6 ,
                                  -16,-4 , 0 , 0 , 0 , 0 ,-4 ,-16,
                                  -20,-16,-6 ,-6 ,-6 ,-6 ,-16,-20,'\0'
                                  };
                                  
int ChessBoard::kingMidMapW[65] = {-8, -9, -9, -10, -10, -9, -9, -8,
								   -8, -9, -9, -10, -10, -9, -9, -8,
								   -8, -9, -9, -10, -10, -9, -9, -8,
								   -8, -9, -9, -10, -10, -9, -9, -8,
								   -6, -8, -8, -9 , -9 , -8, -8, -6,
								   -5, -6, -6, -6 , -6 , -6, -6, -5,
								   -1, -1, -4, -4 , -4 , -4, -1, -1,
								   -1,  0, -2, -4 , -1 , -2,  0, -1,'\0'
								   };

	
int ChessBoard::kingMidMapB[65] = {-1,  0, -2, -4 , -1 , -2,  0, -1,
								   -1, -1, -4, -4 , -4 , -4, -1, -1,
								   -5, -6, -6, -6 , -6 , -6, -6, -5,
								   -6, -8, -8, -9 , -9 , -8, -8, -6,
								   -8, -9, -9, -10, -10, -9, -9, -8,
								   -8, -9, -9, -10, -10, -9, -9, -8,
								   -8, -9, -9, -10, -10, -9, -9, -8,
								   -8, -9, -9, -10, -10, -9, -9, -8,'\0'
								   };

int ChessBoard::rookErlMapW[65] = {-10,-10,-10,-10,-10,-10,-10,-10,
								     3,  5,  5,  5,  5,  5,  5,  3,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								     0,-10,  1,  2,  2,  1,-10,  0,'\0'
								   };


int ChessBoard::rookErlMapB[65] = {  0,-10,  1,  2,  2,  1,-10,  0,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								   -11,-10,-10,-10,-10,-10,-10,-11,
								     3,  5,  5,  5,  5,  5,  5,  3,
								   -10,-10,-10,-10,-10,-10,-10,-10,'\0'
								   };
								   
int ChessBoard::pawnMapW[65] =     { 50, 50, 50, 50, 50, 50, 50, 50,
									 10, 10, 10, 10, 10, 10, 10, 10,
									  2,  2,  4,  6,  6,  4,  2,  2,
									  1,  1,  2,  5,  5,  2,  1,  1,
									  0,  0,  0,  4,  4,  0,  0,  0,
									  1, -1, -2,  0,  0, -2, -1,  1,
									  1,  2, -1, -4, -4,  2,  2,  1,
									  0,  0,  0,  0,  0,  0,  0,  0,'\0'
									  };

int ChessBoard::pawnMapB[65] =     {  0,  0,  0,  0,  0,  0,  0,  0,
									  1,  2,  2, -4, -4, -1,  2,  1,
									  1, -1, -2,  0,  0, -2, -1,  1,
									  0,  0,  0,  4,  4,  0,  0,  0,
									  1,  1,  2,  5,  5,  2,  1,  1,
									  2,  2,  4,  6,  6,  4,  2,  2,
									 10, 10, 10, 10, 10, 10, 10, 10,
									 50, 50, 50, 50, 50, 50, 50, 50,'\0'
									  };

int ChessBoard::MatinglineBN_Wb[65] =  { 50, 45, 40, 30, 20, 15, 10,  2,
										 45, 40, 30, 20, 15, 10,  3, 10,
										 40, 30, 20, 15, 10,  4, 10, 15,
										 30, 20, 15,  3,  0, 10, 15, 20,
										 20, 15, 10,  0,  3, 15, 20, 30,
										 15, 10,  4, 10, 15, 20, 30, 40,
										 10,  3, 10, 15, 20, 30, 40, 45,
										  2, 10, 15, 20, 30, 40, 45, 50,'\0'
										};
										  
int ChessBoard::MatinglineBN_Bb[65] =  {  2, 10, 15, 20, 30, 40, 45, 50,
										 10,  3, 10, 15, 20, 30, 40, 45,
										 15, 10,  4, 10, 15, 20, 30, 40,
										 20, 15, 10,  0,  3, 15, 20, 30,
										 30, 20, 15,  3,  0, 10, 15, 20,
										 40, 30, 20, 15, 10,  4, 10, 15,
										 45, 40, 30, 20, 15, 10,  3, 10,
										 50, 45, 40, 30, 20, 15, 10,  2,'\0'
										};
										
int ChessBoard::pawnPromoMapW[65] =     {70, 70, 70, 70, 70, 70, 70, 70,
										 30, 30, 30, 30, 30, 30, 30, 30,
										 15, 15, 15, 15, 15, 15, 15, 15,
										 10, 10, 10, 10, 10, 10, 10, 10,
										  6,  6,  6,  6,  6,  6,  6,  6,
										  3,  3,  3,  3,  3,  3,  3,  3,
										  1,  1,  1,  1,  1,  1,  1,  1,
										  0,  0,  0,  0,  0,  0,  0,  0,'\0'
										  };
										  
int ChessBoard::pawnPromoMapB[65] =     {  0,  0,  0,  0,  0,  0,  0,  0,
										   1,  1,  1,  1,  1,  1,  1,  1,
										   3,  3,  3,  3,  3,  3,  3,  3,
										   6,  6,  6,  6,  6,  6,  6,  6,
										  10, 10, 10, 10, 10, 10, 10, 10,
										  15, 15, 15, 15, 15, 15, 15, 15,
										  30, 30, 30, 30, 30, 30, 30, 30,
										  70, 70, 70, 70, 70, 70, 70, 70,'\0'
										  };

//==============const===============//

/*
 peices:
 		0 1 2 3 4 5 6 7 8 9 10 11
 		P p N n B b R r Q q K  k
 		
 		0-767: board (piece num * (board index+1))
 		768:   WhiteToMove
 		769:   CastleWhiteRight
 		770:   CastleWhiteLeft
 		771:   CastleBlackRight
 		772:   CastleBlackLeft
 		773:   EnPass A
 		774:   EnPass B
 		775:   EnPass C
 		776:   EnPass D
 		777:   EnPass E
 		778:   EnPass F
 		779:   EnPass G
 		780:   EnPass H
*/
size_t ChessBoard::zhashnums[781] = {};

/* === CONSTANT GENERATION === */
int ChessBoard::_unused_number_created_to_setVars = [](){
	srand(time(NULL));
	
	size_t hold;
	for(int i = 0; i < 781; i++){
		hold = 0;
		for(int j = 0; j < sizeof(size_t); j++){
			hold = (hold*256)+(rand() % 256);
		}
		zhashnums[i] = hold;
	}
	
	return 1;
}();

/*--------- Methods ---------*/

/*------ Supporting functions ------*/

/*
 * Assists in move gen by applyign a given offset and checking if piece can perfrom that move
 */
void ChessBoard::applyOffset(std::vector<SingleMove>& moves, int src_sq, int offset, int rowc, int colc, char isWhite, int rep = 8){
	int pos = src_sq;
	char piece;
	int row = src_sq/8;
	int col = src_sq%8;
	
	////OLD:cout << "off:" << offset << "| R:" << row << "~" << rowc << "| C:" << col << "~" << colc << endl;
	
	while (rep-- > 0){
		//---apply offset
		pos += offset;
		//---check for clashes
		///check if out of bounds
		if(pos < 0 || pos > 63){
			break;
		}
		piece = this->board[pos];
		
		//detect passing the edge
		row += rowc;
		col += colc;
		////OLD:cout << "now:" << pos << "| R:" << row << "~" << rowc << "| C:" << col << "~" << colc << endl;
		if(row < 0 || row > 7 || col < 0 || col > 7){
			////OLD:cout << "end:" << pos << "| R:" << row << "~" << rowc << "| C:" << col << "~" << colc << endl;
			break;
		}
		
		if(piece != ' ' && ((piece < 91 && isWhite) || (piece > 91 && !isWhite))){
			//own piece: break
			break;
		}
		//now no matter what we can move to at least this square so add the move:
		moves.emplace_back(src_sq,pos);
		//if capturing: break as cannot go through picies
		if(piece != ' '){
			break;
		}
	}
}

/**
 * Perfrom a liniar search through a vector of moves for a move with the specified source and destination, 
 * returning the index if such a moive exists and -1 otherwise.
 */
int ChessBoard::moveInVector(vector<SingleMove>& moves, int source, int dest){
	for(int i = 0; i < moves.size(); i++){
		if(moves[i].source_tile == source && moves[i].dest_tile == dest && (moves[i].promo == ' ' || moves[i].promo == 'Q' || moves[i].promo == 'q')){
			return i;
		}
	}
	return -1;
}

/**
 * Perfrom a liniar search through a vector of moves for a move with the specified source and destination, 
 * returning the index if such a moive exists and -1 otherwise.  Will ensure correct promo is picked if relevent.
 */
int ChessBoard::moveInVector(vector<SingleMove>& moves, int source, int dest, char promo){
	for(int i = 0; i < moves.size(); i++){
		if(moves[i].source_tile == source && moves[i].dest_tile == dest && 
		   (moves[i].promo == ' ' || moves[i].promo == promo)){
			return i;
		}
	}
	return -1;
}



/*------ Constructors ------*/
ChessBoard::ChessBoard(){
	//removed board copy as will be overwritten immediatly in all use cases anyway 
	//- this constructor just needs to be as fast as possible as it is called in main AI recursive call
	//copy(begin(ChessBoard::blankBoard), end(ChessBoard::blankBoard), begin(this->board));
}


//copy constructor
ChessBoard::ChessBoard(const ChessBoard &source){
	for(int i = 0; i < 64; i++){
		this->board[i] = source.board[i];
	}
	this->en_pass_index = source.en_pass_index;
	this->wck = source.wck;
	this->wcq = source.wcq;
	this->bck = source.bck;
	this->bcq = source.bcq;
	this->zhash = source.zhash;
	//speedups:
	this->whitePcCount = source.whitePcCount;
	this->blackPcCount = source.blackPcCount;
	this->whiteKingLoc = source.whiteKingLoc;
	this->blackKingLoc = source.blackKingLoc;
	for(int i = 0; i < source.whitePcCount; i++){
		this->whiteIndexs[i] = source.whiteIndexs[i];
	}
	for(int i = 0; i < source.blackPcCount; i++){
		this->blackIndexs[i] = source.blackIndexs[i];
	}
}


/*------ Board manipulation ------*/

/**
 * set the board - ignore flags
 */
void ChessBoard::setBoard(char source[]){
	for(int i = 0; i < 65; i++){
		this->board[i] = source[i];
	}
}

 
/**
 * perfectly duplicate a board
 */
void ChessBoard::cloneBoard(ChessBoard& source){
	for(int i = 0; i < 64; i++){
		this->board[i] = source.board[i];
	}
	this->en_pass_index = source.en_pass_index;
	this->wck = source.wck;
	this->wcq = source.wcq;
	this->bck = source.bck;
	this->bcq = source.bcq;
	this->zhash = source.zhash;
	//speedups:
	this->whitePcCount = source.whitePcCount;
	this->blackPcCount = source.blackPcCount;
	this->whiteKingLoc = source.whiteKingLoc;
	this->blackKingLoc = source.blackKingLoc;
	for(int i = 0; i < source.whitePcCount; i++){
		this->whiteIndexs[i] = source.whiteIndexs[i];
	}
	for(int i = 0; i < source.blackPcCount; i++){
		this->blackIndexs[i] = source.blackIndexs[i];
	}
}


/**
 * generate a board from fen
 */
char ChessBoard::loadFromFen(string fen){
	this->empty();
	this->wck = 0;
	this->wcq = 0;
	this->bck = 0;
	this->bcq = 0;
	
	int fenIndex = -1;
	int boardPointer = 0;
	char val;
	
	while(fen[++fenIndex] != ' '){
		val = fen[fenIndex];
		if(val == '/'){
			boardPointer += (8 - (boardPointer % 8)) % 8;
		} else if(val < 58 && val > 48){
			boardPointer += val-48;
		} else {
			this->addPiece(boardPointer,val);
			//update kingloc if needed
			switch(val){
				case 'K':
					whiteKingLoc = boardPointer;
					break;
				case 'k':
					blackKingLoc = boardPointer;
					break;
			}
			boardPointer += 1;
		}
	}
	
	char whiteToPlay;
	if(fen[++fenIndex] == 'w'){
		whiteToPlay = 1;
	} else {
		whiteToPlay = 0;
	}
	fenIndex++;
	
	while(fen[++fenIndex] != ' '){
		switch(fen[fenIndex]){
			case 'K':
				this->wck = 1;
				break;
			case 'Q':
				this->wcq = 1;
				break;
			case 'k':
				this->bck = 1;
				break;
			case 'q':
				this->bcq = 1;
				break;
		}
	}
	
	if(fen[++fenIndex] == '-'){
		fenIndex++;
	} else {
		this->en_pass_index = ((56-fen[fenIndex+1])*8)+fen[fenIndex]-65;
		fenIndex += 2;
	}
	
	return whiteToPlay;
}

/*
 * return the board and speedup info to the inital position
 * ignore flags
 */
void ChessBoard::reset(){
	this->setBoard(ChessBoard::baseBoard);
	this->whitePcCount = 16;
	this->blackPcCount = 16;
	for(int i = 0; i < 16; i++){
		this->whiteIndexs[i] = ChessBoard::baseWhiteIndexs[i];
		this->blackIndexs[i] = ChessBoard::baseBlackIndexs[i];
	}
	whiteKingLoc = 60;
	blackKingLoc = 4;
}

/*
 * Clear the board
 */
void ChessBoard::empty(){
	this->setBoard(ChessBoard::blankBoard);
	this->whitePcCount = 0;
	this->blackPcCount = 0;
	whiteKingLoc = -1;
	blackKingLoc = -1;
}

/*------ New Piece manipulation ------*/

void ChessBoard::removePiece(char sq){
	this->removePiece(sq,!(this->board[sq] > 91));
}
/*
 * Remove the piece at the specified square
 */
void ChessBoard::removePiece(char sq,char isWhite){
	if(isWhite){
		int* p = whiteIndexs;
		bool found = false;
		for(int i = 0; i < this->whitePcCount; i++){
			if(*(p+i) == sq){
				found = true;
				this->board[sq] = ' ';
				this->whitePcCount--;
			}
			if(found){
				*(p+i) = *(p+i+1);
			}
		}
	} else {
		int* p = blackIndexs;
		bool found = false;
		for(int i = 0; i < this->blackPcCount; i++){
			if(*(p+i) == sq){
				found = true;
				this->board[sq] = ' ';
				this->blackPcCount--;
			}
			if(found){
				*(p+i) = *(p+i+1);
			}
		}
	}
}

void ChessBoard::addPiece(char sq, char pc){
	this->addPiece(sq,pc,!(pc > 91));
}
/*
 * Add a piece to a specified square
 *
 * Should only be called on a square known empty else inconsistent speedup data may result
 */
void ChessBoard::addPiece(char sq, char pc, char isWhite){
	this->board[sq] = pc;
	if(isWhite){
		whiteIndexs[whitePcCount] = sq;
		whitePcCount++;
	} else {
		blackIndexs[blackPcCount] = sq;
		blackPcCount++;
	}
}

void ChessBoard::blindMove(SingleMove& move){
	this->blindMove(move.source_tile,move.dest_tile,!(this->board[move.source_tile] > 91));
}

void ChessBoard::blindMove(SingleMove& move, char isWhite){
	this->blindMove(move.source_tile,move.dest_tile,isWhite);
}

void ChessBoard::blindMove(int src, int dest){
	this->blindMove(src,dest,!(this->board[src] > 91));
}

/*
 * Perform a move from src to dest without regaurd for if the piece can make that move or setting flags
 * Does set speedups though
 */
void ChessBoard::blindMove(int src, int dest,char isWhite){
	//if the destination is not blank make it blank
	if(this->board[dest] != ' '){
		removePiece(dest);
	}
	//update the quikc itterate tables
	if(isWhite){
		int* p = whiteIndexs;
		for(int i = 0; i < this->whitePcCount; i++){
			if(*(p+i) == src){
				*(p+i) = dest;
				break;
			}
		}
	} else {
		int* p = blackIndexs;
		for(int i = 0; i < this->blackPcCount; i++){
			if(*(p+i) == src){
				*(p+i) = dest;
				break;
			}
		}
	}
	//make blind move
	this->board[dest] = this->board[src];
	this->board[src] = ' ';
	//update kingloc if needed
	switch(this->board[dest]){
		case 'K':
			whiteKingLoc = dest;
			break;
		case 'k':
			blackKingLoc = dest;
			break;
	}
}


void ChessBoard::setSquare(string sqrep, char pc){
	this->setSquare(((56-sqrep[1])*8)+::toupper(sqrep[0])-65,pc);
}
/*
 * Set the piece at a square to the one specified
 */
void ChessBoard::setSquare(int sq, char pc){
	if(this->board[sq] != ' '){
		removePiece(sq);
	}
	addPiece(sq,pc);
}


/*------ Evaluation ------*/

/*
 * Counts the points for each player based on the board position then returns 
 * the pair of points for white and black in that sequence
 */
pair<int,int> ChessBoard::getPointsOnBoard(){
	int w_points_on_board = 0;
	int b_points_on_board = 0;
	//get the points on the board
	char pc;
	int* sip = whiteIndexs;
	for(int i = 0; i < whitePcCount; sip++,i++){
		//Checks most common case first then binary search for correct piece. 
		pc = this->board[*sip];
		if(pc == 'P'){
			w_points_on_board += 1;
			continue;
		}
		if(pc >80){
			if(pc == 'R'){
				w_points_on_board += 5;
				continue;
			} else {
				w_points_on_board += 9;
				continue;
			}
		} else {
			if(pc == 'B'){
				w_points_on_board += 3;
				continue;
			} else if (pc == 'N'){
				w_points_on_board += 3;
				continue;
			}
		}
	}
	
	sip = blackIndexs;
	for(int i = 0; i < blackPcCount; sip++,i++){
		//Checks most common case first then binary search for correct piece. 
		pc = this->board[*sip];
		if(pc == 'p'){
			b_points_on_board += 1;
			continue;
		}
		if(pc >112){
			if(pc == 'r'){
				b_points_on_board += 5;
				continue;
			} else {
				b_points_on_board += 9;
				continue;
			}
		} else {
			if(pc == 'b'){
				b_points_on_board += 3;
				continue;
			} else if (pc == 'n'){
				b_points_on_board += 3;
				continue;
			}
		}
	}
	
	return make_pair(w_points_on_board,b_points_on_board);
}

/*
 * Estimate the worth of a board (resolves the value of leaves of a search)
 */
int ChessBoard::courseValue(){	
	pair<int,int> respair = this->getPointsOnBoard();
	int w_points_on_board = respair.first;
	int b_points_on_board = respair.second;
	
	int val = 0;
	int Bc = 0;//bishop counts
	int bc = 0;
	char bi = -1;//last bishop index
	int Nc = 0;//knight counts
	int nc = 0;
	
	int Wendness = max(0,(60-(10*w_points_on_board))/6);
	int Bendness = max(0,(60-(10*b_points_on_board))/6);
	int Gendness = min((Wendness+Bendness),10);
	
	int Wearlyness = max(0,5-max(0,(39-w_points_on_board)-2))*2;
	int Bearlyness = max(0,5-max(0,(39-b_points_on_board)-2))*2;
	
	int Wmidness = max(max(0,80-max(0,(10*w_points_on_board)-70))/8 - Gendness,0);
	int Bmidness = max(max(0,80-max(0,(10*b_points_on_board)-70))/8 - Gendness,0);
	int Gmidness = min(((Wmidness+Bmidness)*14)/20,10);
	
	
	/*
	cout << " Wendness " << Wendness << " Bendness " << Bendness << " Gendness " << Gendness
	     << " Wmidness " << Wmidness << " Bmidness " << Bmidness
	     << " Gmidness " << Gmidness << " Wearlyness " << Wearlyness<< " Bearlyness " << Bearlyness << endl;
	//*/
	
	char pc;
	char pawnAttackable;
	char pawnDefended;
	char pawnDefendable;
	char pawnDefendCount;
	int* sip = whiteIndexs;
	for(int i = 0; i < whitePcCount; sip++,i++){
		//Checks most common case first then binary search for correct piece. 
		pc = this->board[*sip];
		if(pc == 'P'){
			val += 100+(ChessBoard::pawnMapW[i])+(Gendness*ChessBoard::pawnPromoMapW[i]/4);
			pawnAttackable = (  ((*sip) % 8 != 0 && this->board[(*sip)-9] == 'p')  ||
							    ((*sip) % 8 != 7 && this->board[(*sip)-7] == 'p')
							 );
			pawnDefended =   (  ((*sip) % 8 != 0 && this->board[(*sip)+7] == 'P')  ||
							    ((*sip) % 8 != 7 && this->board[(*sip)+9] == 'P')
							 );
			pawnDefendable=(  (*sip) / 8 <= 5 && (
			    ((*sip) % 8 != 0 && this->board[(*sip)+7] == ' ' && this->board[(*sip)+15] == 'P')  ||
				((*sip) % 8 != 7 && this->board[(*sip)+9] == ' ' && this->board[(*sip)+17] == 'P')
							 ));
			pawnDefendCount =    (  ((*sip) % 8 != 0 && this->board[(*sip)-9] == 'P')  +
							    ((*sip) % 8 != 7 && this->board[(*sip)-7] == 'P')
							 );
			if(pawnAttackable && !pawnDefended){
				val -= 7;
			}
			if(!pawnAttackable && (pawnDefended || pawnDefendable)){
				val += 1;
			}
			val += pawnDefendCount*pawnDefendCount;//makes defending pawns more valuble
			continue;
		}
		if(pc >80){
			if(pc == 'R'){
				val += 500+((Wearlyness*ChessBoard::rookErlMapW[i])/10);
				continue;
			} else {//queen
				val += 900;
				continue;
			}
		} else {
			if(pc == 'B'){
				val += 315;
				Bc += 1;
				bi = i;
				continue;
			} else if (pc == 'N'){
				val += 300+(ChessBoard::knightMap[i]);
				Nc += 1;
				continue;
			} else {//king
				val += 100000+((Wendness*ChessBoard::kingEndMap[i])/2)+((Gmidness*ChessBoard::kingMidMapW[i])/5);
				continue;
			}
		}
	}
	
	sip = blackIndexs;
	for(int i = 0; i < blackPcCount; sip++,i++){
		//Checks most common case first then binary search for correct piece. 
		pc = this->board[*sip];
		if(pc == 'p'){
			val -= 100+(ChessBoard::pawnMapB[i])+(Gendness*ChessBoard::pawnPromoMapB[i]/4);
			pawnAttackable = (  ((*sip) % 8 != 0 && this->board[(*sip)+7] == 'P')  ||
							    ((*sip) % 8 != 7 && this->board[(*sip)+9] == 'P')
							 );
			pawnDefended =   (  ((*sip) % 8 != 0 && this->board[(*sip)-9] == 'p')  ||
							    ((*sip) % 8 != 7 && this->board[(*sip)-7] == 'p')
							 );
			pawnDefendable=(  (*sip) / 8 >= 4 && (
			    ((*sip) % 8 != 0 && this->board[(*sip)-9] == ' ' && this->board[(*sip)-17] == 'p')  ||
				((*sip) % 8 != 7 && this->board[(*sip)-7] == ' ' && this->board[(*sip)-15] == 'p')
							 ));
			pawnDefendCount =    (  ((*sip) % 8 != 0 && this->board[(*sip)+7] == 'p')  +
							    ((*sip) % 8 != 7 && this->board[(*sip)+9] == 'p')
							 );
			if(pawnAttackable && !pawnDefended){
				val += 30;
			}
			if(!pawnAttackable && (pawnDefended || pawnDefendable)){
				val -= 5;
			}
			val -= pawnDefendCount*pawnDefendCount*5;//makes defending pawns more valuble
			continue;
		}
		if(pc > 112){
			if(pc == 'r'){
				val -= 500+((Bearlyness*ChessBoard::rookErlMapB[i])/10);
				continue;
			} else {//queen
				val -= 900;
				continue;
			}
		} else {
			if(pc == 'b'){
				val -= 315;
				bc += 1;
				bi = i;
				continue;
			} else if (pc == 'n'){
				val -= 300+(ChessBoard::knightMap[i]);
				nc += 1;
				continue;
			} else {//king
				val -= 100000+((Bendness*ChessBoard::kingEndMap[i])/2)+((Gmidness*ChessBoard::kingMidMapB[i])/5);
				continue;
			}
		}
	}
	
	val += ((Bc > 2)-(bc > 2))*30;
	
		
	//as max dis = 14 7 would mean up to 20 for optimal placement to make 
	// value added less than that added by centering it is 14
	val += ((Wendness-Bendness)*(abs(whiteKingLoc % 8 - blackKingLoc % 8)+abs(whiteKingLoc / 8 - blackKingLoc / 8)))/14;
	
	//enable mating lines if relevent
	if(b_points_on_board == 0 && w_points_on_board == 6 && Bc == 1 && Nc == 1){
		char bishop_on_white = ((bi+1) % 2);
		if(bishop_on_white){
			val += ChessBoard::MatinglineBN_Wb[this->blackKingLoc];
		} else {
			val += ChessBoard::MatinglineBN_Bb[this->blackKingLoc];
		}
	} else if(w_points_on_board == 0 && b_points_on_board == 6 && bc == 1 && nc == 1){
		char bishop_on_white = ((bi+1) % 2);
		if(bishop_on_white){
			val -= ChessBoard::MatinglineBN_Wb[this->whiteKingLoc];
		} else {
			val -= ChessBoard::MatinglineBN_Bb[this->whiteKingLoc];
		}
	}
	
	return val;
}

void ChessBoard::addSquareMoves(vector<SingleMove>& moves, int sq){
	this->addSquareMoves(moves,sq,'N');
}
/*
 * Adds all moves that can be made from a square, sq, to the supplied move vector
 */
void ChessBoard::addSquareMoves(vector<SingleMove>& moves, int sq, char flag){
	
	char piece = this->board[sq];
	char isWhite = !(piece > 91);
	
	switch(piece){
		case 'P'://OPP: Pawn first as most common
			//forward
			if(this->board[sq-8] == ' '){
				if(sq <= 15 && sq >= 8){//OPP: check most limiting condition first
					moves.emplace_back(sq,sq-8,'P','Q');
					if(flag != 'O'){
						moves.emplace_back(sq,sq-8,'P','N');
						moves.emplace_back(sq,sq-8,'P','R');
						moves.emplace_back(sq,sq-8,'P','B');
					}
				} else {
					moves.emplace_back(sq,sq-8);
				}
			}
			//capture
			if(sq % 8 != 7 && this->board[sq-7] > 91){
				if(sq <= 15 && sq >= 8){//OPP: check most limiting condition first
					moves.emplace_back(sq,sq-7,'P','Q');
					if(flag != 'O'){
						moves.emplace_back(sq,sq-7,'P','N');
						moves.emplace_back(sq,sq-7,'P','R');
						moves.emplace_back(sq,sq-7,'P','B');
					}
				} else {
					moves.emplace_back(sq,sq-7);
				}
				
			}
			if(sq % 8 != 0 && this->board[sq-9] > 91){
				if(sq <= 15 && sq >= 8){//OPP: check most limiting condition first
					moves.emplace_back(sq,sq-9,'P','Q');
					if(flag != 'O'){
						moves.emplace_back(sq,sq-9,'P','N');
						moves.emplace_back(sq,sq-9,'P','R');
						moves.emplace_back(sq,sq-9,'P','B');
					}
				} else {
					moves.emplace_back(sq,sq-9);
				}
			}
			//take via en-passaunt
			if((sq % 8 != 7 && this->en_pass_index == sq-7 ) || (sq % 8 != 0 && this->en_pass_index == sq-9 )){
				moves.emplace_back(sq,this->en_pass_index,'E');
			}
			//first move
			if(sq >= 48 && sq <= 55 && this->board[sq-8] == ' ' && this->board[sq-16] == ' '){
				//flag for possible en passuant if it is a thing 
				//(dosen't check for edge wrapping as that is done taking side)
				if(this->board[sq-15] == 'p' || this->board[sq-17] == 'p'){
					moves.emplace_back(sq,sq-16,'e');
				} else {
					moves.emplace_back(sq,sq-16);
				}
			}
			break;
		case 'p'://OPP: Pawn first as most common
			//forward
			if(this->board[sq+8] == ' '){
				if(sq >= 48 && sq <= 55){//OPP: check most limiting condition first
					moves.emplace_back(sq,sq+8,'P','q');
					if(flag != 'O'){
						moves.emplace_back(sq,sq+8,'P','n');
						moves.emplace_back(sq,sq+8,'P','r');
						moves.emplace_back(sq,sq+8,'P','b');
					}
				} else {
					moves.emplace_back(sq,sq+8);
				}
			}
			//capture
			if(sq % 8 != 0 && this->board[sq+7] < 91 && this->board[sq+7] != ' '){
				if(sq >= 48 && sq <= 55){//OPP: check most limiting condition first
					moves.emplace_back(sq,sq+7,'P','q');
					if(flag != 'O'){
						moves.emplace_back(sq,sq+7,'P','n');
						moves.emplace_back(sq,sq+7,'P','r');
						moves.emplace_back(sq,sq+7,'P','b');
					}
				} else {
					moves.emplace_back(sq,sq+7);
				}
			}
			if(sq % 8 != 7 && this->board[sq+9] < 91 && this->board[sq+9] != ' '){
				if(sq >= 48 && sq <= 55){//OPP: check most limiting condition first
					moves.emplace_back(sq,sq+9,'P','q');
					if(flag != 'O'){
						moves.emplace_back(sq,sq+9,'P','n');
						moves.emplace_back(sq,sq+9,'P','r');
						moves.emplace_back(sq,sq+9,'P','b');
					}
				} else {
					moves.emplace_back(sq,sq+9);
				}
			}
			//take via en-passaunt
			if((sq % 8 != 0 && this->en_pass_index == sq+7 ) || (sq % 8 != 7 && this->en_pass_index == sq+9 )){
				moves.emplace_back(sq,this->en_pass_index,'E');
			}
			//first move
			if(sq >= 8 && sq <= 15 && this->board[sq+8] == ' ' && this->board[sq+16] == ' '){
				//flag for possible en passuant if it is a thing
				//(dosen't check for edge wrapping as that is done taking side)
				if((this->board[sq+15] == 'P') || (this->board[sq+17] == 'P')){
					moves.emplace_back(sq,sq+16,'e');
				} else {
					moves.emplace_back(sq,sq+16);
				}
			}
			break;
		case 'R':
		case 'r':
			this->applyOffset(moves,sq,-8,-1, 0,isWhite);
			this->applyOffset(moves,sq,-1, 0,-1,isWhite);
			this->applyOffset(moves,sq, 1, 0, 1,isWhite);
			this->applyOffset(moves,sq, 8, 1, 0,isWhite);
			break;
		case 'B':
		case 'b':
			this->applyOffset(moves,sq,-9,-1,-1,isWhite);
			this->applyOffset(moves,sq,-7,-1, 1,isWhite);
			this->applyOffset(moves,sq, 7, 1,-1,isWhite);
			this->applyOffset(moves,sq, 9, 1, 1,isWhite);
			break;
		case 'Q':
		case 'q':
			this->applyOffset(moves,sq,-8,-1, 0,isWhite);
			this->applyOffset(moves,sq,-1, 0,-1,isWhite);
			this->applyOffset(moves,sq, 1, 0, 1,isWhite);
			this->applyOffset(moves,sq, 8, 1, 0,isWhite);
			this->applyOffset(moves,sq,-9,-1,-1,isWhite);
			this->applyOffset(moves,sq,-7,-1, 1,isWhite);
			this->applyOffset(moves,sq, 7, 1,-1,isWhite);
			this->applyOffset(moves,sq, 9, 1, 1,isWhite);
			break;
		case 'K':
		case 'k':
			this->applyOffset(moves,sq,-8,-1, 0,isWhite,1);
			this->applyOffset(moves,sq,-1, 0,-1,isWhite,1);
			this->applyOffset(moves,sq, 1, 0, 1,isWhite,1);
			this->applyOffset(moves,sq, 8, 1, 0,isWhite,1);
			this->applyOffset(moves,sq,-9,-1,-1,isWhite,1);
			this->applyOffset(moves,sq,-7,-1, 1,isWhite,1);
			this->applyOffset(moves,sq, 7, 1,-1,isWhite,1);
			this->applyOffset(moves,sq, 9, 1, 1,isWhite,1);
			//castling
			if(piece == 'K'){
				if(this->wcq && this->board[57] == ' ' && 
				   this->board[58] == ' ' && this->board[59] == ' ' && this->board[56] == 'R' &&
				   !isSquareCheck(59,1) && !isSquareCheck(60,1)
				   ){
					moves.emplace_back(60,58,'C');
				}
				if(this->wck && this->board[61] == ' ' && 
				   this->board[62] == ' ' && this->board[63] == 'R' && !isSquareCheck(61,1)  && !isSquareCheck(60,1)
				   ){
					moves.emplace_back(60,62,'C');
				}
			} else {
				if(this->bcq && this->board[1] == ' ' && 
				   this->board[2] == ' '  && this->board[3] == ' ' && this->board[0] == 'r' &&
				   !isSquareCheck(3,0) && !isSquareCheck(4,0)
				   ){
					moves.emplace_back(4,2,'C');
				}
				if(this->bck && this->board[5] == ' ' && 
				   this->board[6] == ' '  && this->board[7] == 'r' && !isSquareCheck(5,0) && !isSquareCheck(4,0)
				   ){
					moves.emplace_back(4,6,'C');
				}
			}
			break;
		case 'N':
		case 'n':
			this->applyOffset(moves,sq,-17,-2,-1,isWhite,1);
			this->applyOffset(moves,sq,-15,-2, 1,isWhite,1);
			this->applyOffset(moves,sq,-10,-1,-2,isWhite,1);
			this->applyOffset(moves,sq,-6 ,-1, 2,isWhite,1);
			this->applyOffset(moves,sq, 6 , 1,-2,isWhite,1);
			this->applyOffset(moves,sq, 10, 1, 2,isWhite,1);
			this->applyOffset(moves,sq, 15, 2,-1,isWhite,1);
			this->applyOffset(moves,sq, 17, 2, 1,isWhite,1);
			break;
	}
}

void ChessBoard::getAllSideMoves(std::vector<SingleMove>& moves, char isWhite){
	this->getAllSideMoves(moves,isWhite,'N');
}
/*
 * Generate all moves for a given side
 */
void ChessBoard::getAllSideMoves(std::vector<SingleMove>& moves, char isWhite, char flag){
	if(isWhite){
		int* sip = whiteIndexs;
		for(int i = 0; i < whitePcCount; sip++,i++){
			this->addSquareMoves(moves,*sip,flag);
		}
	} else {
		int* sip = blackIndexs;
		for(int i = 0; i < blackPcCount; sip++,i++){
			this->addSquareMoves(moves,*sip,flag);
		}
	}
}

/*
 * Very efficently work out if a square would be check for the king of the specified colour
 */
char ChessBoard::isSquareCheck(char sq, char forWhite){
	int p;
	char val;
	if(forWhite){
		//diagonals:
		for(p = sq+9; p <= 63 && p % 8 != 0; p += 9){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'q' || val == 'b'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq+7; p <= 63 && p % 8 != 7; p += 7){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'q' || val == 'b'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq-7; p >= 0 && p % 8 != 0; p -= 7){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'q' || val == 'b'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq-9; p >= 0 && p % 8 != 7; p -= 9){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'q' || val == 'b'){
				return 1;
			} else {
				break;
			}
		}
		//straights:
		for(p = sq+8; p <= 63; p += 8){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'q' || val == 'r'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq+1; p % 8 != 0; p += 1){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'q' || val == 'r'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq-1; p % 8 != 7; p -= 1){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'q' || val == 'r'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq-8; p >= 0; p -= 8){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'q' || val == 'r'){
				return 1;
			} else {
				break;
			}
		}
		//knight
		if(sq-17 >= 0){
			if( (sq % 8 >= 1 && sq / 8 >= 2 && this->board[sq-17] == 'n') || 
			    (sq % 8 <= 6 && sq / 8 >= 2 && this->board[sq-15] == 'n') ||
				(sq % 8 >= 2 && sq / 8 >= 1 && this->board[sq-10] == 'n') ||
				(sq % 8 <= 5 && sq / 8 >= 1 && this->board[sq-6] == 'n')){
				return 1;
			}
		} else {
			if( (sq-15 >= 0 && sq % 8 <= 6 && sq / 8 >= 2 && this->board[sq-15] == 'n') ||
				(sq-10 >= 0 && sq % 8 >= 2 && sq / 8 >= 1 && this->board[sq-10] == 'n') ||
				(sq-6  >= 0 && sq % 8 <= 5 && sq / 8 >= 1 && this->board[sq-6] == 'n')){
				return 1;
			}
		}
		if(sq+17 <= 63){
			if( (sq % 8 <= 6 && sq / 8 <= 5 && this->board[sq+17] == 'n') || 
				(sq % 8 >= 1 && sq / 8 <= 5 && this->board[sq+15] == 'n') ||
				(sq % 8 <= 5 && sq / 8 <= 6 && this->board[sq+10] == 'n') ||
				(sq % 8 >= 2 && sq / 8 <= 6 && this->board[sq+6] == 'n')){
				return 1;
			}
		} else {
			if ((sq+15 <= 63 && sq % 8 >= 1 && sq / 8 <= 5 && this->board[sq+15] == 'n') ||
				(sq+10 <= 63 && sq % 8 <= 5 && sq / 8 <= 6 && this->board[sq+10] == 'n') ||
				(sq+6  <= 63 && sq % 8 >= 2 && sq / 8 <= 6 && this->board[sq+6] == 'n')){
				return 1;
			}
		}
		//king & pawn
		if(
			(sq-9 >= 0  && sq / 8 != 0 && sq % 8 != 0 && (this->board[sq-9] == 'k' || this->board[sq-9] == 'p')) ||
			(sq-8 >= 0  && sq / 8 != 0 &&                 this->board[sq-8] == 'k'                             ) ||
			(sq-7 >= 0  && sq / 8 != 0 && sq % 8 != 7 && (this->board[sq-7] == 'k' || this->board[sq-7] == 'p')) ||
			(sq-1 >= 0                 && sq % 8 != 0 &&  this->board[sq-1] == 'k'                             ) ||
			(sq+1 <= 63                && sq % 8 != 7 &&  this->board[sq+1] == 'k'                             ) ||
			(sq+7 <= 63 && sq / 8 != 7 && sq % 8 != 0 &&  this->board[sq+7] == 'k'                             ) ||
			(sq+8 <= 63 && sq / 8 != 7 &&                 this->board[sq+8] == 'k'                             ) ||
			(sq+9 <= 63 && sq / 8 != 7 && sq % 8 != 7 &&  this->board[sq+9] == 'k'                             )
			){
			return 1;
		}
	} else {
		//diagonals:
		for(p = sq+9; p <= 63 && p % 8 != 0; p += 9){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'Q' || val == 'B'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq+7; p <= 63 && p % 8 != 7; p += 7){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'Q' || val == 'B'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq-7; p >= 0 && p % 8 != 0; p -= 7){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'Q' || val == 'B'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq-9; p >= 0 && p % 8 != 7; p -= 9){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'Q' || val == 'B'){
				return 1;
			} else {
				break;
			}
		}
		//straights:
		for(p = sq+8; p <= 63; p += 8){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'Q' || val == 'R'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq+1; p % 8 != 0; p += 1){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'Q' || val == 'R'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq-1; p % 8 != 7; p -= 1){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'Q' || val == 'R'){
				return 1;
			} else {
				break;
			}
		}
		for(p = sq-8; p >= 0; p -= 8){
			val = this->board[p];
			if(val == ' '){
				continue;
			} else if (val == 'Q' || val == 'R'){
				return 1;
			} else {
				break;
			}
		}
		//knight
		if(sq-17 >= 0){
			if ((sq % 8 >= 1 && sq / 8 >= 2 && this->board[sq-17] == 'N') || 
				(sq % 8 <= 6 && sq / 8 >= 2 && this->board[sq-15] == 'N') ||
				(sq % 8 >= 2 && sq / 8 >= 1 && this->board[sq-10] == 'N') ||
				(sq % 8 <= 5 && sq / 8 >= 1 && this->board[sq-6] == 'N')){
				return 1;
			}
		} else {
			if ((sq-15 >= 0 && sq % 8 <= 6 && sq / 8 >= 2 && this->board[sq-15] == 'N') ||
				(sq-10 >= 0 && sq % 8 >= 2 && sq / 8 >= 1 && this->board[sq-10] == 'N') ||
				(sq-6  >= 0 && sq % 8 <= 5 && sq / 8 >= 1 && this->board[sq-6] == 'N')){
				return 1;
			}
		}
		if(sq+17 <= 63){
			if ((sq % 8 <= 6 && sq / 8 <= 5 && this->board[sq+17] == 'N') || 
				(sq % 8 >= 1 && sq / 8 <= 5 && this->board[sq+15] == 'N') ||
				(sq % 8 <= 5 && sq / 8 <= 6 && this->board[sq+10] == 'N') ||
				(sq % 8 >= 2 && sq / 8 <= 6 && this->board[sq+6] == 'N')){
				return 1;
			}
		} else {
			if ((sq+15 <= 63 && sq % 8 >= 1 && sq / 8 <= 5 && this->board[sq+15] == 'N') ||
				(sq+10 <= 63 && sq % 8 <= 5 && sq / 8 <= 6 && this->board[sq+10] == 'N') ||
				(sq+6  <= 63 && sq % 8 >= 2 && sq / 8 <= 6 && this->board[sq+6] == 'N')){
				return 1;
			}
		}
		//king & pawn
		if(
			(sq-9 >= 0  && sq / 8 != 0 && sq % 8 != 0 &&  this->board[sq-9] == 'K'                             ) ||
			(sq-8 >= 0  && sq / 8 != 0 &&                 this->board[sq-8] == 'K'                             ) ||
			(sq-7 >= 0  && sq / 8 != 0 && sq % 8 != 7 &&  this->board[sq-7] == 'K'                             ) ||
			(sq-1 >= 0                 && sq % 8 != 0 &&  this->board[sq-1] == 'K'                             ) ||
			(sq+1 <= 63                && sq % 8 != 7 &&  this->board[sq+1] == 'K'                             ) ||
			(sq+7 <= 63 && sq / 8 != 7 && sq % 8 != 0 && (this->board[sq+7] == 'K' || this->board[sq+7] == 'P')) ||
			(sq+8 <= 63 && sq / 8 != 7 &&                 this->board[sq+8] == 'K'                             ) ||
			(sq+9 <= 63 && sq / 8 != 7 && sq % 8 != 7 && (this->board[sq+9] == 'K' || this->board[sq+9] == 'P'))
			){
			return 1;
		}
	}
	return 0;
}


/* ------ User evaluation ------ */

/**
 * Filter a vector of moves such that only valid moves are allowed
 */
void ChessBoard::trueValidMoves(std::vector<SingleMove>& moves, char isWhite){
	//filter the given list of moves to only the valid ones
	ChessBoard consideration = ChessBoard();
	for(int i = 0; i < moves.size(); i++){
		consideration.cloneBoard(*this);
		consideration.performMove(moves[i]);
		//due to opperator short circuiting this is a very quick opperation
		if  (( isWhite && consideration.isSquareCheck(consideration.whiteKingLoc,1/*white*/)) ||
			 (!isWhite && consideration.isSquareCheck(consideration.blackKingLoc,0/*black*/))
		    ){
			moves.erase(moves.begin()+i);
			i--;//as the list is now shorter
		}
	}
}

/*
 * Work out if a board is checkmate-ish
 */
char ChessBoard::isCheckMate(char isWhite){
	vector<SingleMove> PossibleMoves;
	PossibleMoves.reserve(45);
	this->getAllSideMoves(PossibleMoves, isWhite);
	this->trueValidMoves(PossibleMoves, isWhite);
	return (int)(PossibleMoves.size() == 0);
}

/*
 * Work out if a board is drawn due to insefficent materials
 */
char ChessBoard::isDrawn(){
	//as a game cannnot be drawn with rooks or queens or pawns on the board this 
	// will return on encountering them rather than tally them up
	int Wbishops = 0;
	int Wknights = 0;
	
	int Bbishops = 0;
	int Bknights = 0;
	
	char piece;
	int* sip = whiteIndexs;
	for(int i = 0; i < whitePcCount; sip++,i++){
		piece = this->board[*sip];
		switch(piece){
			case 'P':
				return 0;
			case 'Q':
				return 0;
			case 'R':
				return 0;
			case 'B':
				Wbishops += 1;
				break;
			case 'N':
				Wknights += 1;
				break;
		}
	}
	
	sip = blackIndexs;
	for(int i = 0; i < blackPcCount; sip++,i++){
		piece = this->board[*sip];
		switch(piece){
			case 'p':
				return 0;
			case 'q':
				return 0;
			case 'r':
				return 0;
			case 'b':
				Bbishops += 1;
				break;
			case 'n':
				Bknights += 1;
				break;
		}
	}
	
	//It is always drawn at this point if there are no knights and neigther side 2+ bishops
	if(!Wknights && !Bknights && Wbishops <= 1 && Bbishops <= 1){
		return 1;
	}
	
	//white has just a king and black has just a king and 1 or 2 knights
	if(!Wknights && !Wbishops && Bknights <= 2 && !Bbishops){
		return 1;
	}
	
	//black has just a king and white has just a king and 1 or 2 knights
	if(!Bknights && !Bbishops && Wknights <= 2 && !Wbishops){
		return 1;
	}
	
	return 0;
}

/*
 * Generates and returns a user readable summary of the taken pieces
 */
std::string ChessBoard::getSideRemainingPieces(char forWhite){
	//init with expected values
	int queens  = 1;
	int rooks   = 2;
	int bishops = 2;
	int knights = 2;
	int pawns   = 8;
	
	//remove 1 from each when piece is found (as it is not taken)
	char piece;
	if(forWhite){
		int* sip = whiteIndexs;
		for(int i = 0; i < whitePcCount; sip++,i++){
			piece = this->board[*sip];
			switch(piece){
				case 'P':
					pawns -= 1;
					break;
				case 'Q':
					queens -= 1;
					break;
				case 'R':
					rooks -= 1;
					break;
				case 'B':
					bishops -= 1;
					break;
				case 'N':
					knights -= 1;
					break;
			}
		}
	} else {
		int* sip = blackIndexs;
		for(int i = 0; i < blackPcCount; sip++,i++){
			piece = this->board[*sip];
			switch(piece){
				case 'p':
					pawns -= 1;
					break;
				case 'q':
					queens -= 1;
					break;
				case 'r':
					rooks -= 1;
					break;
				case 'b':
					bishops -= 1;
					break;
				case 'n':
					knights -= 1;
					break;
				
			}
		}
	}
	
	//generate return string
	queens  = max(queens ,0);
	rooks   = max(rooks  ,0);
	bishops = max(bishops,0);
	knights = max(knights,0);
	pawns   = max(pawns  ,0);
	
	string out = "";
	
	if(queens == 1){
		out += 'q';
	}
	if(rooks == 2){
		out += 'r';
		out += 'r';
	}
	if(rooks == 1){
		out += 'r';
	}
	if(bishops == 2){
		out += 'b';
		out += 'b';
	}
	if(bishops == 1){
		out += 'b';
	}
	if(knights == 2){
		out += 'n';
		out += 'n';
	}
	if(knights == 1){
		out += 'n';
	}
	for(int i = 0; i < pawns; i++){
		out += 'p';
	}
	
	if(forWhite){
		std::transform(out.begin(), out.end(),out.begin(), ::toupper);
	}
	return out;
}

/*------ TTabling ------*/
/*
 * get each pieces nubmer for zobrist hashing
 */
int ChessBoard::getZhashpcIndex(char pc){
	if(pc < 91){//white
		if(pc == 'P'){
			return 0;
		}
		if(pc >80){
			if(pc == 'R'){
				return 6;
			} else {
				return 8;
			}
		} else {
			if(pc == 'B'){
				return 4;
			} else if (pc == 'N'){
				return 2;
			} else {//w king
				return 10;
			}
		}
	} else {//black
		if(pc == 'p'){
			return 1;
		}
		if(pc > 112){
			if(pc == 'r'){
				return 7;
			} else {
				return 9;
			}
		} else {
			if(pc == 'b'){
				return 5;
			} else if (pc == 'n'){
				return 3;
			} else {//b king
				return 11;
			}
		}
	}
}

/*
 * Fully recalculate the zobrist hash for a board
 *
 * this is called outside the recursive function and thus can run slowly without concern
 */
void ChessBoard::recalculateZhash(char isWhiteToMove){
	char pc;
	int pcn;
	this->zhash = 0;
	for(int i = 0; i < 64; i++){
		pc = this->board[i];
		if(pc == ' '){
			continue;
		}
		pcn = getZhashpcIndex(pc);
		//bitwise XOR ing
		this->zhash = this->zhash ^ zhashnums[(12*i)+pcn];
	}
	/*
	 peices:
	 		0 1 2 3 4 5 6 7 8 9 10 11
	 		P p N n B b R r Q q K  k
	 		
	 		0-767: board (piece num * (board index+1))
	 		768:   WhiteToMove
	 		769:   CastleWhiteRight
	 		770:   CastleWhiteLeft
	 		771:   CastleBlackRight
	 		772:   CastleBlackLeft
	 		773:   EnPass A
	 		774:   EnPass B
	 		775:   EnPass C
	 		776:   EnPass D
	 		777:   EnPass E
	 		778:   EnPass F
	 		779:   EnPass G
	 		780:   EnPass H
	*/
	
	if(isWhiteToMove){
		this->zhash = this->zhash ^ zhashnums[768];
	}
	if(this->wck){
		this->zhash = this->zhash ^ zhashnums[769];
	}
	if(this->wcq){
		this->zhash = this->zhash ^ zhashnums[770];
	}
	if(this->bck){
		this->zhash = this->zhash ^ zhashnums[771];
	}
	if(this->bcq){
		this->zhash = this->zhash ^ zhashnums[772];
	}
	if(this->en_pass_index != -1){
		this->zhash = this->zhash ^ zhashnums[773+(this->en_pass_index % 8)];
	}
}

/*
 * Update the hash for a given move (much faster than recalculating)
 *
 * Must call ***before*** performing move to keep hash consistent
 */
void ChessBoard::updateZhashForMove(SingleMove& move){
	//turn:
	this->zhash = this->zhash ^ zhashnums[768];
	//en_pass_old&offered
	if(this->en_pass_index != -1){//undoes the last en-pass
		this->zhash = this->zhash ^ zhashnums[773+(this->en_pass_index % 8)];
	}
	if(move.extra == 'e'){
		this->zhash = this->zhash ^ zhashnums[773+(move.source_tile % 8)];
	}
	//board (main move)
	char spcn = getZhashpcIndex(this->board[move.source_tile]);
	char dpcn = getZhashpcIndex(this->board[move.dest_tile]);
	
	this->zhash = this->zhash ^ zhashnums[(12*move.source_tile)+spcn];//remove source piece
	if(this->board[move.dest_tile] != ' '){//remove dest piece
		this->zhash = this->zhash ^ zhashnums[(12*move.dest_tile)+dpcn];
	}
	this->zhash = this->zhash ^ zhashnums[(12*move.dest_tile)+spcn];//add source piece
	
	//castle flags
	/*
		 	769:   CastleWhiteRight
	 		770:   CastleWhiteLeft
	 		771:   CastleBlackRight
	 		772:   CastleBlackLeft
	*/
	switch(move.source_tile){
		case 0:
			if(this->bcq == 0){
				this->zhash = this->zhash ^ zhashnums[772];
			}
			break;
		case 4:
			if(this->bcq == 0){
				this->zhash = this->zhash ^ zhashnums[772];
			}
			if(this->bck == 0){
				this->zhash = this->zhash ^ zhashnums[771];
			}
			break;
		case 7:
			if(this->bck == 0){
				this->zhash = this->zhash ^ zhashnums[771];
			}
			break;
		case 56:
			if(this->wcq == 0){
				this->zhash = this->zhash ^ zhashnums[770];
			}
			break;
		case 60:
			if(this->wcq == 0){
				this->zhash = this->zhash ^ zhashnums[770];
			}
			if(this->wck == 0){
				this->zhash = this->zhash ^ zhashnums[769];
			}
			break;
		case 63:
			if(this->wck == 0){
				this->zhash = this->zhash ^ zhashnums[769];
			}
			break;
	}
	
	//en_pass_taken
	if(move.extra == 'E'){
		if(move.dest_tile > 32){
			this->zhash = this->zhash ^ zhashnums[(12*(move.dest_tile-8))+0];
		} else {
			this->zhash = this->zhash ^ zhashnums[(12*(move.dest_tile+8))+1];
		}
	}
	
	//Promotion
	if(move.extra == 'P'){
		if(move.dest_tile > 32){
			this->zhash = this->zhash ^ zhashnums[(12*move.dest_tile)+1];//remove black pawn
			this->zhash = this->zhash ^ zhashnums[(12*move.dest_tile)+9];//replace with black queen
		} else {
			this->zhash = this->zhash ^ zhashnums[(12*move.dest_tile)+0];//remove white pawn
			this->zhash = this->zhash ^ zhashnums[(12*move.dest_tile)+8];//replace with white queen
		}
	}
	
	//castle moves
	if(move.extra == 'P'){
		if(move.dest_tile == 6){
			this->zhash = this->zhash ^ zhashnums[(12*7)+7];
			this->zhash = this->zhash ^ zhashnums[(12*5)+7];
		} else if(move.dest_tile == 2){
			this->zhash = this->zhash ^ zhashnums[(12*0)+7];
			this->zhash = this->zhash ^ zhashnums[(12*3)+7];
		} else if(move.dest_tile == 58){
			this->zhash = this->zhash ^ zhashnums[(12*56)+6];
			this->zhash = this->zhash ^ zhashnums[(12*59)+6];
		} else {
			this->zhash = this->zhash ^ zhashnums[(12*63)+6];
			this->zhash = this->zhash ^ zhashnums[(12*61)+6];
		}
	}
}





/*------ IO ------*/
void ChessBoard::show(){
	this->show('N',-1,0);
}
void ChessBoard::show(char flag){
	this->show(flag,-1,0);
}
void ChessBoard::show(char flag, int moveNum){
	this->show(flag,moveNum,0);
}

/*
 * Show the chess board to the user.
 * Arguments:
 *  flag: N = normal, # = index numbers, C = continus/rolling display
 */
void ChessBoard::show(char flag, int moveNum, char flipBlack){
	cout << "\033[1;37;40m\n\n   +---+---+---+---+---+---+---+---+";
	char letter;
	for(int row = (0+(flipBlack*7)); ((!flipBlack && row < 8) || (flipBlack && row >= 0)); row += (1-(2*flipBlack))){
		cout << "\n " << (8-row) << " ";
		for(int col = 0; col < 8; col++){
			if(flag == 'N' || flag == 'C'){
				letter = this->board[row*8+col];
				if( (letter == 'K' && this->isSquareCheck(row*8+col,1)) || 
				    (letter == 'k' && this->isSquareCheck(row*8+col,0))){
				    cout << "| \033[1;31m" << letter << "\033[1;37;40m ";
				}else if(letter == 32){
					cout << "| " << letter << ' ';
				}else if(letter < 91){//if white
					cout << "| \033[1;33m" << letter << "\033[1;37;40m ";
				} else {//else black
					cout << "| \033[1;34m" << letter << "\033[1;37;40m ";
				}
			} else if(flag == '#'){
				int num = row*8+col;
				if(num<10){
					cout << "| " << num << ' ';
				} else {
					cout << "| " << num;
				}
			} else {
				cout << "| ? ";
			}
			
		}
		
		string bp = this->getSideRemainingPieces(0);
		string wp = this->getSideRemainingPieces(1);
		pair<int,int> valpair = this->getPointsOnBoard();
		int val = valpair.first-valpair.second;
		
		if(row == 0){
			cout << "|  \033[1;34mBlack (" << showpos << -val << noshowpos 
			     <<")\033[1;37;40m\n   +---+---+---+---+---+---+---+---+   \033[1;33m" 
			     << wp << "\033[1;37;40m";
		} else if (row == 7) {
			cout << "|  \033[1;33mWhite (" << showpos << val << noshowpos 
			     <<")\033[1;37;40m\n   +---+---+---+---+---+---+---+---+   \033[1;34m" 
			     << bp << "\033[1;37;40m";
		} else if (moveNum != -1 && row == (3+flipBlack)){
			cout << "|\n   +---+---+---+---+---+---+---+---+  Move: " << moveNum;
		}else {
			cout << "|\n   +---+---+---+---+---+---+---+---+";
		}
	}
	cout << "\n     A   B   C   D   E   F   G   H  \n";
	if(flag != 'C'){
		cout << "\033[0m" << endl;
	}
}

/*
 * Outputs flags and speedup data (for debugging)
 */
void ChessBoard::flags(){
	cout << "Flags:" << "EPI:" << this->en_pass_index
	     << "| K: " << this->wck
	     << "| Q: " << this->wcq
	     << "| k: " << this->bck
	     << "| q: " << this->bcq
	     << "| KT: " << (int)this->whiteKingLoc
	     << "| kt: " << (int)this->blackKingLoc
	     << endl << "White loc (" << (int)this->whitePcCount << ") : ";
	for(int i = 0; i < this->whitePcCount; i++){
		if(i != 0){
			cout << ", ";
		}
		cout << whiteIndexs[i];
	}
	cout << endl << "Black loc (" << (int)this->blackPcCount << ") : ";
	for(int i = 0; i < this->blackPcCount; i++){
		if(i != 0){
			cout << ", ";
		}
		cout << blackIndexs[i];
	}
	cout << endl;
}

SingleMove* ChessBoard::parseRequest(string uin, char isWhite){
	return this->parseRequest(uin, isWhite, -1);
}

/*
 * Converts a user move description to a SingleMove
 */
SingleMove* ChessBoard::parseRequest(string uin, char isWhite, char activeSquare){

	//extra debug bonus actions
	if(uin.size() == 1 && uin[0] == '#'){//UTIL: print array indexs
		this->show('#');
		throw 'U';
	} else if (uin.size() == 2 && uin[0] == '!'){//CHEAT: skip turn:
		throw 'S';
	} else if (uin.size() == 4 && uin[0] == '!'){//CHEAT: set piece for testing:
		transform(uin.begin(), uin.end()-1, uin.begin(), ::toupper);
		if(uin[3] == '-'){
			this->setSquare(((56-uin[2])*8)+uin[1]-65,' ');
		} else {
			this->setSquare(((56-uin[2])*8)+uin[1]-65,uin[3]);
		}
		throw '!';
	} 
	
	transform(uin.begin(), uin.end(), uin.begin(), ::toupper);
	
	int source = -1;
	int dest = -1;
	char promo = ('q'-(32*isWhite));//correct default promotion
	
	if(uin.size() == 6 && uin[2] == '-' && uin[3] == '>'){//sq to sq
		source = ((56-uin[1])*8)+uin[0]-65;
		dest = ((56-uin[5])*8)+uin[4]-65;
	} else if(uin.size() == 8 && uin[2] == '-' && uin[3] == '>' && uin[6] == '='){//sq to sq with promo
		source = ((56-uin[1])*8)+uin[0]-65;
		dest = ((56-uin[5])*8)+uin[4]-65;
		promo = (uin[7]+(32*(1-isWhite)));
	} else if(uin.size() == 4 && uin[0] <= 72 && uin[0] >= 65 && uin[2] <= 72 && uin[2] >= 65 &&
			  uin[1] <= 56 && uin[1] >= 49 && uin[3] <= 56 && uin[3] >= 49){//sq to sq shorthand
		source = ((56-uin[1])*8)+uin[0]-65;
		dest = ((56-uin[3])*8)+uin[2]-65;
	} else if(uin.size() == 5 && uin[0] <= 72 && uin[0] >= 65 && uin[2] <= 72 && uin[2] >= 65 &&
			  uin[1] <= 56 && uin[1] >= 49 && uin[3] <= 56 && uin[3] >= 49 &&
			  (uin[4] == 'Q' || uin[4] == 'N' || uin[4] == 'B' || uin[4] == 'R')){//sq to sq with promo shorthand
		source = ((56-uin[1])*8)+uin[0]-65;
		dest = ((56-uin[3])*8)+uin[2]-65;
		promo = (uin[4]+(32*(1-isWhite)));
	} else if(uin == "0-0" || uin == "O-O"){//castling
		if(isWhite){
			source = 60;
			dest = 62;
		} else {
			source = 4;
			dest = 6;
		}
	} else if(uin == "0-0-0" || uin == "O-O-O"){//castling
		if(isWhite){
			source = 60;
			dest = 58;
		} else {
			source = 4;
			dest = 2;
		}
	} else if(uin.size() >= 1){//algebraic chess notation parsing:
		//when the last letter is a 'takes' instruction, autofill as 'take the active square'
		if(uin[uin.size()-1] == 'X'){
			uin = uin.substr(0,uin.size()-1)+(char)(65+(activeSquare % 8))+(char)(56-(activeSquare / 8));
		}
		
		//clean the string:
		uin.erase(remove(uin.begin(), uin.end(), 'X'), uin.end());
		uin.erase(remove(uin.begin(), uin.end(), '+'), uin.end());
		uin.erase(remove(uin.begin(), uin.end(), '#'), uin.end());
		if(*(uin.end()-2) == '=' || *(uin.end()-2) == ':'){//(parses and removes any trailing promotion instruction)
			promo = (*(uin.end()-1)+(32*(1-isWhite)));
			uin = uin.substr(0,uin.size()-2);
		}
		
		if(uin.size() < 2){
			throw 'u';//unknown move structure (after cleaning)
		}
		
		
		
		//size 2 codes at this point allways reffer to pawns
		if(uin.size() == 2){
			uin = "P"+uin;
		}
		
		//get specified moving piece
		char movePiece = uin[0];
		if(movePiece != 'P' && movePiece != 'R' && movePiece != 'N' && 
		   movePiece != 'B' && movePiece != 'Q' && movePiece != 'K'    ){
			throw 'i';//invalid char encountered
		}
		if(!isWhite){//correct for side
			movePiece += 32;
		}
		
		
		if(uin.size() == 5){//unambiguous move
			source = ((56-uin[2])*8)+uin[1]-65;
			dest = ((56-uin[4])*8)+uin[3]-65;
			if(movePiece != this->board[source]){
				throw 'A';//assertion: moving piece does not match reality
			}
		} else if(uin.size() == 4){//part-ambiguous move
			//generate all moves this might be
			vector<SingleMove> CandidateMoves;
			CandidateMoves.reserve(45);
			this->getAllSideMoves(CandidateMoves,isWhite);
			this->trueValidMoves(CandidateMoves,isWhite);
			
			char reqnum;//The requirement (placed by the extra char) is a numerical one (not a char)
			char numreq;//The parsed requriement
			if(uin[1] < 58 && uin[1] > 48){
				reqnum = 1;
				numreq = 56-uin[1];
			} else if (uin[1] < 73 && uin[1] > 64){
				reqnum = 0;
				numreq = uin[1]-65;
			} else {
				throw 'i';//invalid char encountered
			}
			
			//search for the move making flaging the index when it is found and
			//retruning ambiguity error if a second valid move is found
			dest = ((56-uin[3])*8)+uin[2]-65;
			int validIndex = -1;
			for(int i = 0; i < CandidateMoves.size(); i++){
				//OLD:cout << "::2::" << CandidateMoves[i] << ':' << (int)(CandidateMoves[i].dest_tile == dest) << ' ' << (int)(this->board[CandidateMoves[i].source_tile] == movePiece) << ' ' << (int)(( reqnum && (CandidateMoves[i].source_tile / 8 == numreq))) << ' ' << (int)((!reqnum && (CandidateMoves[i].source_tile % 8 == numreq))) << ' ' << endl;
				if(CandidateMoves[i].dest_tile == dest && 
				   this->board[CandidateMoves[i].source_tile] == movePiece &&
				     (
				   	   ( reqnum && (CandidateMoves[i].source_tile / 8 == numreq)) ||
				   	   (!reqnum && (CandidateMoves[i].source_tile % 8 == numreq))
				     ) && 	
				     (
				       CandidateMoves[i].promo == ' ' || 
				       CandidateMoves[i].promo == 'Q' || 
				       CandidateMoves[i].promo == 'q'
				     )
				   ){
					if(validIndex == -1){
						validIndex = i;
					} else {
						throw '~';
					}
				}
			}
			
			if (validIndex == -1){
				throw 'N';
			}
			
			source = CandidateMoves[validIndex].source_tile;
			
		} else if(uin.size() == 3){//fully-ambiguous move
			//generate all moves this might be
			vector<SingleMove> CandidateMoves;
			CandidateMoves.reserve(45);
			this->getAllSideMoves(CandidateMoves,isWhite);
			this->trueValidMoves(CandidateMoves,isWhite);
			
			//search for the move making flaging the index when it is found and
			//retruning ambiguity error if a second valid move is found
			dest = ((56-uin[2])*8)+uin[1]-65;
			int validIndex = -1;
			for(int i = 0; i < CandidateMoves.size(); i++){
				if(CandidateMoves[i].dest_tile == dest && this->board[CandidateMoves[i].source_tile] == movePiece && 	
				    (
				      CandidateMoves[i].promo == ' ' || 
				      CandidateMoves[i].promo == 'Q' || 
				      CandidateMoves[i].promo == 'q'
				    )
				  ){
					if(validIndex == -1){
						validIndex = i;
					} else {
						throw '~';
					}
				}
			}
			
			if (validIndex == -1){
				throw 'N';
			}
			
			source = CandidateMoves[validIndex].source_tile;
			
		} else {
			throw 'u';//unknown move structure (after cleaning)
		}
		
	} else {
		throw 'u';//unknown move structure
	}
	
	//check source piece is correct color
	if((isWhite && this->board[source] > 91) || (!isWhite && this->board[source] < 91)){
		throw 't';//wrong colour (for turn)
	}
	
	
	//match move to possiblitys:
	vector<SingleMove> PossibleMoves;
	PossibleMoves.reserve(45);
	
	//generate all possible moves for the given source square
	this->addSquareMoves(PossibleMoves,source);
	if(moveInVector(PossibleMoves,source,dest) == -1){
		throw 'm';//move impossible
	}
	
	//filter the list to only the possible moves
	this->trueValidMoves(PossibleMoves,isWhite);
	int moveIndex = moveInVector(PossibleMoves,source,dest,promo);
	
	if(moveIndex == -1){
		throw 'c';//check prevents this
	}
	
	//move is possible so return permenate version of it
	return new SingleMove(PossibleMoves[moveIndex]);
}


/*------ game commands ------ */

/*
 * Initialise gaem to start position
 */
void ChessBoard::setupGame(){
	this->reset();
	this->en_pass_index = -1;
	this->wck = 1;
	this->wcq = 1;
	this->bck = 1;
	this->bcq = 1;
}

/*
 * Do the specified move settings flags
 */
void ChessBoard::performMove(SingleMove& move){
	this->blindMove(move);
	//flag castle restricitons with board
	switch(move.source_tile){
		case 0:
			this->bcq = 0;
			break;
		case 4:
			this->bck = 0;
			this->bcq = 0;
			break;
		case 7:
			this->bck = 0;
			break;
		case 56:
			this->wcq = 0;
			break;
		case 60:
			this->wck = 0;
			this->wcq = 0;
			break;
		case 63:
			this->wck = 0;
			break;
	}
	
	//clear any old en passaunt flags: (as the moves have allreddy been made in their knowlage this is safe)
	this->en_pass_index = -1;
	
	//deal with extras
	if(move.extra != ' '){
		switch(move.extra){
			case 'e':
				this->en_pass_index = ((move.source_tile + move.dest_tile)/2);
				break;
			case 'E':
				if(move.dest_tile > 32){
					removePiece(move.dest_tile-8,1);
				} else {
					removePiece(move.dest_tile+8,0);
				}
				break;
			case 'P':
				//promote to requested piece
				setSquare(move.dest_tile,move.promo);
				break;
			case 'C':
				//perform castles (move the correct rook)
				if(move.dest_tile == 6){
					this->blindMove(7,5);
				} else if(move.dest_tile == 2){
					this->blindMove(0,3);
				} else if(move.dest_tile == 58){
					this->blindMove(56,59);
				} else {
					this->blindMove(63,61);
				}
				break;
		}
	}
	
}

void ChessBoard::beginGame(){
	this->beginGame('A',1,0,-1);
}

void ChessBoard::beginGame(char mode){
	this->beginGame(mode,1,0,-1);
}
void ChessBoard::beginGame(char mode, char isWhite){
	this->beginGame(mode,isWhite,0,-1);
}
void ChessBoard::beginGame(char mode, char isWhite, char aiplaying){
	this->beginGame(mode,isWhite,aiplaying,-1);
}
/**
 * Opperate the game!
 *
 * Arguments:
 *   mode:      selects opponent: A = ai, H = human, S = AI self playing
 *   isWhite:   selects starting turn (1 = whites turn first, 0 = blacks)
 *   aiplaying: in mode A selects who the AI should play as, ignored in other modes
 *   rAiTime = requested AI time-limit (-1 for auto select)
 */
void ChessBoard::beginGame(char mode, char isWhite, char aiplaying, int rAiTime){
	char whiteTurn = isWhite;
	char loop = 1;
	char activeSquare = -1;
	int moveCount = 0;
	string message;
	
	int aiWaitTime;
	if(rAiTime != -1){
		aiWaitTime = rAiTime;
	} else {
		if(mode == 'S'){
			aiWaitTime = 750;
		} else {
			aiWaitTime = 3500;
		}
	}
	
	Rlist rlist;
	
	if(mode == 'A' && aiplaying == 1){
		this->show('C',moveCount,1);//keep board fliped for only player when black
	} else if(mode == 'H'){
		this->show('C',moveCount,!whiteTurn);//flip board for active player
	} else {
		this->show('C',moveCount);//leave board alone
	}
	
	cout << endl;
	
	while(loop){
		this->recalculateZhash(whiteTurn);
		rlist.increment(this->zhash);
		
		if(whiteTurn){
			moveCount += 1;
		}
		
		//game end conditions
		if(this->isCheckMate(whiteTurn)){
			
			int kingTile;
			if(whiteTurn){
				kingTile = this->whiteKingLoc;
			} else {
				kingTile = this->blackKingLoc;
			}
			
			if(this->isSquareCheck(kingTile,whiteTurn)){
				cout << "\033[1;36;40mCHECKMATE!\033[1;37;40m" << endl;
				if(whiteTurn){
					cout << "\033[1;34mBLACK \033[1;36;40mWINS!\033[1;37;40m" << endl;
				} else {
					cout << "\033[1;33mWHITE \033[1;36;40mWINS!\033[1;37;40m" << endl;
				}
			} else {//stalemate
				cout << "\033[1;36;40mSTALEMATE!\nDRAW!\033[1;37;40m" << endl;
			}
			break;
		}
		if(this->isDrawn()){
			cout << "\033[1;36;40mINSUFFICIENT MATERIAL!\nDRAW!\033[1;37;40m" << endl;
			break;
		}
		if(rlist.get(this->zhash) == 5){
			cout << "\033[1;36;40mFIVE-FOLD REPETITION!\nDRAW!\033[1;37;40m" << endl;
			break;
		}

		if((mode == 'A' && whiteTurn == aiplaying) || mode == 'S'){
			Node* node = renderBestMove(*this, rlist, whiteTurn, aiWaitTime, 'P');
			if(whiteTurn){
				cout << "WHITE-MOVE: \033[1;33m";
			} else {
				cout << "BLACK-MOVE: \033[1;34m";
			}
			cout << node->move << "\033[1;37;40m" << endl;
			
			this->performMove(node->move);
			activeSquare = node->move.dest_tile;
			
			if(mode == 'A' && aiplaying == 1){
				this->show('C',moveCount,1);//keep board fliped for only player when black
			} else if(mode == 'H'){
				this->show('C',moveCount,whiteTurn);//flip board for active player
			} else {
				this->show('C',moveCount);//leave board alone
			}
			cout << "\033[1;95;40mPerforming Move: " <<  node->move << " (" << node->value << ")" << " [" << node->depth << "]" << "\033[1;37;40m" << endl;
			
			whiteTurn = !whiteTurn;
			delete node;
			
			continue;//non-huamn moves will call contine to prevent input request
		}
		
		if(whiteTurn){
			cout << "WHITE-MOVE: \033[1;33m";
		} else {
			cout << "BLACK-MOVE: \033[1;34m";
		}
		
		//get move
		cin >> message;
		cout << "\033[1;37;40m";
		
		//Act on move request
		if(message.size() == 1 && message[0] == 'q'){
			break;
		}
		try{
			SingleMove* move = this->parseRequest(message,whiteTurn,activeSquare);
			
			this->performMove(*move);
			activeSquare = move->dest_tile;
			
			if(mode == 'A' && aiplaying == 1){
				this->show('C',moveCount,1);//keep board fliped for only player when black
			} else if(mode == 'H'){
				this->show('C',moveCount,whiteTurn);//flip board for active player
			} else {
				this->show('C',moveCount);//leave board alone
			}
			cout << "\033[1;32;40mPerforming Move: " << *move << "\033[1;37;40m" << endl;
			
			whiteTurn = !whiteTurn;
			delete move;
			
		} catch (char e) {
		
			//show board before error code
			if(mode == 'A' && aiplaying == 1){
				this->show('C',moveCount,1);//keep board fliped for only player when black
			} else if(mode == 'H'){
				this->show('C',moveCount,!whiteTurn);//flip board for active player
			} else {
				this->show('C',moveCount);//leave board alone
			}
		
			switch(e){
				case 'u':
					cout << "\033[1;31;40mMove Description not known\033[1;37;40m" << endl;
					break;
				case 'm':
					cout << "\033[1;31;40mMove is not possible\033[1;37;40m" << endl;
					break;
				case 't':
					cout << "\033[1;31;40mWrong colour piece\033[1;37;40m" << endl;
					break;
				case 'c':
					cout << "\033[1;31;40mMove would check the king\033[1;37;40m" << endl;
					break;
				case 'i':
					cout << "\033[1;31;40mInvalid char in move specification\033[1;37;40m" << endl;
					break;
				case 'A':
					cout << "\033[1;31;40mMoving piece requested does not match reality\033[1;37;40m" << endl;
					break;
				case '~':
					cout << "\033[1;31;40mAmbiguous move specified\033[1;37;40m" << endl;
					break;
				case 'N':
					cout << "\033[1;31;40mNo move like specified possible\033[1;37;40m" << endl;
					break;
				case '!':
					cout << "\033[1;33;40mCheat Move made!\033[1;37;40m" << endl;
					break;
				case 'U':
					cout << "\033[1;33;40mUtility Move Made!\033[1;37;40m" << endl;
					break;
				case 'S':
					cout << "\033[1;33;40mCheat Skip performed!\033[1;37;40m" << endl;
					whiteTurn = !whiteTurn;
					break;
				default:
					cout << "Move invalid: " << e << endl;
					throw e;
			}
		}
	}
	cout << endl;
}











