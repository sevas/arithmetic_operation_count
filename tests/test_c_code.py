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
    assert expected == count_from_tree(oc_tree)


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


def test_count_ops_in_func_params():
    code = """
    int main(){
        int x = 2;
        int y = 4;
        
        float res = sqrt(x*x + y*y);
        return 0;
    }
    """
    expected = OpCount(mul=2, add=1)
    parsed = pycparser.CParser().parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert expected == count_from_tree(oc_tree)


def test_image_processing_example():
    code = """
    int main() {
        float input_image[240*320];
        float output_image[240*320];
        
        // comment out initialization to avoid unary ops to be counted. This should be a constant array
        float kx[3*3]; // = {-1, 0, 1, -2, 0, 2, -1, 0, 1};
        float ky[3*3]; // = {-1, -2, -1, 0, 0, 0, 1, 2, 1};
    
        for (int i = 1; i < 239; i++) {                                     // 238 steps
            for (int j = 1; j < 319; j++) {                                 // 318 steps
                int idx = i * 320 + j;                                      //   1 add, 1 mul
                float x_val = 0.f;
                float y_val = 0.f;
                for (int ki = 0; ki < 3; ki++) {                            //   3 steps
                    for (int kj = 0; kj < 3; kj++) {                        //   3 steps
                        int kidx = ki * 3 + kj;                             //     1 add, 1 mul
                        int idx2 = (i + ki - 1) * 320 + (j + kj - 1);       //     5 add, 1 mul
                        x_val += input_image[idx2] * kx[kidx];              //     1 add, 1 mul
                        y_val += input_image[idx2] * ky[kidx];              //     1 add, 1 mul
                    }   
                }
                output_image[idx] = sqrt(x_val * x_val + y_val * y_val);    //   1 add, 2 mul
            }
        }
        return 0;
    }
    """
    expected = OpCount(mul=238 * 318 * (1 + (9 * (1 + 1 + 1 + 1)) + 2),
                       add=238 * 318 * (1 + (9 * (1 + 5 + 1 + 1)) + 1))

    code = strip_comments(code)
    parsed = pycparser.CParser().parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert expected == count_from_tree(oc_tree)
