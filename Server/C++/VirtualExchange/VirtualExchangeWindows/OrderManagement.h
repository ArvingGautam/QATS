#pragma once
#include "../../Model/Model/Order.h"

FORWARD(QATS, Model, Order)

namespace QATS
{
	namespace VirtualExchange {
		class OrderManagement
		{
			public:
				bool SendOrder(QATS::Model::Order order);
		};
	}
}