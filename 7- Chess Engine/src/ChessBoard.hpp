#ifndef __CHESSBOARD__
#define __CHESSBOARD__ 1



/*-------------------Notes------------------*/
/*

	Upper case = while
	lower case = black
	
	RNBQKBNR 

*/
/*-----------------includes-----------------*/
#include<algorithm>
#include<iostream>
#include<vector>
#include<string>
#include<utility>

#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include "SingleMove.hpp"
#include "Node.hpp"


/*----------------prototypes----------------*/


/*-----------------classes------------------*/


class ChessBoard{
	private:
		//boards
		static char blankBoard[65];
		static char baseBoard[65];
		static int baseWhiteIndexs[64];
		static int baseBlackIndexs[64];
		//matrixes
	public:
		static int kingEndMap[65];
		static int knightMap[65];
		static int kingMidMapW[65];
		static int kingMidMapB[65];
		static int rookErlMapW[65];
		static int rookErlMapB[65];
		static int pawnMapW[65];
		static int pawnMapB[65];
		static int MatinglineBN_Wb[65];
		static int MatinglineBN_Bb[65];
		static int pawnPromoMapW[65];
		static int pawnPromoMapB[65];
	private:
		//Consts
		static size_t zhashnums[781];
		/* === CONSTANT GENERATION === */
		static int _unused_number_created_to_setVars;
		//supporting functions
		void applyOffset(std::vector<SingleMove>&, int, int, int, int, char, int);
	public:
		int moveInVector(std::vector<SingleMove>&, int, int);
		int moveInVector(std::vector<SingleMove>&, int, int, char);
		
		//Public atributes
		char board[65];
		//speed up vars:
		int whiteIndexs[64];
		int blackIndexs[64];
		char whitePcCount = 0;
		char blackPcCount = 0;
		char whiteKingLoc = -1;
		char blackKingLoc = -1;
		
		
		int en_pass_index = -1;
		int wck = 0;
		int wcq = 0;
		int bck = 0;
		int bcq = 0;
		
		size_t zhash = 0;
		
		
		//Constructors
		ChessBoard();
		ChessBoard(const ChessBoard&);
		
		
		//Board manipulation
		void setBoard(char[]);
		void setBoard(ChessBoard&);
		void cloneBoard(ChessBoard&);
		char loadFromFen(std::string);
		void reset();
		void empty();
		//New Piece manipulation
		void removePiece(char);
		void removePiece(char,char);//if colour of removed piece known
		void addPiece(char,char);
		void addPiece(char,char,char);//if colour of added piece known
		
		void blindMove(SingleMove&);
		void blindMove(SingleMove&,char);
		void blindMove(int,int);
		void blindMove(int,int,char);
		
		void setSquare(int,char);
		void setSquare(std::string,char);
		
		//evaluation
		std::pair<int,int> getPointsOnBoard();
		int courseValue();
		void addSquareMoves(std::vector<SingleMove>&, int);
		void addSquareMoves(std::vector<SingleMove>&, int, char);
		void getAllSideMoves(std::vector<SingleMove>&, char);
		void getAllSideMoves(std::vector<SingleMove>&, char, char);
		char isSquareCheck(char,char);
		
		//user evaluation
		void trueValidMoves(std::vector<SingleMove>&, char);
		char isCheckMate(char);
		char isDrawn();
		std::string getSideRemainingPieces(char);
		
		
		//TTableing
		int getZhashpcIndex(char);
		void recalculateZhash(char);
		void updateZhashForMove(SingleMove&);
		
		//IO
		void show();
		void show(char);
		void show(char,int);
		void show(char,int,char);
		void flags();
		SingleMove* parseRequest(std::string, char);
		SingleMove* parseRequest(std::string, char, char);
		
		//game commands
		
		void setupGame();
		void performMove(SingleMove&);
		void beginGame();
		void beginGame(char);
		void beginGame(char,char);
		void beginGame(char,char,char);
		void beginGame(char,char,char,int);
	
		
};

#endif
