"""
Provides counting funcs and operators from advMath module

"""

def list_prod(p):
    """
    Returns product of a list p.

    Func is used in various counting funcs, such as adv_prod.
    """
    prod=1
    for i in p:
        prod*=i
    return prod

def factorial(n):
    """
    Returns a product of first n units
    """
    if n==0:
        return 1
    return n*factorial(n-1)

def powers_factorial(n,power):
    """
    Returns the product of factorial(n,power-1); n in range[1,n]
    For example:

        powers_factorial(3,2) = powers_factorial(1,1) * powers_factorial(2,1) * powers_factorial(3,1) = 
        = 1! * 2! * 3! = 12

        powers_factorial(3,3) = ... = 1!super * 2!super * 3!super = 24

    General formula for powers_factorial(n,power):

        powers_factorial(n,power) = adv_prod(1,n,powers_factorial(i,power-1))

    The most convenient range for power is [1,5]
    """
    if n==0:
        return 1
    if power == 1:
        return n*factorial(n-1)
    return powers_factorial(n,power-1)*powers_factorial(n-1,power)

def double_factorial(n):
    """
    double factorial of n (n!!) is a version of factorial where:
    if n is even:
        8!! = 2*4*6*8 = 384
    if n is odd:
        7!! = 1*3*5*7 = 105
            
    """
    if n==0:
        return 1
    def even_factorial(n):

        #NON-RECURSIVE METHOD

        """def factorial(n):
            if n==1:
                return 1
            return n*factorial(n-1)
        
        def denominator(n):
            if n==1:
                return 1
            odd_part = []
            for i in range(1,n+1):
                if i%2==1:
                    odd_part.append(i)
            return list_multiply(odd_part)
        return factorial(n)//denominator(n)"""

        #RECURSIVE METHOD

        if n == 2:
            return 2
        
        def last_even(n):
            evens=[]
            for j in range(1,n+1):
                if j%2==0:
                    evens.append(j)
            if evens==[]:
                return None
            return evens[-1]
        
        for i in range(n,1,-1):
            if last_even(i)==last_even(i-1):
                continue
            else:
                if n==3:
                    return even_factorial(2)
                return last_even(i)*even_factorial(i-1)
            
    def odd_factorial(n):
        """
        odd_factorial(n) = factorial(n)/even_part(n)
        """
        if n==1:
            return 1
        def list_multiply(p):
            ending_multiply=1
            for i in range(len(p)):
                ending_multiply*=p[i]
            return ending_multiply
        def denominator(n):
            evens=[]
            for j in range(1,n+1):
                if j%2==0:
                    evens.append(j)
            return list_multiply(evens)
        return factorial(n)//denominator(n)
    if n%2==0:
        return even_factorial(n)
    return odd_factorial(n)

def primorial(n):
    """
    Primorial function (n#) returns the product of first n prime units.
    For example:

       1) 5# = 2*3*5*7*11 = 2310
    
    On the other hand, func can be represented as product of first n prime units:

       2) 5# = 2*3*5 = 30

    The first defintion of primorial func always
    returns different results with different args:

        list(map(primorial, [0, 1, 2, 3, 4, 5, 6])) = [1, 2, 6, 30, 210, 2310, 30030]

    In the second defintion of primorial some results are repeated with different args,
    because, for example, for args 7,8,9 and 10, last prime unit in product
    is 7 ==> all products for this args are equal.

        list(map(primorial, [1, 2, 3, 4, 5, 6, 7, 8, 9])) = [1, 2, 6, 6, 30, 30, 210, 210, 210] 

    This func uses second algorithm. To use the first algorithm,
    instead of n input prime(n) as an arg. Or you can use adv_prod(1,n,"prime(i)")

    To check if num n is prime we have to check if div_sigma(n,0,0) == 2,
    which means that n has only 2 dividers (More info in div_sigma(num,power,aliquocy) desc.)

    """
    #NON-RECURSIVE METHOD
    
    prime=[j for j in range(2,n+1) if is_prime(j)]

    return list_prod(prime)

    #RECURSIVE METHOD (not practically rational)
    if n==1 or n==0:
        return 1
    if n==2:
        return 2
    
    def last_prime(n):
        prime=[]
        for j in range(2,n+1):
            if div_sigma(j,0,0)==2:
                prime.append(j)
        return prime[-1]
    
    for i in range(n,2,-1):
        if last_prime(i)==last_prime(i-1):
            continue
        else:
            return last_prime(i)*primorial(i-1)

def any_factorial(n,mode):
    """
    Modes:

        default: returns factorial(n)
        
        prime, primorial, p: return primorial(n)
        
        double: returns double_factorial(n)
        
        compositorial, composite, c: return factorial(n) // primorial(n) (product of first n composite nums)
        
        super, s: return powers_factorial(n,2)
        
        multi/print, m/p, m/print: return all factorials to be printed
        
        multi/list, m/l: return list of all factorials (results only)

        multi/dict, m/dict: return dictionary containing all factorial results with keys

    """
    k=0
    if mode == "default":
        k = factorial(n)

    elif mode == "prime" or mode == "primorial" or mode == "p":
        k = primorial(n)

    elif mode == "double":
        k = double_factorial(n)

    elif mode == "compositorial" or mode == "composite" or mode == "c":
        k = factorial(n) // primorial(n)

    elif mode == "super" or mode  == "s":
        k = powers_factorial(n,2)

    elif mode == "m/p" or mode == "m/print" or mode == "multi/print":
        k= f"""{n}! = {factorial(n)},
{n}!! = {double_factorial(n)},
{n}# = {primorial(n)},
{n}!/# = {factorial(n) // primorial(n)},
{n}!super = {powers_factorial(n,2)}.
-----"""
    elif mode == "multi/list" or mode == "m/l":
        k = [factorial(n), double_factorial(n), primorial(n), factorial(n) // primorial(n), powers_factorial(n,2)]

    elif mode=="multi/dict" or mode == "m/dict":
        k = {"default": factorial(n),
"double": double_factorial(n),
"primorial": primorial(n),
"compositorial": factorial(n) // primorial(n),
"super": powers_factorial(n,2)}
    return k


def sqrt_eq(a,b,c,mode):
    """
        Quadratic equation must be presented as a*x**2 + b*x + c = 0
        where a, b and c are indexes; x is an unknown value
        that programm will find
        using discriminant method (D = b^2 - 4ac).

        Modes:
        list/l: return a list with roots
        print/p: return the answers to be printed in terminal
    """
    def sqrt(d):
        return float(d**0.5)
    solutions = []
    print_roots=0
    d = (b**2) - (4*a*c)
    if d > 0:
        solutions.append(((-b) + sqrt(d)) / (2*a))
        solutions.append(((-b) - sqrt(d)) / (2*a))
        print_roots =  f"""
x1 = {solutions[0]} ,
x2 = {solutions[1]} .
"""
    elif d == 0:
        solutions.append((-b) / (2*a))
        print_roots = f"""
x = {solutions[0]}.
"""
    elif d < 0:
        print_roots = """
No roots can be found for this equation"""

    if mode == "print" or mode == "p":
        return print_roots
    elif mode == "list" or mode == "l":
        return solutions

def root(n,power):
    """
    Returns root of n in any root power
    """
    return n**(1/power)


def int_sum(power,n):

    """ 
        The Σ(n) function summarizes all units before n: 1 + 2 + 3 + ... + n .
        It also can be represented by n*(n+1)/2 formula, which return n-th unit of triangle numbers sequence.

        By increasing the power of Σ(n) func to 2 we proceed to ΣΣ(n) func,
        which summarizes sums of units: Σ(1) + Σ(2) + Σ(3)+ ... + Σ(n)
        So ΣΣ(n) = n*(n+1)*(n+2)/6
        which returns n-th unit of tetrahedral numbers sequence

        The general formula for Σ(power, n) = ((power + n)! // (n - 1)!) // (power + 1)!

    RETURNS:

        n-th unit of (power+2)-th sequence of Pascal triangle: pre-ordinal (just 1 with any n value), ordinal, triangle, tetrahedral, pentatopic, etc.

    ARGS:
    
        power of Σ()
        n (position)         
            
    """
    
    k = (factorial(power + n) // factorial(n - 1)) // factorial(power + 1)

    return k

def div_sigma(num,power,aliquocy):
    """
    div_sigma() can be characterized as sum of dividers of number.
    For example:

        div_sigma(12,1,0) = i[1]^1 + i[2]^1 + i[3]^1 + ... + i[n]^1 =
        = 1 + 2 + 3 + 4 + 6 + 12 = 28, where 12 % i[any] = 0, n is quantity of dividers.

    This example shows us the return of div_sigma() where power equals 1 and aliquocy is 0
    which means that we have to make sure that the number itself is added to the ending sum,
    Evidently, if aliquocy equals 1, we must subtract this number from ending sum

    The power of div_sigma() defines what power each unit of sum will be raised to.

    Main properties:

    1) If the number n  is prime (e.g 7) then it has only 2 dividers (1 and n),
    So, sum of prime number dividers equals n+1:

        div_sigma(7,0,0) = 1^0 +7^0 = 1 + 1 = 2 (power = 0 ==> returns the quantity of dividers)

        div_sigma(7,1,0) = n + 1 = 7 + 1 = 8  

    2) if prime n is raised to the power x then div_sigma(n^x,0,0) = x + 1:

        div_sigma(7^2,0,0) = 1^0 + 7^0 + (7^2)^0 = 2 + 1 = 3
    
    """
    ending_sum=sum([d**power for d in range(1,num+1) if num%d==0])
    if aliquocy==1:
        ending_sum-=num**power
    return ending_sum

def sigma(start,end,rule,environ = None):
    """
    Apart of int_sum(power,n) this func gives an ability for
    summing processes to be defined by certain rules. Also, starting and ending values can be given
    For example:

    if starting value equals 4, ending one is 6, the rule is i+2 (must be a str
    which contains i as a value in range [start,end])
    then the result will be:

        sigma(4,6,i+2) = (4+2) + (5+2) + (6+2) = 6+7+8 = 21

    The opportunity to create non-int formulas proves that this func is more common for educational purposes
    than adv_sigma(start,end,rule,power)

    RESTRICTIONS:

        1) No support for  functions and variables in rules:
            In terms of security, all functions and variables which were defined outside
            supOperators module file are prohibited to be used in rule formula.

        2) No iteration support for variables in rules
    """
    ending_sum = sum([eval(rule,environ) for i in range(start,end+1)])
            
    return ending_sum    
k = sigma(1,8,"div_sigma(i,0,0)",globals())
print(k)
def adv_prod(start,end,rule):
    """
    Returns product of each rule with i in range[start,end].
    Basically, a factorial func,
    but with extensions similar to those which sigma() func has (starting, ending values; rule formula)
    For example:

        adv_prod(4,6,i/2) = 4/2 * 5/2 * 6/2 = 2 * 2.5 * 3 = 15

    Advanced example with primorials:

        primorial(prime(n)) = adv_prod(0, n, prime(i))

    """
    def list_prod(n):
        ending_prod=1
        for i in n:
            ending_prod*=i
        return ending_prod
    ending_seq=1    
    all_values_in = [i for i in range(start,end+1)]
    ending_seq = list_prod(list(map(lambda i: eval(rule),all_values_in)))
    #ending_seq = list_prod([eval(rule) for i in all_values_in]) is the same thing
    return ending_seq

def adv_sigma(start,end,rule,power):
    """
        Advanced version of sigma(start,end,rule) func, where powers can be added to summing processes
        For example:

        if starting value equals 4, ending one is 6, the rule is i+2 (must be a str
        which contains i as an unknown value) and power of func is 2
        then the result will be:

                adv_sigma(4,6,i+2,2) = sigma(1,4+2) + sigma(1,5+2) + sigma(1,6+2) = 21+28+36 = 85

    RESTRICTIONS:

        1) Only integer rule formulas (int with i in [start,end]) <==> only int results

            Due to the fact that sum of integers (used in int_sum(power,n)) can't equal to non-int,
            it is impossible to represent the sum of rules with i in range[start,end] as a float num, because
            of the general sigma(power,n) formula, where factorials are heavily used:

                factorial(n(float,any)) ==> RecursionError (doesn't exist) 

        2) Only inner functions in rules:
            We are working on the issue that eval() function cannot accept custom functions which are
            defined outside the supOperators module file.
            You can still use inner functions such as sigma() as they are defined inside this module
        
    """

    ending_sum=0
    #ending_sum = sum(map(lambda i: int_sum(power-1, eval(rule)), range(start,end+1)))
    ending_sum = sum([int_sum(power-1,eval(rule)) for i in range(start,end+1)])
    return ending_sum


def prime_quantity(n):
    """
    Returns the quantity of prime numbers <= arg
    
    """
    k=0
    i=0
    if n==1 or n==0:
        return 0
    
    for i in range(1,n+1):
        if div_sigma(i,0,0)==2:
            k+=1
    return k

def is_perfect(n):
    """
    Checks if arg is a perfect num

    RESTRICTIONS:

        Not optimal for large args (n>100_000_000)
    """
    if div_sigma(n,1,1) == n:
        return True
    return False

def is_prime(n):
    """
    Checks if arg is prime num

    RESTRICTIONS:

        Not optimal for large args (n>100_000_000)
    """
    if div_sigma(n,0,0)==2:
        return True
    return False

def divs(n):
    """
    Returns a list containing dividers of arg
    """
    dividers_list = [i for i in range(1,n+1) if n%i==0]
   
    return dividers_list

def perfect_formula(n):
    """
    Returns 2^n*(2^(n+1)-1)
    With help of this formula, each known perfect number can be calculated.

    WARNING: 

        Formula can return a perfect num but not with each arg value:
            1) 2^1*(2^2-1) = 6 (perfect)
            2) 2^2*(2^3-1) = 28 (perfect)
            3) 2^3*(2^4-1) = 120 (not perfect!!!)
            4) 2^4*(2^5-1) = 496 (perfect)
            ...
        True method to calculate n-th perfect num hasn't yet been found!
         
    """
    k = 2**n*(2**(n+1)-1) #all known perfect nums can fit in this formula 
    return k
    #formula 2**n*(2**(n+1)-1) contains n, so each perfect num could be calculated through it
    #The only issue is that some result nums coming from this formula are not perfect

def phib(n):
    """
    Return n-th number from Phibonacchi sequence.
    All nums from this sequence are equal to the sum of two previous ones:

        [phib(i) for i in range(1,12)] = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    """
    if n==1:
        return 1
    if n==2:
        return 1
    return phib(n-2)+phib(n-1)

def perfect(n):
    """
    True method to calculate n-th perfect num hasn't yet been found!

    Func is awaited to return n-th perfect number:
        perfect(1) = 6.

        perfect(2) = 28.

        perfect(3) = 496.

        perfect(4) = 8128.
    """
    return None
     
def prime(n):
    """
    Returns n-th prime number.
    By using primorial(prime(n)) we can get n# sequence without repeating returns:

        [primorial(prime(n)) for n in range(7)] = [1, 2, 6, 30, 210, 2310, 30030]
        [primorial(n) for n in range(7)] =  [1; 1; 2; 6; 6; 30; 30]

    RESTRICTIONS:
        Not optimal for n > ~1000
        The only known simple method to find n-th prime is div_sigma() check method.
        It can be convenient when difference between each unit in sequence is not very large:

            [prime(i) for i in range(1,10)] = [2,3,5,7,11,13,17,19,23] ==>
            difference is optimal: div_sigma() method is convenient (for n < ~1000)

            [perfect(i) for i in range(1,4)] = [6,28,496,8128] ==>
            difference is too large: div_sigma() check is not an appropriate method
    """
    if n==0:
        return 1
    primes=0
    k=0
    i=0
    while k<n:
        i+=1
        if is_prime(i):
            k+=1
            primes = i
    return primes

def type_sort(p):
    """
    Returns a dict in which primes and composite values from list
    are sorted. 
    For example:

        type_sort([1,2,7,4,9,11,11]) = {'primes': [2, 7, 11], 'composite': [4, 9], 'None': [1]}
 
    """
    results = {}
    primes=[]
    composite=[]
    none=[]
    for i in p:
        if is_prime(i):
            if i not in primes:
                primes.append(i)
        elif i == 1 or i == 0:
            if i not in none:
                none.append(i)
        else:
            if i not in composite:
                composite.append(i)
    results = {"primes": primes, "composite": composite, "None": none}
    return results