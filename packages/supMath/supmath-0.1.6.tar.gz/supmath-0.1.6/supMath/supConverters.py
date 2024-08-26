"""
Provides converting formulas from advmath module.

"""
def convert(num,scale_base):
    """
    Converts decimal number to any scale of notation
    """
    k=''
    while num>0:
        unit = num%scale_base
        if unit>9:
            unit = chr(55+unit)
        k+=str(unit)
        num//=scale_base
    return k[::-1]

def bin_digits_switch(k):
    """
    Switches all binary digits in num: 
        11010 ==> 00101 ==> 101
    """
    k=k.replace("1","o").replace("0","i").replace("o","0").replace("i","1")
    return k

def lb_to_kg(lb):
    return lb*0.453592

def kg_to_lb(kg):
    return kg*2.204623

def cel_fah(c):
    return (1.8*c)+32

def fah_cel(f):
    return (5/9)*(f - 32) 