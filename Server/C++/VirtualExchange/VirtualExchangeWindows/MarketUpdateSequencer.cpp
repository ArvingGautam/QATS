#include "pch.h"
#include <stdio.h>
#include <cstdlib>
#include <stdexcept>
#include <map>
#include <memory>
#include <atomic>
#include <set>
#include <unordered_map>
using namespace std;
/* Market data is coming with Sequence_Id and Last Trade Price
Some sequence could be missing, so you need to wait until the missing sequence arrives. 
Once sequence arrives, you need to flush all pending messages to client.
e.g . 
1. {1, 10.3}
prints {1, 10.3}
2. {4, 10.5}
3. {6, 10.7}
4. {3, 10.4}
for above 3 messages prints nothing, wait as sequence 2 is still missing
5. {2, 10.6}
prints {2, 10.6}, {3, 10.4}, {4, 10.5}
6. {8, 10.8} - prints nothing, wait as sequence 5, 7 is still missing
7. {5, 10.4} 
prints {5, 10.4}, {6, 10.7}
*/