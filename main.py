import pycparser

from count_ops.c_lang import make_opcount_tree
from count_ops.common import print_tree, count_from_tree

code = """
int main(){

    int res = 0;
    if (res == 0){
        res = res + 2;
    }
    else if (res == 1){
        res = res + 3 + 2;
    }
    else{
        res = res + 4 + 2 +3;
    }

    return 0;
}
"""

# code = """
# int main(){
#     int a = 12 * 2 + 3 + 2 * (2 * 5);
#     return 0;
# }
# """


def main():
    p = pycparser.CParser()
    parsed = p.parse(code)

    parsed = p.parse(strip_comments(code))

    # print(parsed)
    oc_tree = make_opcount_tree(parsed)
    print_tree(oc_tree)
    print(count_from_tree(oc_tree))


if __name__ == '__main__':
    main()
