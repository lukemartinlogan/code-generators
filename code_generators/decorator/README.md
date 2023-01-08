# Decorator

A framework for generating code by parsing decorated functions in a C++
header file. Can only have one decorator per-function.

# Example 

Let's say we have an RPC decorator. 
```cxx
// hello.h
#define RPC

namespace test {

class hello {
 private:
    int num_nodes_, node_id_;
    
 public:
    RPC void LocalHello(int x, int y);
    
    #include "autogen/_hello.h"
};

}
```

We can parse this C++ text and generate the corresponding global RPC
```cxx
// autogen/_hello.h

void GlobalHello(int x, int y) {
    if ((x+y) % num_nodes_ == node_id) {
      LocalHello(x, y);
    } else {
      CallRpc<void>("hello_rpc", x, y);
    }
}
```

This avoids having to create the "Global" function for each corresponding
"Local" function.