#include "ChessAI.hpp"

using namespace std;

/*===============Constants==================*/

OpeningBook mainOpeningBook('L');

/*===============DEBUG======================*/
int benchmarkingNodeAiCount = 0;


void resetNodeAiVisitCount(){
	benchmarkingNodeAiCount = 0;
}
int getNodeAiVisitCount(){
	return benchmarkingNodeAiCount;
}

unsigned long long int genTime = 0;
unsigned long long int filterTime = 0;
unsigned long long int sortTime = 0;
unsigned long long int miscTime = 0;
unsigned long long int testTime = 0;

void resetBMtimes(){
	genTime = 0;
	filterTime = 0;
	sortTime = 0;
	miscTime = 0;
	testTime = 0;
}

void showBMtimes(){
	cout << "TIME: gen:\033[1;32m" << genTime/1000
		 << "\033[0m filter:\033[1;32m" << filterTime/1000
		 << "\033[0m sort:\033[1;32m" << sortTime/1000
		 << "\033[0m test:\033[1;31m" << testTime/1000
		 << "\033[0m misc:\033[1;32m" << miscTime/1000 << "\033[0m" << endl;
}

/*===============Main======================*/
static void showProgBar(int percent, int depth){
	cout << "[" << setw(40) << left << string((percent*40)/100, '-') 
		 << "] (depth: " << setw(3) << right << depth << ")\r" << std::flush;
}

//No rlist requried - for debug use only
Node* renderBestMove(ChessBoard& board, char isWhite, int cutoff){
	Rlist rlist;
	return renderBestMove(board, rlist, isWhite, cutoff, 'N');
}
Node* renderBestMove(ChessBoard& board, Rlist& rlist, char isWhite, int cutoff){
	return renderBestMove(board, rlist, isWhite, cutoff, 'N');
}


/**
 * Generate the best move from the given position.
 * Arguments:
 *   board: The position to generate from
 *   grlist: The global repeating move list
 *   isWhite: 1 when white move is to be generated 0 for black
 *   flag: B = Benchmark mode, N = Normal, P = Progress bar shown
 *
 * node: should not be called from checkmate.
 * 
 * 
 */
Node* renderBestMove(ChessBoard& board, Rlist& grlist, char isWhite, int cutoff, char flag){
	board.recalculateZhash(isWhite);
	srand((unsigned int)(time(NULL))^(unsigned int)(board.zhash));//ensures random seed even if multiple calls in same ms
	//check opening book
	if(mainOpeningBook.contains(board.zhash)){
		vector<SingleMove> moves = mainOpeningBook[board.zhash];
		return new Node(moves[(rand() % moves.size())],0,0);
	}
		

	//search wide inits:
	vector<SingleMove> moves;
	moves.reserve(45);
	board.getAllSideMoves(moves, isWhite);
	board.trueValidMoves(moves, isWhite);
	
	//init transposition table
	Ttable transTable = Ttable();
	
	
	
	//initalise with the worse possible value for the playing side ensuring that any move is preferable
	int initial_Best = (1-(2*isWhite))*10000000;
	
	Node* last_solution = new Node(moves[0],initial_Best,0);
	
	int depth = 0;
	
	//Internal inits
	int bestVal;
	int curVal;
	int reps;
	vector<int> bestIndexes;
	
	ChessBoard curBoard = ChessBoard();
	Rlist lrlist;
	
	auto start = chrono::high_resolution_clock::now();
	auto timeval = chrono::duration_cast<chrono::microseconds>(chrono::high_resolution_clock::now()-start).count();
	
	char subcheck = 0;
	
	while(1){
		depth += 1;
		if(flag == 'B' && depth == cutoff){
			return last_solution;
		}
		//if a 100th of the set time has passed return
		timeval = chrono::duration_cast<chrono::microseconds>(chrono::high_resolution_clock::now()-start).count();
		if(timeval > cutoff*10){
			subcheck = 1;
		}
		if(flag == 'P'){//show prgress bar
			showProgBar(   (100*min(timeval,(long int) cutoff))   /   cutoff   ,depth);
		}
		
		bestVal = initial_Best;
		bestIndexes.clear();
		
		//sequence here as may update
		sequenceMoves(board, moves, transTable, isWhite);
		
		for(int i = 0; i < moves.size(); i++){
			if(subcheck && flag != 'B'){
				timeval = chrono::duration_cast<chrono::milliseconds>(chrono::high_resolution_clock::now()-start).count();
				if(timeval > cutoff){
					if(flag == 'P'){//clear prgress bar
						cout << setw(55) << ' ' << "\r" << std::flush;
					}
					return last_solution;
				}
				if(flag == 'P'){//show prgress bar
					showProgBar(   (100*min(timeval,(long int) cutoff))   /   cutoff   ,depth);
				}
			}
		
			
			curBoard.cloneBoard(board);
			curBoard.updateZhashForMove(moves[i]);
			curBoard.performMove(moves[i]);
			
			reps = grlist.get(curBoard.zhash);
			
			if(reps == 4){
				curVal = 0;
			} /* Only generate a curVal on non-drawn boards */ 
			else if(depth == 1){
				curVal = curBoard.courseValue();
			} else {
				curVal = deviseNodeValue(curBoard, grlist, lrlist, !isWhite, transTable, depth-1, ((depth*2)/3), flag);
			}
			
			switch(reps){
				case 0:
					break;
				case 1:
					curVal = (curVal*95)/100;
					break;
				case 2:
					curVal = (curVal*80)/100;
					break;
				case 3:
					curVal = (curVal*50)/100;
					break;
				case 4:
					curVal = 0;
					break;
			}
			
			if(curVal == bestVal){
				bestIndexes.push_back(i);
			}
			if(isWhite && curVal > bestVal || !isWhite && curVal < bestVal){
				bestIndexes.clear();
				bestVal = curVal;
				bestIndexes.push_back(i);
			}
		}
		
		delete last_solution;
		last_solution = new Node(moves[bestIndexes[(rand() % bestIndexes.size())]],bestVal,depth);
	}
	
}


int deviseNodeValue(ChessBoard& board, Rlist& grlist, Rlist& lrlist, char isWhite, Ttable& transTable, int depth, int depthCutoff){
	return deviseNodeValue(board, grlist, lrlist, isWhite, transTable, depth, depthCutoff, 'N', -10000000, 10000000);
}

int deviseNodeValue(ChessBoard& board, Rlist& grlist, Rlist& lrlist, char isWhite, Ttable& transTable, int depth, int depthCutoff, char flag){
	return deviseNodeValue(board, grlist, lrlist, isWhite, transTable, depth, depthCutoff, flag, -10000000, 10000000);
}
/*
 * The main recursive element of move generation.  
 * Does very simmilar stuff to renderBestMove except everything is optimised and the output 
 * assumes that it is being called from a posiotion that doesn't need to know the
 * best move from here only what value that best move yeilds
 */
int deviseNodeValue(ChessBoard& board, Rlist& grlist, Rlist lrlist, char isWhite, Ttable& transTable, int depth, int depthCutoff, char flag, int alpha, int beta){
	//auto tstart = chrono::high_resolution_clock::now();
	//auto ttimeval = chrono::duration_cast<chrono::nanoseconds>(chrono::high_resolution_clock::now()-tstart).count();
	if(transTable.contains(board.zhash)){
		pair<int,int> res = transTable[board.zhash];
		if(depth <= res.first){
			return res.second;
		}
	}

	vector<SingleMove> moves;
	moves.reserve(45);
	
	if(1){
		board.getAllSideMoves(moves, isWhite, 'O');
		/*miscTime += moves.size();
		sortTime = max((int)sortTime,(int)moves.size());
		testTime += 1;
		genTime += respair.first;
		filterTime += respair.second;*/
		board.trueValidMoves(moves, isWhite);
		if(depth >= depthCutoff){//only sequence moves that have a large effect on the tree
			sequenceMoves(board, moves, transTable, isWhite);
		}
	} else { // benchmarking branch optimised away
		auto start = chrono::high_resolution_clock::now();
		auto timeval = chrono::duration_cast<chrono::nanoseconds>(chrono::high_resolution_clock::now()-start).count();
		
		start = chrono::high_resolution_clock::now();
		board.getAllSideMoves(moves, isWhite, 'O');
		timeval = chrono::duration_cast<chrono::nanoseconds>(chrono::high_resolution_clock::now()-start).count();
		genTime += timeval;
		
		start = chrono::high_resolution_clock::now();
		board.trueValidMoves(moves, isWhite);
		timeval = chrono::duration_cast<chrono::nanoseconds>(chrono::high_resolution_clock::now()-start).count();
		filterTime += timeval;
		
		//correction:
		start = chrono::high_resolution_clock::now();
		timeval = chrono::duration_cast<chrono::nanoseconds>(chrono::high_resolution_clock::now()-start).count();
		genTime -= timeval;
		filterTime -= timeval;
		
		if(depth >= depthCutoff){//only sequence moves that have a large effect on the tree
			//time correction: 
			sortTime -= timeval;
			
			
			start = chrono::high_resolution_clock::now();
			sequenceMoves(board, moves, transTable, isWhite);
			timeval = chrono::duration_cast<chrono::nanoseconds>(chrono::high_resolution_clock::now()-start).count();
			sortTime += timeval;
		}
	}
		
	if(moves.size() == 0){
		if(isWhite){
			if(board.isSquareCheck(board.whiteKingLoc,1)){
				//as no moves mean king is taken next turn this -100000
				// 1000*depth causes the quickest mate to be prefered
				return -(100000+1000*depth);
			} else {
				return 0;//stale mate so 0
			}
		} else {
			if(board.isSquareCheck(board.blackKingLoc,0)){
				//as no moves mean king is taken next turn this -100000
				// 1000*depth causes the quickest mate to be prefered
				return (100000+1000*depth);
			} else {
				return 0;//stale mate so 0
			}
		}
	}
	
	lrlist.increment(board.zhash);
	
	int bestVal = (1-(2*isWhite))*10000000;//initalise with the worse possible value for the playing side ensuring that any move is preferable
	
	int curVal;	
	ChessBoard curBoard = ChessBoard();
	
	int repmul;
	
	int reps;
	int i;
	for(i = 0; i < moves.size(); i++){
		
		curBoard.cloneBoard(board);
		curBoard.updateZhashForMove(moves[i]);
		curBoard.performMove(moves[i]);
	
		reps = grlist.get(curBoard.zhash)+lrlist.get(curBoard.zhash);
		if(reps == 4){
			curVal = 0;
		} /* Only generate a curVal on non-drawn boards */ 
		else if(depth == 1){
			curVal = curBoard.courseValue();
		} else {
			curVal = deviseNodeValue(curBoard, grlist, lrlist, !isWhite, transTable, depth-1, depthCutoff, flag, alpha, beta);
		}
		
		switch(reps){
			case 0:
				break;
			case 1:
				curVal = (curVal*95)/100;
				break;
			case 2:
				curVal = (curVal*80)/100;
				break;
			case 3:
				curVal = (curVal*50)/100;
				break;
			case 4:
				curVal = 0;
				break;
		}

		if(isWhite){
			bestVal = max(bestVal,curVal);
			alpha = max(alpha, bestVal);
			if(alpha >= beta){//beta cutoff
				break;
			}
		} else {
			bestVal = min(bestVal,curVal);
			beta = min(beta,bestVal);
			if(beta <= alpha){
				break;
			}
		}
	}
	
	if(flag == 'B' && depth == 1){
		benchmarkingNodeAiCount += i;
	}
	
	transTable.add(board.zhash,depth,bestVal);
	
	return bestVal;
}


/*===============Supporting======================*/

/*
 * Helper for efficent sorting
 */
static bool chessAImoveComparator (pair<int,int> i,pair<int,int> j) { 
	return (i.second > j.second); 
}

/*
 * Sorts the moves for increased gains from the alpha-beta pruning
 */
void sequenceMoves(ChessBoard& board,vector<SingleMove>& moves, Ttable& transTable, char isWhite){
	vector<pair<int,int>> moveVal;
	int val;
	char sourceTile;
	char sourcepc;
	char destTile;
	char destpc;
	char mv_attackable;
	
	pair<int,int> respair = board.getPointsOnBoard();
	int w_points_on_board = respair.first;
	int b_points_on_board = respair.second;
	
	int Wendness = max(0,(60-(10*w_points_on_board))/6);
	int Bendness = max(0,(60-(10*b_points_on_board))/6);
	int Gendness = min((Wendness+Bendness),10);
	
	int Wmidness = max(0,80-max(0,(10*w_points_on_board)-70))/8;
	int Bmidness = max(0,80-max(0,(10*b_points_on_board)-70))/8;
	int Gmidness = min(((Wmidness+Bmidness)*14)/20,10);
	
	ChessBoard hashGenBoard = ChessBoard();
	
	for(int i = 0; i < moves.size();i++){
		hashGenBoard.cloneBoard(board);
		hashGenBoard.updateZhashForMove(moves[i]);
		
		if(transTable.contains(hashGenBoard.zhash)){
			pair<int,int> res = transTable[hashGenBoard.zhash];
			if(isWhite){
				val = res.second;
			} else {
				val = -res.second;
			}
			
		} else {
			val = 0;
			sourceTile = moves[i].source_tile;
			sourcepc = board.board[sourceTile];
			destTile = moves[i].dest_tile;
			destpc = board.board[destTile];
			mv_attackable = board.isSquareCheck(destTile,isWhite);
			
			if(destpc == ' '){}//filter line
			else if(destpc < 91){
				switch(destpc){//capturing piece
					case 'P':
						val += 100;
						break;
					case 'Q':
						val += 900;
						break;
					case 'R':
						val += 500;
						break;
					case 'B':
						val += 315;
						break;
					case 'N':
						val += 300;
						break;
				}
			} else {
				switch(destpc){//capturing piece
					case 'p':
						val += 100;
						break;
					case 'q':
						val += 900;
						break;
					case 'r':
						val += 500;
						break;
					case 'b':
						val += 315;
						break;
					case 'n':
						val += 300;
						break;
				}
			}
			
			
			if(mv_attackable){//taking piece
				if(sourcepc < 91){
					switch(sourcepc){
						//10 less than normal to encorage looking at equal exchange moves before moves with nothing fun
						case 'P':
							val -= 90;
							break;
						case 'Q':
							val -= 890;
							break;
						case 'R':
							val -= 490;
							break;
						case 'B':
							val -= 305;
							break;
						case 'N':
							val -= 290;
							break;
						
					}
				} else {
					switch(sourcepc){
						//10 less than normal to encorage looking at equal exchange moves before moves with nothing fun
						case 'p':
							val -= 90;
							break;
						case 'q':
							val -= 890;
							break;
						case 'r':
							val -= 490;
							break;
						case 'b':
							val -= 305;
							break;
						case 'n':
							val -= 290;
							break;
					}
				}
			}
			
			//prioritize promotion
			if(moves[i].extra == 'P' ){
				val += 300;
				if(moves[i].promo == 'Q' || moves[i].promo == 'q'){
					val += 600;
				}
			}
			
			//knight map bonus
			if(sourcepc == 'n' || sourcepc == 'N'){
				val += ChessBoard::knightMap[destTile];
			}
			
			//king map
			if(sourcepc == 'K'){
				val += ((Wendness*ChessBoard::kingEndMap[i])/5)+((Gmidness*ChessBoard::kingMidMapW[i])/5);
			} else if(sourcepc == 'k'){
				val += ((Bendness*ChessBoard::kingEndMap[i])/5)+((Gmidness*ChessBoard::kingMidMapW[i])/5);
			}
			
			//rook early map not needed as rooks are not ever the best move early on
			
			//pawns:
			if(sourcepc == 'P'){
				val += ChessBoard::pawnMapW[destTile] + (Gendness*ChessBoard::pawnPromoMapW[i]/4);
			} else if(sourcepc == 'p'){
				val += ChessBoard::pawnMapB[destTile] + (Gendness*ChessBoard::pawnPromoMapB[i]/4);
			}
		}
		moveVal.emplace_back(i,val);
	}
	
	std::sort (moveVal.begin(), moveVal.end(), chessAImoveComparator);
	
	vector<SingleMove> oldMoves(moves);
	
	for(int i = 0; i < oldMoves.size(); i++){
		moves[i] = oldMoves[moveVal[i].first];
	}
}

























