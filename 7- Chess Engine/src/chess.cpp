#include "chess.hpp"


using namespace std;

int main(int argc, char** argv){
	printf("\033[0m");//clears any leftover colours from the terminal
	
	//ChessBoard gameBoard = ChessBoard();
	//gameBoard.setupGame();
	
	//gameBoard.show('N',0,1);

	
	
	show_menu();
}


/* -------------------------------------- UI functions! ------------------------------------- */

namespace chessSettings{
	char mode = 'P';//P = play | B = Benchmark
	string board = "default";//default = standard else fen
	//play options
	char game_type = 'A';//H:human vs human A: human vs Ai S: AI vs AI
	int ai_time = 3500;//time for the AI to think
	char play_as = 1;//1 = White 0 = Black | only allpys to human vs AI games
	
	//benchmark options 
	char bench_type = 'M';//M == move gen | P = Perft
	char bench_depth = 4;//how deep to run non-default benchmarks to
}

/*
 * display the main menu for the chess AI
 */
void show_menu(){

	char loop = 1;
	string message;
	string responce;
	redraw_menu();
	cout << endl;
	while(loop){
		responce = "";
		cin >> message;
		if(message.length() == 0){
			continue;//blank lines do nothing
		}
		
		if(message.length() >= 2){
			responce = "\033[31mThe option '" + message + 
			           "' is too long! (1 character expected in the interval 0-9 or q or h)\033[33m";
		} else if(message[0] == 'q'){
			break;
		} else if(message[0] == 'h'){
			cout << "\033[34m=======Help=======\033[33m\n";
			cout << "\033[32m=======Menu=======\033[33m\n";
			cout << "The menu can be navigated by pressing the number of the\noption you wish to interact with: i.e 1 would take you to\nboard settings and 9 would start with the selected\nsettings.  There are 2 Main modes: the default \"Play\"\nmode and the benchmarking mode.  The benchmarking mode is\nused to quickly run tests to check the performance of the\ncurrent system and is not normally used so will not be\ncovered here.  The main \"Play\" mode has a few settings.\nFirst is Board which lets you select a FEN position to\nstart play from, the next is the type of game you want to\nplay (human vs human / human vs AI / AI vs AI) next for all\ngame types with an AI the length of time the AI is allowed\nto think for on each turn can be set. If this is set lower\nit will be an easier game and higher will make the game\nharder.  Finally, when playing against the AI you can\ndecide if you want to play white or black.\n";
			cout << "\033[32m=======Making Moves=======\033[33m\n";
			cout << "Most standard notations for chess moves are supported, below\nis a summary of them.  Examples will be in square []backets. \n >The first mode is square to square.  In this mode\n  you specify the starting square [e2] optionally write\n  an arrow [->] then the finishing square [e4] (e.g [e2e4] or [e2->e4]).  This method\n  has advanced move info (due to it being unambiguous) so if\n  a different move method is not working try the same move in\n  this notation to find out why the move is not allowed. \n >When promoting any move can be appended with equals then \n  a piece [=R] to select the promotion type, if no promotion\n  type is specified then a queen will be selected. \n >To castle the notation O-O or O-O-O can be used for castling\n  king and queen side, respectively. \nAlgebraic chess notation is also generally supported,\nthis is summarised below:\n >A piece can be moved by specifying the piece [P/R/N/B/Q/K] \n  then the destination square. E.g. [Ba4] means Bishop to a4 \n >Where this is ambiguous a phile and/or rank of the origin\n  square can be included after the piece specification to\n  resolve the ambiguity. [B3a4] means bishop on the 3rd rank\n  to the square a4\n >The Piece can be omitted if it is a pawn where\n  this is unambiguous.  [e4] means pawn to e4 \n >If a square last moved to/on by the opponent can be taken\n  on with the takes [x] or X notation. [Bx] means bishop\n  takes on the square the opponent just moved to.\n";
			cout << "\n\033[32mPress enter to continue\033[33m" << endl;
			cin.ignore();//Clear trailing newline (effective non-blocking)
			cin.ignore();//wait for user to push enter

		} else if(message[0] == '0'){
			if(chessSettings::mode == 'P'){
				chessSettings::mode = 'B';
			} else {
				chessSettings::mode = 'P';
			}
		} else if(message[0] == '1'){
			redraw_menu();
			cout << "\033[36mPlease enter a FEN position or enter 'd' to restore to (d)efaults\033[33m" << endl;
			string fen;
			
			std::getline(cin,fen);//Clear trailing newline (effective non-blocking)
			std::getline(cin,fen);//read a line (with possible whitespace)
			
			if(fen.length() == 1 && fen[0] == 'd'){
				chessSettings::board = "default";
				responce = "\033[32mRestoring to default\033[33m";
			} else if(fen.length() >= 1 && isValidFEN(fen)){
				chessSettings::board = fen;
				responce = "\033[32mFEN position accepted\033[33m";
			} else {
				responce = "\033[31mInvalid FEN position\033[33m";
			}
		} else if(message[0] == '2'){
			if(chessSettings::mode == 'P'){
				switch(chessSettings::game_type){
					case 'H':
						chessSettings::game_type = 'A';
						break;
					case 'A':
						chessSettings::game_type = 'S';
						break;
					case 'S':
						chessSettings::game_type = 'H';
						break;
				}
			} else {
				if(chessSettings::bench_type == 'M'){
					chessSettings::bench_type = 'P';
				} else {
					chessSettings::bench_type = 'M';
				}
			}
		} else if(message[0] == '3'){
			if(chessSettings::mode == 'P' && chessSettings::game_type != 'H'){
				redraw_menu();
				cout << "\033[36mPlease enter a Time Limit for the Ai's turns or enter 'd' to restore to (d)efaults\033[33m" << endl;
				string aitms;
				cin >> aitms;
				aitms.erase(remove(aitms.begin(), aitms.end(), ','), aitms.end());
				if(aitms.length() == 1 && aitms[0] == 'd'){
					chessSettings::ai_time = 3500;
					responce = "\033[32mRestoring to default.\033[33m";
				} else if(aitms.length() >= 7){
					responce = "\033[31mThe responce '" + aitms +"' is too long to be valid!\033[33m";
				} else {
					int val = 0;
					for(int i = 0; i < aitms.length(); i++){
						if(aitms[i] <= 57 && aitms[i] >= 48){
							val = val * 10 + (aitms[i]-48);
						} else {
							responce = "\033[31mThe character '";
							responce += aitms[i];
							responce += "' at position ";
							responce += i;
							responce += " is not a number!\033[33m";
						}
					}
					chessSettings::ai_time = val;
				}
			} else if (chessSettings::mode == 'B' && chessSettings::board != "default"){
				redraw_menu();
				cout << "\033[36mPlease enter a Depth for the search or enter 'd' to restore to (d)efaults\033[33m" << endl;
				
				string dpth;
				cin >> dpth;
				
				
				if(dpth.length() == 1 && dpth[0] == 'd'){
					chessSettings::bench_depth = 4;
					responce = "\033[32mRestoring to default.\033[33m";
				} else {
					int rdepth = 0;
					for(int i = 0; i < dpth.length(); i++){
						if(dpth[i] <= 57 && dpth[i] >= 48){
							rdepth = rdepth * 10 + (dpth[i]-48);
						} else {
							responce = "\033[31mThe character '";
							responce += dpth[i];
							responce += "' at position ";
							responce += i;
							responce += " is not a number!\033[33m";
						}
					}
					
					if(rdepth > 35){//35 picked as there is apsolutly no circumstance where 35 is possible 
						responce = "\033[31mThe responce '" + dpth +"' is too large to ever complete in resonable time!\033[33m";
					} else {
						chessSettings::bench_depth = rdepth;
					}
				}
				
				
			} else {
				responce = "\033[31mOption 3 is not avalible in this Mode/Game Type!\033[33m";
			}
		} else if(message[0] == '4'){
			if(chessSettings::mode == 'P' && chessSettings::game_type == 'A'){
				if(chessSettings::play_as){
					chessSettings::play_as = 0;
				} else {
					chessSettings::play_as = 1;
				}
			}
		} else if(message[0] == '9'){
			if(chessSettings::mode == 'P'){
				ChessBoard gameBoard = ChessBoard();
				gameBoard.setupGame();
				char toMove = 1;
				if(chessSettings::board != "default"){
					toMove = gameBoard.loadFromFen(chessSettings::board);
				}
				gameBoard.beginGame(chessSettings::game_type, 
				                    toMove, 
				                    !chessSettings::play_as,
				                    chessSettings::ai_time);
			} else {
				if(chessSettings::board == "default"){
					if(chessSettings::bench_type == 'M'){
						printf("\033[0m\n");
						runAllBestMoveBenchmarkTests();
					} else {
						printf("\033[0m\n");
						runAllPositionReachedBenchmarkTest();
					}
				} else {
					ChessBoard gameBoard = ChessBoard();
					gameBoard.setupGame();
					char toMove = gameBoard.loadFromFen(chessSettings::board);
					
					if(chessSettings::bench_type == 'M'){
						printf("\033[0m\n");
						runBestMoveBenchmarkTest(gameBoard, toMove, chessSettings::bench_depth);
					} else {
						printf("\033[0m\n");
						runPositionReachedBenchmarkTest(gameBoard,toMove,chessSettings::bench_depth);
					}
				}
			}
		} else {
			responce = "\033[31mThe option '" + message + "' is not known!\033[33m";
		}
		redraw_menu();
		cout << responce << endl;
	}
	
	printf("\033[0m\n");//when this funciton terminates reset/fix the console colours
}


/*
 * Draws the graphics for the main menu - normally called from the show_menu function
 */
void redraw_menu(){
	cout << "\033[1;33;40m\n"
	     << "\033[0;33;40m-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\033[1m\n\n\n"
	     << "   _____   _                                       _____ \n"
	     << "  / ____| | |                              /\\     |_   _|\n"
	     << " | |      | |__     ___   ___   ___       /  \\      | |  \n"
	     << " | |      | '_ \\   / _ \\ / __| / __|     / /\\ \\     | |   \n"
	     << " | |____  | | | | |  __/ \\__ \\ \\__ \\    / ____ \\   _| |_  \n"
	     << "  \\_____| |_| |_|  \\___| |___/ |___/   /_/    \\_\\ |_____| \n"
	     << '\n' << " 0) Mode:       ";
	if(chessSettings::mode == 'P'){
		cout << "\033[4mPlay\033[24m\n"
			 << " 1) Board:      " << (chessSettings::board == "default"
			     ? "\033[4mDefault\033[24m"
			     : chessSettings::board) << '\n'
			 << " 2) Game Type:  " << (chessSettings::game_type == 'A' 
			     ? "\033[4;32mHuman\033[33m vs \033[35mAI\033[24;33m"
			     : (chessSettings::game_type == 'H'
			         ? "\033[32mHuman\033[33m vs \033[32mHuman\033[33m"
			     	 : "\033[35mAI\033[33m vs \033[35mAI\033[33m"
			    )) << '\n'
			 << (chessSettings::game_type != 'H' 
			     ? (" 3) AI Limit:   " + commafy(chessSettings::ai_time) + "ms\n")
			     : "\n")
			 << (chessSettings::game_type == 'A' 
			     ? (" 4) Play As:    " + (string)(chessSettings::play_as
			         ? "\033[4mWhite\033[24m\n"
			         : "\033[34mBlack\033[33m\n"))
			     : "\n")
			 << "\n 9) Go!\n";
	} else {//benchmarking mode
		cout << "\033[35mBenchmark\033[33m\n"
		     << " 1) Board:      " << (chessSettings::board == "default"
			     ? "\033[4mDefault\033[24m"
			     : chessSettings::board) << '\n'
		     << " 2) Bench Type: " << (chessSettings::bench_type == 'M'
		         ? "\033[4;35mBest-Move\033[24;33m"
		         : "\033[36mPerft\033[33m") << '\n'
		     << (chessSettings::board == "default" ? "\n" :
		     	" 3) Depth:      " + to_string((int)(chessSettings::bench_depth)) + "\n"
		     	)
		     << "\n\n 9) Go!\n";
	}
	
	cout << "\n\n\033[0;33;40m(h)elp                                             (q)uit\033[1m"
	     << "  \n\033[0;33;40m-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\033[1m" << endl;//newline and flush output
}

/*
 * Checks if the passed in FEN-string is valid
 */
char isValidFEN(string fen){
	char fenIndex = -1;
	
	char row = 0;
	char col = 0;
	char val;
	
	while(fen[++fenIndex] != ' '){
		val = fen[fenIndex];
		if(val == '/'){
			row += 1;
			col = 0;
		} else if(val < 58 && val > 48){
			col += val-48;
		} else {
			if(val == 'p' || val == 'r' || val == 'b' || val == 'n' || val == 'q' || val == 'k' ||
			   val == 'P' || val == 'R' || val == 'B' || val == 'N' || val == 'Q' || val == 'K'   ){
				col += 1;
			} else {
				//cout << "CHAR";
				return 0;//invalid char encountered
			}
		}
		
		if(row > 8 || col > 8){
			//cout << "ROLCOL";
			return 0;//invalid row/column number
		}
	}
	
	fenIndex++;
	
	if(fen[fenIndex] != 'w' && fen[fenIndex] != 'b'){
		//cout << "TOMOVE";
		return 0;//invalid to-move
	}
	
	fenIndex++;

	while(fen[++fenIndex] != ' '){
		switch(fen[fenIndex]){
			case 'K':
			case 'Q':
			case 'k':
			case 'q':
			case '-':
				break;
			default:
				//cout << "CASTLE";
				return 0;//invalid castleing info
		}
	}
	
	fenIndex++;
	
	if(!(fen[fenIndex] == '-' || //no enpass
	      (  
	     	(fen[fenIndex  ] < 105 && fen[fenIndex  ] > 96) && //this char is a phile
	        (fen[fenIndex+1] < 58  && fen[fenIndex+1] > 48)    //this char is a rank
	      )
	    ) 
	  ){
	     //cout << "ENPASS";
	     return 0;//Invalid enpass info
	}
	
	//rest of the FEN not validated as not used so no need

	return 1;
}


                                    
                                    



/* ---------------------------------------- TESTING! ----------------------------------------- */

/* ============================== Position Reached testing ============================== */
int positionReachedTest(ChessBoard& board, char depth){
	return positionReachedTest(board,depth,1,-1);
}

int positionReachedTest(ChessBoard& board, char depth, char isWhite){
	return positionReachedTest(board,depth,isWhite,-1);
}
/*
 * Performs a perft test on a given board
 * Arguments:
 *   board:        The board to test
 *   depth:        The depth to check until
 *   isWhite:      If the Person to play is white
 *   faultFlagNum: The number at which it flag all found moves and the size of the tree below them (with an aim to identifing faulty moves)
 */
int positionReachedTest(ChessBoard& board, char depth, char isWhite, char faultFlagNum){
	if(depth == 0){
		return 1;
	}
	
	int numPos = 0;
	
	vector<SingleMove> moves;
	board.getAllSideMoves(moves, isWhite);
	board.trueValidMoves(moves, isWhite);
	
	for(int i = 0; i < moves.size(); i++){
		ChessBoard newBoard = ChessBoard(board);
		newBoard.performMove(moves[i]);
		if(faultFlagNum == 1 && depth == 1){
			cout << moves[i] << ": 1" << endl;
		} else if(depth == faultFlagNum){
			cout << moves[i] << ": ";
		}
		numPos += positionReachedTest(newBoard,depth-1,!isWhite,faultFlagNum);
		
	}
	if(depth == faultFlagNum-1){
		cout << numPos << endl;
	}
	return numPos;
}


void runPositionReachedDepthTest(ChessBoard& board,char isWhite){
	 runPositionReachedDepthTest(board,isWhite, 500);
}
/*
 * Run "positionReachedTest" tests at increasing depth until cutoff miliseconds have passed
 */
void runPositionReachedDepthTest(ChessBoard& board,char isWhite, int cutoff){
	auto start = chrono::high_resolution_clock::now();
	//auto end = chrono::high_resolution_clock::now();
	//cout << std::chrono::duration_cast<std::chrono::milliseconds>(end-start).count() << endl;
	
	int depth = 1;
	int pos = 0;
	
	while(chrono::duration_cast<chrono::milliseconds>(chrono::high_resolution_clock::now()-start).count() < cutoff){
		cout << "Testing at depth: " << depth << " : " << std::flush;
		pos = positionReachedTest(board, depth, isWhite);
		cout << pos << " | Took: " << chrono::duration_cast<chrono::milliseconds>(chrono::high_resolution_clock::now()-start).count() << "ms" << endl;
		
		depth++;
	}
}

void runPositionReachedBenchmarkTest(ChessBoard& board,char isWhite, int depth){
	runPositionReachedBenchmarkTest(board, isWhite, depth, -1, 1);
}
void runPositionReachedBenchmarkTest(ChessBoard& board,char isWhite, int depth, int expected){
	runPositionReachedBenchmarkTest(board, isWhite, depth, expected, 1);
}
/*
 * Performs position reached tests for move generation benchmarking purposes.
 * Arguments:
 *   board:    The board to test on
 *   isWhite:  If the player to move is white
 *   depth:    The depth to benchmark at
 *   expected: The Expected number of moves generated (to aid in detecting errors in move gen)
 *   reps:     How manny times to repeat tests
 */
void runPositionReachedBenchmarkTest(ChessBoard& board,char isWhite, int depth, int expected, int reps){
	int pos = 0;
	for(int i = 0; i < 1; i++){
		cout << "Testing at depth: " << depth << " : " << std::flush;
		
		auto start = chrono::high_resolution_clock::now();
		pos = positionReachedTest(board, depth, isWhite);
		auto timeval = chrono::duration_cast<chrono::microseconds>(chrono::high_resolution_clock::now()-start).count();
		
		if(expected == -1){
			cout << "\033[33m";
		}else if(pos == expected){
			cout << "\033[1;32m";
		} else {
			cout << "\033[1;31m";
		}
		cout << pos << "\033[0m | Took: " << timeval << " us" << endl;
	}
}

/*
 * Run 3 perft tests known to highlight bugs in move gen
 */
void runAllPositionReachedBenchmarkTest(){
	ChessBoard testBoard = ChessBoard();
	testBoard.setupGame();
	
	cout << "Testing board 1: (position 4)" << endl;
	testBoard.loadFromFen("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1");
	runPositionReachedBenchmarkTest(testBoard,1,4,422333);
	
	cout << "Testing board 2: (Position 5)" << endl;
	testBoard.loadFromFen("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8");
	runPositionReachedBenchmarkTest(testBoard,1,4,2103487);

	cout << "Testing board 3: (Position 6)" << endl;
	testBoard.loadFromFen("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10");
	runPositionReachedBenchmarkTest(testBoard,1,4,3894594);
}
/* ====== supporting ====== */

/*
 * prepend a string to length len with 0's
 */
string prepend0(string str,int len){
	if(str.length() < len){
		return "0"+prepend0(str,len-1);
	}
	return str;
}

/*
 * Convert the suplied number to a comma seperated string
 */
string commafy(unsigned long long int num){
	if(num >= 1000){
		return commafy(num/1000)+","+prepend0(to_string(num%1000),3);
	}
	return to_string(num);
	
}

/* ============================== Best Move Testing ============================== */


/*
 * Generate the best move from a given position timing the process
 */
void runBestMoveBenchmarkTest(ChessBoard& board, char isWhite, int depth){
	for(int i = 0; i < 1; i++){
		cout << "Searching at depth: " << depth << " | " << std::flush;
		
		resetNodeAiVisitCount();
		
		auto start = chrono::high_resolution_clock::now();
		Rlist rlist;
		Node* node = renderBestMove(board, rlist, isWhite, depth, 'B');
		auto timeval = chrono::duration_cast<chrono::microseconds>(chrono::high_resolution_clock::now()-start).count();
		
		cout << "Found: " << *node << " | Visiting:" << getNodeAiVisitCount() << " | Took: " << timeval << " us" << endl;
		delete node;
	}
}

/*
 * Run Benchmarking test from numerour positions for optimising code
 */
void runAllBestMoveBenchmarkTests(){
	auto start = chrono::high_resolution_clock::now();
	ChessBoard testBoard = ChessBoard();
	testBoard.setupGame();
	
	cout << "Testing board 1: (Base Position)" << endl;
	testBoard.setupGame();
	runBestMoveBenchmarkTest(testBoard, 1, 6);
	//runPositionReachedBenchmarkTest(testBoard,1,6);
	
	cout << "Testing board 2: (Alpha Beta Prune Tests)" << endl;
	testBoard.loadFromFen("rnbqkbnr/ppppp3/8/4N3/2BP1BQ1/4P1Pp/PPP4P/RN2K2R w KQkq - 0 1");
	runBestMoveBenchmarkTest(testBoard, 1, 5);
	//runPositionReachedBenchmarkTest(testBoard, 1, 4);
	
	cout << "Testing board 3: (Puzzle: Mate in 3)" << endl;
	testBoard.loadFromFen("3q1r1k/2p4p/1p1pBrp1/p2Pp3/2PnP3/5PP1/PP1Q2K1/5R1R w - - 1 0");
	runBestMoveBenchmarkTest(testBoard, 1, 5);
	//runPositionReachedBenchmarkTest(testBoard, 1, 4);

	cout << "Testing board 4: (Mate in 1)" << endl;
	testBoard.loadFromFen("1k6/3Q4/2K5/8/8/8/8/8 w - - 0 1");
	runBestMoveBenchmarkTest(testBoard, 1, 10);
	//runPositionReachedBenchmarkTest(testBoard, 1, 6);
		
	cout << "Testing board 5: (Mate in 2)" << endl;
	testBoard.loadFromFen("8/8/8/8/5k2/8/4q3/6K1 b - - 0 1");
	runBestMoveBenchmarkTest(testBoard, 0, 8);
	//runPositionReachedBenchmarkTest(testBoard, 0, 6);
	
	cout << "Testing board 6: (Position 5)" << endl;
	testBoard.loadFromFen("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8");
	runBestMoveBenchmarkTest(testBoard, 1, 6);
	//runPositionReachedBenchmarkTest(testBoard, 1, 4);

	cout << "Testing board 7: (Mid Game)" << endl;
	testBoard.loadFromFen("r1b1k2r/p1ppqpb1/Bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPB1PPP/R3K2R b KQkq - 0 1");
	runBestMoveBenchmarkTest(testBoard, 0, 6);
	//runPositionReachedBenchmarkTest(testBoard, 0, 6);
	
	cout << "Testing board 8: (Mate in 10 Mid game)" << endl;
	testBoard.loadFromFen("rn1kqbnr/p3p3/1p4p1/1N1RN2p/Q1p1P3/8/PP3PPP/R1B3K1 b Qkq - 0 1");
	runBestMoveBenchmarkTest(testBoard, 0, 6);
	
	auto timeval = chrono::duration_cast<chrono::microseconds>(chrono::high_resolution_clock::now()-start).count();
	showBMtimes();
	cout << "Total time to run all tests: \033[1;32m" << commafy(timeval) << "\033[0m us" << endl;
}



	
