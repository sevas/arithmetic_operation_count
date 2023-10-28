import pytest
import pycparser
from count_ops.c_lang import make_opcount_tree, OpCount, get_loop_range, range_to_count
from count_ops.common import OpCountNode, count_from_tree, strip_comments


def test_simple_expression():
    code = """
int main(){
    int a = 12 * 2 + 3 + 2 * (2 * 5);
    return 0;
}
"""
    expected = OpCount(mul=3, add=2)
    parsed = pycparser.CParser().parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert count_from_tree(oc_tree) == expected


def test_count_loop_steps():
    code = """
int main(){
    int res = 0;
    for(int i= 0; i < 10; i++){
        res = res + i;
    }
    return 0;
}
"""
    parsed = pycparser.CParser().parse(code)
    for_node = parsed.ext[0].body.block_items[1]
    loop_range = get_loop_range(for_node)
    assert loop_range == (0, 10, 1)


def test_loop_with_constant():
    code = """
int main(){   
    int res = 0;
    for(int i= 0; i < 10; i++){
        res = (2*res) + i;
    }
    return 0;
}
    """
    expected = OpCount(mul=10, add=10)
    parsed = pycparser.CParser().parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert count_from_tree(oc_tree) == expected


def test_nested_loops_with_constant():
    code = """
int main(){   
    int res = 0;
    for(int i= 0; i < 10; i++){
        for(int j= 0; j < 20; j++){
            res = (i*res) + j;
        }
    }
    return 0;
}
    """
    expected = OpCount(mul=200, add=200)
    parsed = pycparser.CParser().parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert count_from_tree(oc_tree) == expected


def test_simple_ifelse():
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
    expected = OpCount(mul=0, add=1)
    parsed = pycparser.CParser().parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert count_from_tree(oc_tree) == expected