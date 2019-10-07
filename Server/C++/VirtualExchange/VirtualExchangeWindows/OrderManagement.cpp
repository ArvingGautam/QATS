#include "pch.h"
#include "OrderManagement.h"
#include "../../Model/Model/Order.h"

FORWARD(QATS, Model, Order)

namespace QATS
{
	namespace VirtualExchange {		
		bool OrderManagement::SendOrder(QATS::Model::Order order)
		{
			return true;
		}
	}
}