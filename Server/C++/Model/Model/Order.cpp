#include "stdafx.h"
#include "Order.h"

namespace QATS {
	namespace Model
	{
		Order::Order()
		{
		}
		Order::~Order()
		{
		}
		const long & Order::getQuantity() const
		{
			return _quantity;
		}
		const std::string & Order::getInstrumentId() const
		{
			return _instrumentId;
		}
		const std::string & Order::getAccount() const
		{
			return _account;
		}
		const OrderSide & Order::getOrderSide() const
		{
			return _side;
		}
		void Order::setQuantity(const long & quantity)
		{
			_quantity = std::move(quantity);
		}
		void Order::setInstrumentId(std::string && instrumentId)
		{
			_instrumentId = std::move(instrumentId);
		}
		void Order::setAccount(std::string && account)
		{
			_account = std::move(account);
		}
		void Order::setOrderSide(OrderSide && side)
		{
			_side = std::move(side);
		}
	}
}