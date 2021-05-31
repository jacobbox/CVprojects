#ifndef __CHESS__
#define __CHESS__ 1

/*-----------------includes-----------------*/
#include<iostream>
#include<vector>
#include<chrono>
#include<string>

#include<stdio.h>

#include "SingleMove.hpp"
#include "ChessBoard.hpp"
#include "Node.hpp"
#include "Ttable.hpp"
#include "OpeningBook.hpp"
#include "ChessAI.hpp"

/*----------------Prototypes----------------*/

/* ------ UI functions ------ */

void show_menu();
void redraw_menu();

char isValidFEN(std::string);

/* ------ TESTING! ------ */
/* === Position reached testing === */
int positionReachedTest(ChessBoard&,char);
int positionReachedTest(ChessBoard&,char,char);
int positionReachedTest(ChessBoard&,char,char,char);

void runPositionReachedDepthTest(ChessBoard&,char);
void runPositionReachedDepthTest(ChessBoard&,char,int);

void runPositionReachedBenchmarkTest(ChessBoard&, char, int);
void runPositionReachedBenchmarkTest(ChessBoard&, char, int, int);
void runPositionReachedBenchmarkTest(ChessBoard&, char, int, int, int);

void runAllPositionReachedBenchmarkTest();

/* === supporting === */
std::string prepend0(std::string,int);
std::string commafy(unsigned long long int);

/* === best-move-testing === */
void runBestMoveBenchmarkTest(ChessBoard&, char, int);

void runAllBestMoveBenchmarkTests();

#endif
