//
// Created by mohammad on 5/20/23.
//
#include <iostream>
#include "common.h"
#include "movingFilter.h"

////inline float myrand() { return (float)std::rand() / (RAND_MAX); }
//inline float myrand() { return float(std::rand() % 20); }

int main() {

    std::vector<float> data  {7, 5, 13, 114, 16, 17, 18, 23, 21, 22, 26, 25, 21, 25, 21, 26, 25, 20, 22, 12, 15, 8, 9,
                              3, 2, 3, -2, -6, -7, -8, -9, -13, -10, -14, -14, -16, -12, -14, -18, -12, -9, -11, -7,
                              -10, -6, -5, -3, 3, 3, 9, 8, 5, 11, 18, 16, 14, 18, 17, 28, 29, 28, 26, 27, 21, 22, 24,
                              20, 16, 23, 16, 15, 11, 7, 6, 9, 5, -1, -7, -2, -9, -8, -15, -10, -15, -15, -15, -16, -14,
                              -10, -18, -15, -16, -8, -7, -9, -5, -1, 2, 99, 8, 10, 6, 16, 17, 19, 19, 18, 26, 24, 23,
                              22, 29, 24, 25, 26, 27, 23, 17, 19, 16, 15, 14, 7, 4, 2, 100, -4, -1, -7, -10, -13, -13,
                              -14, -16, -15, -14, -11, -10, -19, -17, -12, -15, -7, -11, -4, -3, 0, -4, 0, 7, 3, 5, 11,
                              15, 12, 14, 116, 20, 25, 21, 28, 24, 26, 22, 26, 28, 21, 18, 18, 16, 15, 13, 5, 4, 5, 5,
                              3, 0, -4, -2, -10, -11, -9, -10, -15, -11, -15, -12, -19, -19, -9, -15, -9, -11, -9, -6,
                              2, 101, 7, 7};

    show(data);
    std::vector<float> filtData(data.size());
    const uint32_t halfWindowSize = 2;
    tic;
    filt::movingFilter(filtData, data, halfWindowSize, filt::kernel::median);
    toc;

    show(filtData);
    printf("\ngood bye :)\n");
    return 0;

}
