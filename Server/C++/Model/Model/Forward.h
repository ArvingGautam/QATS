#pragma once

#define FORWARD1(ns1, className)  namespace ns1 { class className; }

#define FORWARD2(ns1, ns2, className) namespace ns1 { FORWARD1(ns2, className) }

#define FORWARD3(ns1, ns2, ns3, className) namespace ns1 { FORWARD2(ns2, ns3, className) }

#define FORWARD4(ns1, ns2, className) namespace ns1 { FORWARD3(ns2, ns3, ns4, className) }

#define FORWARD(ns1, ns2, className) FORWARD2(ns1, ns2, className)

#define FORWARD_STRUCT(ns1, ns2, structName) namespace ns1 { namespace ns2 { struct structName; } }
