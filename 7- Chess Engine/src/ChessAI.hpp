#ifndef __CHESSAI__
#define __CHESSAI__ 1

/*-----------------includes-----------------*/
#include<vector>
#include<algorithm>
#include<utility>
#include<chrono>
#include<iomanip>

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "SingleMove.hpp"
#include "ChessBoard.hpp"
#include "Node.hpp"
#include "Ttable.hpp"
#include "OpeningBook.hpp"
#include "Rlist.hpp"

/*----------------Prototypes----------------*/

/*===============DEBUG======================*/
void resetNodeAiVisitCount();
int getNodeAiVisitCount();

void resetBMtimes();
void showBMtimes();

/*===============Main======================*/
static void showProgBar(int, int);

Node* renderBestMove(ChessBoard&,char,int);
Node* renderBestMove(ChessBoard&,Rlist&,char,int);
Node* renderBestMove(ChessBoard&,Rlist&,char,int,char);

int deviseNodeValue(ChessBoard&,Rlist&,Rlist&,char,Ttable&,int,int);
int deviseNodeValue(ChessBoard&,Rlist&,Rlist&,char,Ttable&,int,int,char);
int deviseNodeValue(ChessBoard&,Rlist&,Rlist ,char,Ttable&,int,int,char,int,int);//alpha beta
//                                          ^ Not by reffrence: very important!

/*===============Supporting======================*/

void sequenceMoves(ChessBoard&,std::vector<SingleMove>&, Ttable&, char);

#endif
