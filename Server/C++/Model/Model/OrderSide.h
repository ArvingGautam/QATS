#pragma once
#include<string>
namespace QATS {
	namespace Model
	{
		class OrderSide
		{
		public:
			typedef enum {
				Undefined = -1,
				Buy = 1,
				Sell = 2,
				SellShort = 3
			} Value;
			static std::string toString(Value value);
		};
	}
}