// VirtualExchangeWindows.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include "pch.h"
#include <iostream>
#include "OrderManagement.h"
#include "../../Model/Model/Order.h"
#include "../../Model/Model/Order.h"


FORWARD(QATS, VirtualExchange, OrderManagement)
FORWARD(QATS, Model, Order)

int main1()
{
	QATS::VirtualExchange::OrderManagement orderManagement;
    std::cout << "Hello World!\n"; 
	QATS::Model::Order order;
	orderManagement.SendOrder(order);
	return 0;
}
