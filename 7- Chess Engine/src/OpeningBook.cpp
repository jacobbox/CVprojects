#include "OpeningBook.hpp"

using namespace std;

/* ------------------ Construct ------------------- */

OpeningBook::OpeningBook() : unordered_map<size_t,std::vector<SingleMove>,OPENINGBOOK_INTERNAL::PreservingHasher>(){}

OpeningBook::OpeningBook(char flag) : OpeningBook(){
	if(flag == 'L'){
		this->loadBookFromFile();
	}
}

/* ------------------ Usage ------------------- */
char OpeningBook::contains(size_t zhash){
	if (this->find(zhash) == this->end()){
		return 0;
	}
    return 1;
}

void OpeningBook::add(size_t zhash, SingleMove& move){
	vector<SingleMove>* moves = new vector<SingleMove>();
	(*moves).push_back(move);
	this->emplace(zhash,*moves);
}

void OpeningBook::add(size_t zhash, vector<SingleMove>& moves){
	this->emplace(zhash,moves);
}

void OpeningBook::add(ChessBoard& board, vector<SingleMove>& moves){
	this->emplace(board.zhash,moves);
}

void OpeningBook::appendMove(ChessBoard& board, SingleMove& move){
	this->appendMove(board.zhash,move);
}

void OpeningBook::appendMove(size_t zhash, SingleMove& move){
	(*this)[zhash].push_back(move);
}

/* ------------------  IO  ------------------- */

void OpeningBook::loadBookFromFile(){
	loadBookFromFile("./openingBook.txt");
}

void OpeningBook::loadBookFromFile(string fileName){
	ifstream file(fileName);
	//cout << "loading: " << fileName << endl;
	
	int lineCount = 0;//for giveing useful errors
	string line;
	while(getline(file, line)) {
		lineCount++;
		if(line.length() < 4 || line[0] == '#'){
			continue;
		}
		try{
			this->parseLine(line);
		} catch (char e){
			switch(e){
				case 'm':
				case 's':
					cerr << lineCount << ')' << endl;
					break;
				
				default:
					cerr << "An unknown error was encountered: Aborting!" << endl;
					throw e;
			}
		}
	}
	
	file.close();
}

void OpeningBook::parseLine(string line){
	const char* p = line.c_str();
	int len = line.length();
	int source = -1;
	int dest = -1;
	char isWhite = 1;
	
	transform(line.begin(), line.end(), line.begin(), ::toupper);
	
	ChessBoard curBoard = ChessBoard();
	curBoard.setupGame();
	curBoard.recalculateZhash(1);
	
	SingleMove* move = new SingleMove(0,0);
	int moveIndex;
	while(len >= 4){
		
		if(   p[0] <= 72 && p[0] >= 65 && p[2] <= 72 && p[2] >= 65 &&
		      p[1] <= 56 && p[1] >= 49 && p[3] <= 56 && p[3] >= 49){
			source = ((56-p[1])*8)+p[0]-65;
			dest =   ((56-p[3])*8)+p[2]-65;
		} else {
			cerr << "The move: \033[31m" << p[0] << p[1] << p[2] << p[3] 
			     << "\033[0m on the line \033[33m\n" << line << "\n\033[0mDoes not follow a valid structure. (Line: ";
			throw 's';
		}
		
		vector<SingleMove> PossibleMoves;
		PossibleMoves.reserve(45);
		
		//generate all possible moves for the given source square
		curBoard.addSquareMoves(PossibleMoves,source);
		curBoard.trueValidMoves(PossibleMoves,isWhite);
		moveIndex = curBoard.moveInVector(PossibleMoves,source,dest);
		if(moveIndex == -1){
			cerr << "The move: \033[31m" << p[0] << p[1] << p[2] << p[3] 
			     << "\033[0m on the line \033[33m\n" << line << "\n\033[0mIs not a valid move for ";
			if(isWhite){
				cerr << "white";
			} else {
				cerr << "black";
			}
			cerr << ". (Line: ";
			throw 'm';//move impossible
		}
		
		delete move;
		move = new SingleMove(PossibleMoves[moveIndex]);
		
		
		if(this->contains(curBoard.zhash)){
			this->appendMove(curBoard.zhash,*move);
		} else {
			this->add(curBoard.zhash,*move);
		}
		
		curBoard.updateZhashForMove(*move);
		curBoard.performMove(*move);
		
		len -= 5;
		p += 5;
		isWhite = !isWhite;
	}
}


















