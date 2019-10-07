#include<string>
#include "OrderSide.h"
#include "Util.h"
#pragma once

FORWARD(QATS, Model, OrderSide)

namespace QATS {
	namespace Model
	{
		class Order
		{
		public:
			Order();
			virtual ~Order();
			const long& getQuantity() const;
			const std::string& getInstrumentId() const;
			const std::string& getAccount() const;
			const OrderSide& getOrderSide() const;

			void setQuantity(const long& quantity);
			void setInstrumentId(std::string&& instrumentId);
			void setAccount(std::string&& account);
			void setOrderSide(OrderSide&& side);
		private:
			std::string _orderId;
			std::string _instrumentId;
			std::string _account;
			OrderSide _side;
			long _quantity;
		};
	}
}