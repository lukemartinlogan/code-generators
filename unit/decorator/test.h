namespace hello {

class test {
 public:
  TEST void LocalHi(int x, int y);
  TEST void LocalLo(std::vector<int> y);

  #include "_test.h"
};

}  // namespace hello