import pycparser

from count_ops.c_lang import count_ops

code = """
int main(){
    
    int res = 0;
    if (res == 0){
        res = res + 2;
    }
    else{
        res = res + 3;
    }
    
    return 0;
}

"""

def main():
    p = pycparser.CParser()
    parsed = p.parse(code)

    print(parsed)
    print(count_ops(parsed))



if __name__ == '__main__':
    main()
