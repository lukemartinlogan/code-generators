keywords = """
alignas (C++11)
alignof (C++11)
and
and_eq
asm
atomic_cancel (TM TS)
atomic_commit (TM TS)
atomic_noexcept (TM TS)
auto (1)
bitand
bitor
bool
break
case
catch
char
char8_t (C++20)
char16_t (C++11)
char32_t (C++11)
class (1)
compl
concept (C++20)
const
consteval (C++20)
constexpr (C++11)
constinit (C++20)
const_cast
continue
co_await (C++20)
co_return (C++20)
co_yield (C++20)
decltype (C++11)
default (1)
delete (1)
do
double
dynamic_cast
else
enum
explicit
export (1) (3)
extern (1)
false
float
for
friend
goto
if
inline (1)
int
long
mutable (1)
namespace
new
noexcept (C++11)
not
not_eq
nullptr (C++11)
operator
or
or_eq
private
protected
public
reflexpr (reflection TS)
register (2)
reinterpret_cast
requires (C++20)
return
short
signed
sizeof (1)
static
static_assert (C++11)
static_cast
struct (1)
switch
synchronized (TM TS)
template
this (4)
thread_local (C++11)
throw
true
try
typedef
typeid
typename
union
unsigned
using (1)
virtual
void
volatile
wchar_t
while
xor
xor_eq
""".strip()

lines = keywords.splitlines()
cpp0 = []
cpp11 = []
cpp17 = []
cpp20 = []
cpp23 = []

for line in lines:
    if '(C++11)' in line:
        cpp11.append(line.split()[0])
    elif '(C++17)' in line:
        cpp17.append(line.split()[0])
    elif '(C++20)' in line:
        cpp20.append(line.split()[0])
    elif '(C++23)' in line:
        cpp23.append(line.split()[0])
    else:
        cpp0.append(line.split()[0])

print(f"self.cpp0 = {cpp0}")
print(f"self.cpp11 = self.cpp0 + {cpp11}")
print(f"self.cpp17 = self.cpp11 + {cpp17}")
print(f"self.cpp20 = self.cpp17 + {cpp20}")
print(f"self.cpp23 = self.cpp20 + {cpp23}")