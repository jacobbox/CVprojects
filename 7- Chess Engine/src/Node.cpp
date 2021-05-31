#include "Node.hpp"

using namespace std;

/*
 * Make the return node
 */
Node::Node(SingleMove& sourceMove,int sourceVal,int sourceDepth) : move(sourceMove){
	this->value = sourceVal;
	this->depth = sourceDepth;
}

/*
 * Add stream support
 */
ostream& operator<<(ostream& os, const Node& nd)
{
	os << "NODE(" << nd.move << "," << nd.value << ")";
    
    return os;
}




