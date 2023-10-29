import pycparser

from count_ops.lang_c import make_opcount_tree
from count_ops.common import print_tree, count_from_tree
from count_ops.parse import parse

code = """
 int main() {
        float input_image[240*320];
        float output_image[240*320];
        
        float kx[3*3]; //= {-1, 0, 1, -2, 0, 2, -1, 0, 1};
        float ky[3*3]; // = {-1, -2, -1, 0, 0, 0, 1, 2, 1};
    
        for (int i = 1; i < 239; i++) {
            for (int j = 1; j < 319; j++) {
                int idx = i * 320 + j;
                float x_val = 0.f;
                float y_val = 0.f;
                for (int ki = 0; ki < 3; ki++) {
                    for (int kj = 0; kj < 3; kj++) {
                        int kidx = ki * 3 + kj;
                        int idx2 = (i + ki - 1) * 320 + (j + kj - 1);
                        x_val += input_image[idx2] * kx[kidx];
                        y_val += input_image[idx2] * ky[kidx];
                    
                    }   
                }
                output_image[idx] = sqrt(x_val * x_val + y_val * y_val);
            }
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
    parsed = parse(code)

    # print(parsed)
    oc_tree = make_opcount_tree(parsed)
    print_tree(oc_tree)
    print(count_from_tree(oc_tree))


if __name__ == "__main__":
    main()
